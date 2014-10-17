from django.core.exceptions import ObjectDoesNotExist
from django.db import models, connection, transaction, IntegrityError, DatabaseError
from django.utils import timezone
import random
from south.db.generic import DatabaseOperations

from twitter_stream.fields import PositiveBigAutoField, PositiveBigAutoForeignKey

from swapper import get_model_name
from datetime import timedelta
import settings
from twitter_feels.libs.twitter_analysis import TweetTimeFrame

import logging
import re

logger = logging.getLogger('map')

class TreeNode(models.Model):
    class Meta:
        index_together = [
            ['parent', 'word'],
            ['created_at', 'parent'],
        ]

    ROOT_NODES = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    parent = models.ForeignKey('self', null=True, blank=True, related_name='children')
    word = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True, default=None, null=True, blank=True)

    def get_child(self, word):
        child = list(self.children.filter(word=word)[:1])
        if child:
            return child[0]
        return None

    @classmethod
    def get_empty_nodes(cls):
        """
        Return a queryset for all the tree nodes that have no associated
        TweetChunks
        """
        return cls.objects.filter(chunks=None).exclude(pk__in=cls.ROOT_NODES)

    @classmethod
    def follow_chunks(cls, prefix, query_chunks):
        """Returns the node referenced by the given prefix and chunks."""
        root = cls.get_root()
        if not root:
            raise Exception("No root node in tweet tree")

        prefix_node = root.get_child(prefix)
        if prefix_node is None:
            return None

        node = prefix_node
        for chunk in query_chunks:
            node = node.get_child(chunk.lower())
            if not node:
                return None

        return node

    @classmethod
    def orphan_empty_nodes(cls, batch_size=10000):

        most_recent_time = cls.objects.aggregate(most_recent_time=models.Max('created_at'))
        if most_recent_time['most_recent_time'] is None:
            return 0

        most_recent_time = most_recent_time['most_recent_time']
        time_cutoff = most_recent_time - settings.NODE_FREEZE_INTERVAL

        subset_query = """
        SELECT map_treenode.id
          FROM map_treenode
          LEFT OUTER JOIN map_tweetchunk
            ON ( map_treenode.id = map_tweetchunk.node_id )
          WHERE (map_tweetchunk.id IS NULL)
            AND (map_treenode.parent_id IS NOT NULL)
            AND (map_treenode.created_at < %s)
            AND NOT (map_treenode.id IN %s)
          LIMIT %s
        """

        query = """
        UPDATE map_treenode
        JOIN (
          {subset_query}
        ) subset
          ON map_treenode.id = subset.id
        SET map_treenode.parent_id = NULL
        """.format(subset_query=subset_query)

        params = [time_cutoff, cls.ROOT_NODES, batch_size]

        cursor = connection.cursor()
        return cursor.execute(query, params)

    @classmethod
    def propagate_orphanage(cls):
        """Makes sure that all children of current orphans are also orphaned."""
        future_orphans = cls.objects.filter(parent__parent=None).exclude(parent=None)\
            .exclude(pk__in=cls.ROOT_NODES)

        return future_orphans.update(parent=None)

    @classmethod
    def delete_orphans(cls, batch_size=10000):
        """Delete a batch of orphans"""

        query = """
        DELETE FROM map_treenode
        WHERE (parent_id IS NULL)
          AND NOT (id IN %s)
        LIMIT %s
        """
        params = [cls.ROOT_NODES, batch_size]

        cursor = connection.cursor()
        return cursor.execute(query, params)

    @classmethod
    def cleanup(cls, batch_size=10000, reset=False):
        cls.cleanup_empty(batch_size=batch_size, reset=reset)
        cls.cleanup_orphans(batch_size=batch_size, reset=reset)
        

    @classmethod
    def cleanup_empty(cls, batch_size=10000, reset=False):
        # Disconnect TreeNodes without any chunks

        logger.info("Orphaning empty tree nodes...")

        batch_orphaned = cls.orphan_empty_nodes(batch_size=batch_size)
        total_orphaned = batch_orphaned
        while batch_orphaned == batch_size:
            logger.info("  ... orphaned batch of %d", batch_orphaned)
            batch_orphaned = cls.orphan_empty_nodes(batch_size=batch_size)
            total_orphaned += batch_orphaned

        if total_orphaned > 0:
            logger.info("Orphaned %d empty nodes", total_orphaned)
        else:
            logger.info("No empty nodes to orphan")

        logger.info("Orphaning children of orphans... (should not be needed)")
        propagated = cls.propagate_orphanage()
        while propagated > 0:
            logger.info("  ...orphaned %d new nodes (should be 0!)", propagated)
            propagated = cls.propagate_orphanage()


    @classmethod
    def cleanup_orphans(cls, batch_size=10000, reset=False):
        
        logger.info("Deleting orphans...")
        batch_deleted = cls.delete_orphans(batch_size=batch_size)
        total_deleted = batch_deleted
        while batch_deleted == batch_size:
            logger.info("  ... deleted batch of %d", batch_deleted)
            batch_deleted = cls.delete_orphans(batch_size=batch_size)
            total_deleted += batch_deleted

            if reset and settings.DEBUG:
                # Prevent apparent memory leaks
                # https://docs.djangoproject.com/en/dev/faq/models/#why-is-django-leaking-memory
                from django import db
                db.reset_queries()

        if total_deleted > 0:
            logger.info("Deleted %d orphans", total_deleted)
        else:
            logger.info("No orphans to delete")

    def get_top_chunk_countries_for_children(self, limit=10):
        """
        Look at the children of this node. Look at
        the chunks that refer to them.
        Return the top countries for those chunks by frequency.

        Returns a list.
        """

        # Group by tz_country
        query = TweetChunk.objects.values('tz_country')

        # Only non-empty tz_countries, words
        query = query.exclude(tz_country='')
        query = query.exclude(node__word='')

        # Only chunks belonging to our children
        query = query.filter(node__parent=self)

        # Order by count
        query = query.order_by('-chunk_count')

        # Aggregate fields
        query = query.annotate(chunk_count=models.Count('id'))

        # Limit
        query = query[:limit]

        print query.query

        return [r['tz_country'] for r in query]

    def get_most_popular_child_chunk_in(self, country):
        """
        Get the chunk following this node with the most tweets
        in the given country.
        """

        # Group by chunk
        query = TweetChunk.objects.values('node', 'node__word')

        # Only with the given country, non-empty words
        query = query.exclude(node__word='')
        query = query.filter(tz_country=country)

        # Only chunks belonging to our children
        query = query.filter(node__parent=self)

        # Order by count, desc
        query = query.order_by('-count')

        # Aggregate fields
        query = query.annotate(count=models.Count('id'))

        print query.query

        # Limit
        try:
            result = query.first()
            return result['node__word'], result['count']
        except ObjectDoesNotExist:
            return None


    def get_subquery(self):
        """
        Generates SQL like the following:

        SELECT
          `map_tweetchunk`.`tz_country`,
          `map_treenode`.`word`,
          COUNT(`map_tweetchunk`.`id`) AS `count`
        FROM `map_tweetchunk`
          INNER JOIN `map_treenode`
            ON (`map_tweetchunk`.`node_id` = `map_treenode`.`id`)
        WHERE (
          AND `map_treenode`.`parent_id` = MY_ID_GOES HERE
        )
        GROUP BY `map_tweetchunk`.`tz_country`, `map_treenode`.`word`
        """

        # Group by country, chunk
        query = TweetChunk.objects.values('tz_country', 'node__word')

        # Only with the given country, non-empty words
        # We'll do this later instead
        # query = query.exclude(node__word='')
        # query = query.exclude(tz_country='')

        # Only chunks belonging to our children
        query = query.filter(node__parent=self)

        # Aggregate fields
        query = query.annotate(count=models.Count('id'))

        return query

    def get_most_popular_child_chunk_by_country2(self, country_limit=10):
        """
        Get tuples of country, word, count for the top 10 countries
        following this node.

        More specifically:
            - Look at all the words that followed this one anywhere
            - In every country, find the word following this one that was most commonly used
            - For the top result from each country, return the top 10 country-word-counts.
        """

        # How much padding to add to counts for the concat/max/split trick
        count_padding = 10

        # Get the name of the stupid index from South
        db = DatabaseOperations(None)
        index_name = db.create_index_name('map_tweetchunk', ['tz_country', 'node_id'])

        # Find the words following this node for every
        # country, and the number of tweets with that word.

        # Concatenate the tweet count to the word
        subquery = """
        SELECT map_tweetchunk.tz_country,
           CONCAT(
              LPAD(COUNT(DISTINCT map_tweetchunk.id), {padding}, '0'),
              '-',
              map_treenode.word
           ) as combo
        FROM map_tweetchunk
        -- USE INDEX ({index_name})
        LEFT OUTER JOIN map_treenode
        ON ( map_tweetchunk.node_id = map_treenode.id )
        WHERE map_treenode.parent_id = %s
            AND map_tweetchunk.tz_country != ''
            AND map_treenode.word != ''
        GROUP BY map_tweetchunk.tz_country, map_tweetchunk.node_id
        """.format(padding=count_padding, index_name=index_name)

        # Now select the max of the combo field for each country
        # Since we've padded with 0s, alphabetic max is the same as numeric max
        maxquery = """
        SELECT sub.tz_country,
               MAX(sub.combo) as maxcombo
        FROM ({subquery}) sub
        GROUP BY sub.tz_country
        ORDER BY maxcombo DESC
        LIMIT %s
        """.format(subquery=subquery)

        # Now split up the max combo into the count and the word
        # The word is substring(maxcombo, padding+2) because
        # it is 1-indexed and we added a '-' character in the middle.
        splitquery = """
        SELECT sub2.tz_country,
               SUBSTRING(sub2.maxcombo, {padding} + 2) AS word,
               CAST(SUBSTRING(sub2.maxcombo, 1, {padding}) AS UNSIGNED) AS `count`
        FROM ({maxquery}) sub2
        """.format(maxquery=maxquery, padding=count_padding)

        print splitquery

        cursor = connection.cursor()
        cursor.execute(splitquery, [self.id, country_limit])

        return cursor.fetchall()


    def get_most_popular_child_chunk_by_country(self, country_limit=10):
        """
        Get tuples of country, word, count for the top 10 countries
        following this node.

        More specifically:
            - Look at all the words that followed this one anywhere
            - In every country, find the word following this one that was most commonly used
            - For the top result from each country, return the top 10 country-word-counts.
        """

        # Make sure this is valid
        country_limit = int(country_limit)

        subquery = self.get_subquery()

        # This query finds the maximum number of tweets
        # with chunks following this node for every country
        # up to the limit (plus 1 to allow for the empty country)
        maxquery = """
        SELECT
            sub.tz_country,
            MAX(sub.count) AS max_count
        FROM ({subquery}) sub
        GROUP BY tz_country
        ORDER BY max_count DESC
        LIMIT {limit}
        """.format(subquery=subquery.query, limit=country_limit + 1)

        # Template for the overall query
        # It finds the actual chunk for each country
        # that had the maximum count.
        # Further, filters out empty words and countries.
        superquery = """
        SELECT
            country_node_count.tz_country,
            country_node_count.word,
            country_node_count.count
        FROM
            ({subquery}) country_node_count
        INNER JOIN ({maxquery}) countrymax
            ON (countrymax.tz_country = country_node_count.tz_country)
        WHERE (
            country_node_count.count = countrymax.max_count
            AND country_node_count.tz_country != ''
            AND country_node_count.word != ''
        )
        ORDER BY country_node_count.count DESC
        LIMIT {limit}
        """.format(subquery=subquery.query, maxquery=maxquery, limit=country_limit)

        print superquery
        cursor = connection.cursor()
        cursor.execute(superquery)

        return cursor.fetchall()


    @classmethod
    def get_root(cls):
        try:
            return cls.objects.get(id=1)
        except ObjectDoesNotExist:
            return None


class Tz_Country(models.Model):
    user_time_zone = models.CharField(max_length=32)
    country = models.CharField(max_length=32)


class TweetChunk(models.Model):

    class Meta:
        index_together = [
            ['tz_country', 'node'],
        ]

    id = PositiveBigAutoField(primary_key=True)

    node = models.ForeignKey(TreeNode, related_name='chunks')

    twitter_id = models.BigIntegerField(default=0)
    tweet_text = models.CharField(max_length=250, default=None, null=True)

    created_at = models.DateTimeField(db_index=True)
    tz_country = models.CharField(max_length=32, blank=True)

    @classmethod
    def get_example_tweet(cls, country_name, node):
        """Returns a Tweet for the given country and node."""
        try:
            chunks = cls.objects.filter(tz_country=country_name, node=node)
            count = chunks.count()
            chunk = chunks[random.randint(0, count - 1)]
            return chunk.tweet_text
        except DatabaseError:
            # things could potentially disappear while we're doing these operations
            return None

    @classmethod
    def delete_before(cls, oldest_date, batch_size=10000):
        """Delete a batch of chunks before the given date"""

        cursor = connection.cursor()

        deleted = cursor.execute("DELETE FROM map_tweetchunk WHERE created_at <= %s ORDER BY created_at LIMIT %s", [oldest_date, batch_size])

        return deleted

    @classmethod
    def get_earliest_created_at(cls):
        """Get the earliest created_at in any tweet chunk."""
        results = cls.objects.aggregate(earliest_created_at=models.Min('created_at'))
        return results['earliest_created_at']

    @classmethod
    def cleanup(cls, batch_size=10000, reset=False):

        # Get the most recently finished map time frame
        now = MapTimeFrame.objects \
            .filter(calculated=True) \
            .aggregate(latest_start_time=models.Max('start_time'))

        # maybe there aren't any?
        if now['latest_start_time'] is None:
            return

        # Preserve some time prior to that time frame
        trailing_edge_date = now['latest_start_time'] - settings.KEEP_DATA_FOR

        logger.info("Cleaning chunks from before %s...", trailing_edge_date)

        batch_deleted = TweetChunk.delete_before(trailing_edge_date, batch_size=batch_size)
        total_deleted = batch_deleted
        while batch_deleted == batch_size:
            logger.info("  ... deleted batch of %d", batch_deleted)
            batch_deleted = TweetChunk.delete_before(trailing_edge_date, batch_size=batch_size)
            total_deleted += batch_deleted

            if reset and settings.DEBUG:
                # Prevent apparent memory leaks
                # https://docs.djangoproject.com/en/dev/faq/models/#why-is-django-leaking-memory
                from django import db
                db.reset_queries()

        if total_deleted > 0:
            logger.info("Deleted %d tweet chunks", total_deleted)
        else:
            logger.info("No chunks to delete")


class MapTimeFrame(TweetTimeFrame):
    """
    A basic time frame for demo analysis.

    1. Extend the BaseTimeFrame class.
    2. Indicate how often to run the analysis (same as the time frame duration)
    3. Add any fields you need to calculate. You can also store data on separate models,
       if your data is not strictly 1:1 with time frames.
    4. Implement calculate(tweets). This is where you do your work.
       At the end, make sure to call self.mark_done(tweets)
    5. Add any additional functions related to your time frames
       that will make them easier to work with.
    """

    # Analyze every 15 seconds
    DURATION = timedelta(seconds=60)

    # Simply store the total tweet count in this time frame
    tweet_count = models.IntegerField(default=0)
    nodes_added = models.IntegerField(default=0)
    chunks_added = models.IntegerField(default=0)
    node_cache_hits = models.IntegerField(default=0)
    node_cache_size = models.IntegerField(default=0)

    def check_prefix(self, tweet, roots):
        """Returns a root in the tweet, if it exists"""
        for root in roots:
            if root.word in tweet.text:
                return root

        return None

    def get_tree_node(self, parent, word, cache=None):
        """
        Returns a tree node for the parent and word, and whether or not it is new.
        A dictionary can optionally be provided for caching values across calls.
        """
        if cache is not None and (parent, word) in cache:
            self.node_cache_hits += 1
            return cache[(parent, word)], False
        else:
            # We want to keep trying to grab this node until we get one
            while True:
                try:
                    with transaction.atomic():
                        # Get or create a node with parent and word
                        node, created = TreeNode.objects.get_or_create(parent=parent, word=word)

                        if not created:
                            # If it is an old node, there is a risk that the cleanup
                            # procedure will delete it while we are working with it.
                            # Setting created_at makes it impossible for it to be deleted for a brief period.
                            node.created_at = timezone.now()
                            node.save()

                except IntegrityError:
                    # it was deleted while we were getting it
                    continue

                # we got one
                if cache is not None:
                    cache[(parent, word)] = node

                if created:
                    self.nodes_added += 1

                return node, created

    def calculate(self, tweets):
        self.tweet_count = len(tweets)

        tzcountries = Tz_Country.objects.all()
        roots = TreeNode.objects.filter(parent=1)
        user_tz_map = dict((r.user_time_zone, r) for r in tzcountries)
        user_tz_map[None] = None

        node_cache = {}
        new_tweet_chunks = []
        for tweet in tweets:
            root = self.check_prefix(tweet, roots)
            if not root:
                continue
            rh = tweet.text.split(root.word, 1)[1]
            rh = rh.lower()
            chunks = re.split('[*,.!:"\s;()/@#]+|\'[\W]|\?+', rh)
            parent = root
            depth = 0

            for chunk in chunks:
                if chunk == "":
                    continue
                if depth > settings.MAX_DEPTH:
                    break

                # This node is guaranteed safe to work with for a few minutes
                # It won't be deleted by cleanup before we create its TweetChunk.
                node, created = self.get_tree_node(parent=parent, word=chunk, cache=node_cache)

                country = user_tz_map.get(tweet.user_time_zone, None)
                if country is None:
                    country = ''
                else:
                    country = country.country

                new_tweet_chunks.append(TweetChunk(
                    node=node,
                    twitter_id=tweet.tweet_id,
                    tweet_text=tweet.text,
                    created_at=tweet.created_at,
                    tz_country=country))
                parent = node
                depth += 1

        TweetChunk.objects.bulk_create(new_tweet_chunks)

        self.chunks_added += len(new_tweet_chunks)
        self.node_cache_size = len(node_cache)

        return tweets

    def cleanup(self):
        
        if self.id % 3 == 0:
            # Then remove obsolete tree nodes
            TreeNode.cleanup_empty()
        else:
            logger.info("Skipping empty treenode cleanup on this frame")

            # First delete old tweet chunks
            TweetChunk.cleanup()
            TreeNode.cleanup_orphans()
            

    @classmethod
    def get_stream_memory_cutoff(cls):
        """Need to override this because we have tons of data that depends on tweets."""

        baseline_cutoff = super(TweetTimeFrame, cls).get_stream_memory_cutoff()

        # Get the earliest tweet referenced in any Tweet Chunk
        earliest_created_at = TweetChunk.get_earliest_created_at()

        if earliest_created_at is not None:
            return min(earliest_created_at, baseline_cutoff)
        else:
            return baseline_cutoff

    @classmethod
    def get_most_recent(cls, limit=20):
        """
        A handy static method to get the <limit>
        most recent frames.
        """

        query = cls.get_in_range(calculated=True) \
            .order_by('-start_time')

        return query[:limit]
