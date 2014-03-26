from django.db import models, connection
import logging

import stream_analysis
from twitter_stream.models import Tweet

logger = logging.getLogger('twitter_analysis')

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

    def delete_tweet_batch(self, cutoff_datetime, batch_size=10000):
        query = """
        DELETE FROM twitter_stream_tweet
        WHERE created_at < %s
        LIMIT %s
        """
        params = [cutoff_datetime, batch_size]

        cursor = connection.cursor()
        return cursor.execute(query, params)

    def delete_before(self, cutoff_datetime):
        if cutoff_datetime is None:
            return 0

        logger.info("Deleting tweets before %s", cutoff_datetime)

        batch_size = 10000
        batch_deleted = self.delete_tweet_batch(cutoff_datetime, batch_size)
        total_deleted = batch_deleted
        while batch_deleted == batch_size:
            logger.info("  ... deleted %d tweets", batch_deleted)
            batch_deleted = self.delete_tweet_batch(cutoff_datetime, batch_size)
            total_deleted += batch_deleted

        if total_deleted > 0:
            logger.info("Deleted %d tweets", total_deleted)
        else:
            logger.info("No tweets to delete")

        return total_deleted

    def count_before(self, cutoff_datetime):
        if cutoff_datetime is None:
            return 0

        analyzed = Tweet.objects.filter(created_at__lt=cutoff_datetime)
        return analyzed.count()


class TweetTimeFrame(stream_analysis.BaseTimeFrame):
    """
    Extend this if you want to define a Time Frame for the tweet stream.
    """

    class Meta:
        abstract = True

    STREAM_CLASS = TweetStream
