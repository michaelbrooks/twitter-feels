from django.db import models
from twitter_feels.libs.analysis import BaseTimeFrame
from datetime import timedelta


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
    DURATION = timedelta(seconds=15)

    # Simply store the total tweet count in this time frame
    tweet_count = models.IntegerField(default=0)

    def calculate(self, tweets):
        self.tweet_count = len(tweets)
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
