from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from datetime import timedelta
from django.db import connection
import settings
from twitter_feels.libs.twitter_analysis import TweetTimeFrame
from twitter_stream.models import Tweet

import re


class TreeNode(models.Model):
    class Meta:
        index_together = [
            ['parent', 'word']
        ]

    parent = models.ForeignKey('self', null=True, blank=True, related_name='children')
    word = models.CharField(max_length=150)

    def get_child(self, word):
        child = list(self.children.filter(word=word)[:1])
        if child:
            return child[0]
        return None

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
        );
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
    node = models.ForeignKey(TreeNode)
    tweet = models.ForeignKey(Tweet)
    created_at = models.DateTimeField(db_index=True)
    tz_country = models.CharField(max_length=32, blank=True)

    @classmethod
    def delete_before(cls, oldest_date, batch_size=10000):
        """Delete a batch of chunks before the given date"""

        cursor = connection.cursor()

        deleted = cursor.execute("DELETE FROM map_tweetchunk WHERE created_at <= %s ORDER BY created_at LIMIT %s", [oldest_date, batch_size])

        return deleted

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
            node, created = TreeNode.objects.get_or_create(parent=parent, word=word)

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

                node, created = self.get_tree_node(parent=parent, word=chunk, cache=node_cache)

                country = user_tz_map.get(tweet.user_time_zone, None)
                if country is None:
                    country = ''
                else:
                    country = country.country
                new_tweet_chunks.append(TweetChunk(
                    node=node,
                    tweet=tweet,
                    created_at=tweet.created_at,
                    tz_country=country))
                parent = node
                depth += 1

        TweetChunk.objects.bulk_create(new_tweet_chunks)

        self.chunks_added += len(new_tweet_chunks)
        self.node_cache_size = len(node_cache)

        return tweets

    @classmethod
    def get_most_recent(cls, limit=20):
        """
        A handy static method to get the <limit>
        most recent frames.
        """

        query = cls.get_in_range(calculated=True) \
            .order_by('-start_time')

        return query[:limit]
