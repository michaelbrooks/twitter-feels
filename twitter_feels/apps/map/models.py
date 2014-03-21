from django.db import models

from datetime import timedelta
import settings
from twitter_feels.libs.twitter_analysis import TweetTimeFrame
from twitter_stream.models import Tweet

import re


class TreeNode(models.Model):
    class Meta:
        index_together = [
            ['parent', 'word']
        ]

    parent = models.ForeignKey('self', null=True, blank=True)
    word = models.CharField(max_length=150)


class Tz_Country(models.Model):
    user_time_zone = models.CharField(max_length=32)
    country = models.CharField(max_length=32)


class TweetChunk(models.Model):
    node = models.ForeignKey(TreeNode)
    tweet = models.ForeignKey(Tweet)
    created_at = models.DateTimeField()
    tz_country = models.CharField(max_length=32, null=True, blank=True)


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
            return cache[(parent, word)], False
        else:
            node, created = TreeNode.objects.get_or_create(parent=parent, word=word)
            if cache is not None:
                cache[(parent, word)] = node
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
