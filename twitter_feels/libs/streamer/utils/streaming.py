__all__ = ['FeelsTermChecker', 'QueueStreamListener']

import Queue
import logging
import time
import twitter_monitor
from .. import models
import tweet_queue

logger = logging.getLogger('streamer')


class FeelsTermChecker(twitter_monitor.TermChecker):
    """
    Checks the database for filter terms.

    Note that because this is run every now and then, and
    so as not to block the streaming thread, this
    object will actually also insert the tweets into the database.
    """

    def __init__(self, queue_listener, stream_process, scheduler=None):
        super(FeelsTermChecker, self).__init__()

        # A queue for tweets that need to be written to the database
        self.listener = queue_listener
        self.error_count = 0
        self.process = stream_process
        # If provided, will periodically enqueue scheduled tasks
        self.scheduler = scheduler

    def update_tracking_terms(self):

        # Process the tweet queue -- this is more important
        # to do regularly than updating the tracking terms
        # Update the process status in the database
        self.process.tweet_rate = self.listener.process_tweet_queue()
        self.process.error_count = self.error_count

        # Check for scheduled jobs
        if self.scheduler:
            self.scheduler.enqueue_jobs()

        # Check for new tracking terms
        filter_terms = models.FilterTerm.objects.filter(enabled=True)

        if len(filter_terms):
            self.process.status = models.StreamProcess.STREAM_STATUS_RUNNING
        else:
            self.process.status = models.StreamProcess.STREAM_STATUS_WAITING

        self.process.heartbeat()

        return set([t.term for t in filter_terms])

    def ok(self):
        return self.error_count < 5

    def error(self, exc):
        logger.error(exc)
        self.error_count += 1


class QueueStreamListener(twitter_monitor.JsonStreamListener):
    """
    Saves tweets in a queue for later insertion into database
    when process_tweet_batch() is called.

    Note that this is operated by the streaming thread.
    """

    def __init__(self, api=None):
        super(QueueStreamListener, self).__init__(api)

        # A place to put the tweets
        self.queue = tweet_queue.TweetQueue()

        # For calculating tweets / sec
        self.time = time.time()

    def on_status(self, status):
        # construct a Tweet object from the raw status object.
        self.queue.put_nowait(status)

    def process_tweet_queue(self):
        """
        Inserts any queued tweets into the database.

        It is ok for this to be called on a thread other than the streaming thread.
        """

        # this is for calculating the tps rate
        now = time.time()
        diff = now - self.time
        self.time = now

        try:
            batch = self.queue.get_all_nowait()
        except Queue.Empty:
            return 0

        if len(batch) == 0:
            return 0

        # we will ignore the possible embedded original tweet (e.g. this is a retweet)
        tweets = [models.Tweet.create_from_json(status) for status in batch]
        models.Tweet.objects.bulk_create(tweets)

        logger.info("Inserted %s tweets at %s tps" % (len(batch), len(batch) / diff))
        return len(batch) / diff
