from django.db import models

import stream_analysis
from twitter_stream.models import Tweet

class TweetStream(stream_analysis.AbstractStream):
    """Stream interface for Tweets"""

    def is_stream_empty(self):
        return Tweet.objects.count() == 0

    def get_earliest_stream_time(self):
        return Tweet.get_earliest_created_at()

    def get_latest_stream_time(self):
        return Tweet.get_latest_created_at()

    def get_stream_data(self, start, end):
        return Tweet.get_created_in_range(start, end) \
            .order_by('created_at')

    def delete_analyzed(self, num_analyses=None):
        analyzed = Tweet.objects.filter(analyzed_by__gte=num_analyses)
        count = len(analyzed)
        analyzed.delete()
        return count

    def count_analyzed(self, num_analyses=None):
        analyzed = Tweet.objects.filter(analyzed_by__gte=num_analyses)
        return len(analyzed)

    def mark_analyzed(self, stream_data, analysis_task):
        # Increase the analyzed_by count on the tweets
        stream_data.update(analyzed_by=models.F('analyzed_by') + 1)


class TweetTimeFrame(stream_analysis.BaseTimeFrame):
    """
    Extend this if you want to define a Time Frame for the tweet stream.
    """

    class Meta:
        abstract = True

    STREAM_CLASS = TweetStream
