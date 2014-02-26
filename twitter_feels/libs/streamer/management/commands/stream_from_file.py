import logging
from optparse import make_option
from logging.config import dictConfig
import threading
import time

from django.core.management.base import BaseCommand
import signal

from ... import models
from ...utils import streaming, tweet_processor

# Setup logging if not already configured
logger = logging.getLogger('streamer')
if not logger.handlers:
    dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            "streamer": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
            },
        },
        "streamer": {
            "handlers": ["streamer"],
            "level": "DEBUG"
        }
    })


class FakeTwitterStream(tweet_processor.TweetProcessor):
    """
    A tweet processor with a similar interface to the
    DynamicTweetStream class. It launches the tweet file
    reading in a separate thread.
    """
    def __init__(self, tweets_file, listener, term_checker,
                 limit=None, rate_limit=None):
        super(FakeTwitterStream, self).__init__(tweets_file, limit=limit, rate_limit=rate_limit)

        self.listener = listener
        self.term_checker = term_checker

        self.tracking_terms = []
        self.polling = False
        self.stream = None
        self.last_created_at = 0

        self.polling_interrupt = threading.Event()

    def process(self, tweet, raw_tweet):
        self.listener.on_status(tweet)
        self.last_created_at = tweet['created_at']

    def start(self, interval):
        """
        Start polling for term updates and streaming.
        """

        self.polling = True

        # clear the stored list of terms - we aren't tracking any
        self.term_checker.reset()

        logger.info("Starting polling for changes to the track list")
        while self.polling:
            if self.last_created_at:
                logger.info('Inserted tweets up to %s', str(self.last_created_at))

            # Check if the tracking list has changed
            if self.term_checker.check():
                # There were changes to the term list -- restart the stream
                self.tracking_terms = self.term_checker.tracking_terms()
                self.update_stream()

            # check to see if an exception was raised in the streaming thread
            if self.listener.streaming_exception is not None:
                # propagate outward
                raise self.listener.streaming_exception

            # wait for the interval unless interrupted
            try:
                self.polling_interrupt.wait(interval)
            except KeyboardInterrupt as e:
                logger.info("Polling canceled by user")
                raise e

        logger.info("Term poll ceased!")

    def update_stream(self):
        if not self.stream:
            self.stream = threading.Thread(target=self.run)
            self.stream.start()
        else:
            logger.warn("Cannot restart fake twitter streams!")


class Command(BaseCommand):
    """
    Streams tweets from an existing file. The file should
    be pretty-printed JSON dump from the streaming API.

    Example usage:
    python manage.py stream_from_file tweets.json
    python manage.py stream_from_file tweets.json --limit 100000
    python manage.py stream_from_file tweets.json --rate-limit 25 --poll-interval 25
    """

    option_list = BaseCommand.option_list + (
        make_option(
            '--poll-interval',
            action='store',
            dest='poll_interval',
            default=10,
            type=int,
            help='Seconds between tweet inserts.'
        ),
        make_option(
            '--rate-limit',
            action='store',
            dest='rate_limit',
            default=None,
            type=float,
            help='Rate to read in tweets.'
        ),
        make_option(
            '--limit',
            action='store',
            dest='limit',
            default=None,
            type=int,
            help='Limit the number of tweets read.'
        )
    )
    args = '<tweets_file>'
    help = "Fakes a streaming connection to twitter by reading from a file."

    def handle(self, tweets_file=None, *args, **options):

        # The suggested time between hearbeats
        poll_interval = options.get('poll_interval', 10)
        rate_limit = options.get('rate_limit', 50)
        limit = options.get('limit', None)

        # First expire any old stream process records that have failed
        # to report in for a while
        timeout_seconds = 3 * poll_interval
        models.StreamProcess.expire_timed_out()

        stream_process = models.StreamProcess.create(
            timeout_seconds=3 * poll_interval
        )

        def stop(signum, frame):
            """
            Register scheduler's death and exit.
            """
            logger.debug("Stopping because of signal")

            if stream_process:
                stream_process.status = models.StreamProcess.STREAM_STATUS_STOPPED
                stream_process.heartbeat()

            raise SystemExit()

        def install_signal_handlers():
            """
            Installs signal handlers for handling SIGINT and SIGTERM
            gracefully.
            """

            signal.signal(signal.SIGINT, stop)
            signal.signal(signal.SIGTERM, stop)

        install_signal_handlers()

        try:

            logger.info("Streaming from %s", tweets_file)
            if rate_limit:
                logger.info("Rate limit: %f", rate_limit)

            listener = streaming.QueueStreamListener()
            checker = streaming.FeelsTermChecker(queue_listener=listener,
                                                 stream_process=stream_process)

            while checker.ok():
                try:
                    # Start and maintain the streaming connection...
                    stream = FakeTwitterStream(tweets_file,
                                               limit=limit, rate_limit=rate_limit,
                                               listener=listener, term_checker=checker)

                    stream.start(poll_interval)
                except Exception as e:
                    checker.error(e)
                    time.sleep(1)  # to avoid craziness

            logger.error("Stopping because term checker not ok")
            stream_process.status = models.StreamProcess.STREAM_STATUS_STOPPED
            stream_process.heartbeat()

        except Exception as e:
            logger.error(e)

        finally:
            stop(None, None)
