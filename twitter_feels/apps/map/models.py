from django.db import models
from twitter_feels.libs.analysis import BaseTimeFrame
from datetime import timedelta
from twitter_feels.libs.streamer.models import Tweet
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
    tz_country = models.ForeignKey(Tz_Country, null=True, blank=True)

class MapTimeFrame(BaseTimeFrame):
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

        for root in roots:
            if root.word in tweet.text:
                return root

        return None


    def calculate(self, tweets):
        self.tweet_count = len(tweets)
        tzcountries = Tz_Country.objects.all()
        roots = TreeNode.objects.filter(parent__isnull=True)
        
        user_tz_map = dict((r.user_time_zone, r) for r in tzcountries)
        user_tz_map[None] = None

        new_tweet_chunks = []

        for tweet in tweets:
            root = self.check_prefix(tweet, roots)
            if not root:
                continue
            rh = tweet.text.split(root.word, 1)[1]
            chunks = rh.split(' ')
            for chunk in chunks:
                node, created = TreeNode.objects.get_or_create(parent=root, word=chunk)
                new_tweet_chunks.append(TweetChunk(
                    node=node, 
                    tweet=tweet, 
                    created_at=tweet.created_at, 
                    tz_country=user_tz_map[tweet.user_time_zone]))

        TweetChunk.objects.bulk_create(new_tweet_chunks)

        self.mark_done(tweets)

    @classmethod
    def get_most_recent(cls, limit=20):
        """
        A handy static method to get the <limit>
        most recent frames.
        """

        query = cls.get_in_range(calculated=True) \
            .order_by('-start_time')

        return query[:limit]
