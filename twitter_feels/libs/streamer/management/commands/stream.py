import logging
from optparse import make_option
from logging.config import dictConfig
import time
from django.core.exceptions import ImproperlyConfigured

from django.core.management.base import BaseCommand
import signal
import tweepy
import twitter_monitor

from ... import models
from ...utils import streaming

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


try:
    from django_rq import get_scheduler
except ImportError:
    def get_scheduler(*args, **kwargs):
        raise ImproperlyConfigured('django_rq not installed')


class Command(BaseCommand):
    """
    Starts a process that streams data from Twitter.

    If --scheduler-queue is provided, manages scheduled
    RQ jobs on the given queue at the same rate as polling.

    Example usage:
    python manage.py stream
    python manage.py stream --poll-interval 25
    python manage.py stream --poll-interval 25 --scheduler-queue default
    """

    option_list = BaseCommand.option_list + (
        make_option(
            '--poll-interval',
            action='store',
            dest='poll_interval',
            default=10,
            help='Seconds between term updates and tweet inserts.'
        ),
        make_option(
            '--scheduler-queue',
            action='store',
            dest='scheduler_queue',
            default=None,
            help='Schedule RQ tasks on this queue.'
        )
    )
    args = '<credentials_name>'
    help = "Starts a streaming connection to Twitter, optionally schedules RQ jobs"

    def handle(self, credentials_name=None, *args, **options):

        # The suggested time between hearbeats
        poll_interval = options.get('poll_interval', 10)
        scheduler_queue = options.get('scheduler_queue', None)

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
            if scheduler:
                scheduler.register_death()

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
            credentials = models.TwitterAPICredentials.get_credentials(credentials_name)

            if scheduler_queue:
                scheduler = get_scheduler(name=scheduler_queue, interval=poll_interval)
                if not scheduler:
                    logger.error("Unable to initialize scheduler %s", scheduler_queue)
                else:
                    logger.info("Managing scheduled tasks on %s", scheduler_queue)
                    scheduler.register_birth()

            logger.info("Using credentials for %s", credentials.name)
            stream_process.credentials = credentials
            stream_process.save()

            auth = tweepy.OAuthHandler(credentials.api_key, credentials.api_secret)
            auth.set_access_token(credentials.access_token, credentials.access_token_secret)

            listener = streaming.QueueStreamListener()
            checker = streaming.FeelsTermChecker(queue_listener=listener,
                                       stream_process=stream_process,
                                       scheduler=scheduler)

            # Start and maintain the streaming connection...
            stream = twitter_monitor.DynamicTwitterStream(auth, listener, checker)

            while checker.ok():
                try:
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
