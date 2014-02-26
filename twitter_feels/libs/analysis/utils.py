"""
Defines the Analysis task and
functions for executing scheduled analysis work
based on the settings in ANALYSIS_TIME_FRAME_TASKS.
"""

import datetime
from django.utils import importlib
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
import models
import settings
import django_rq
import logging
from logging.config import dictConfig
import re
from twitter_feels.libs.streamer.models import Tweet

logger = logging.getLogger('analysis')
if not logger.handlers:
    dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            "analysis": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
            },
        },
        "analysis": {
            "handlers": ["analysis"],
            "level": "DEBUG"
        }
    })

scheduler = django_rq.get_scheduler()


def _import_attribute(name):
    """Return an attribute from a dotted path name (e.g. "path.to.func")."""
    module_name, attribute = name.rsplit('.', 1)
    module = importlib.import_module(module_name)
    return getattr(module, attribute)


class AnalysisTask(object):
    """
    A class for representing, validating, and scheduling analysis tasks.
    """
    TASK_KEY_REGEX = re.compile('\w+')

    def __init__(self, key, taskdef):
        self.key = key
        self.name = taskdef['name']
        self.frame_class_path = taskdef['frame_class_path']
        self.frame_class = None

    def validate(self):
        """Verify the values from the settings file."""

        # The keys must be word-like
        if not AnalysisTask.TASK_KEY_REGEX.match(self.key):
            raise ImproperlyConfigured("Key %s in ANALYSIS_TIME_FRAME_TASKS is not word-like." % self.key)

        if not isinstance(self.name, basestring):
            raise ImproperlyConfigured("Name %s in ANALYSIS_TIME_FRAME_TASKS is not a string" % self.name)

        try:
            # Try locating the target class
            self.frame_class = _import_attribute(self.frame_class_path)
        except Exception:
            raise ImproperlyConfigured("Frame class path %s is not reachable" % self.frame_class_path)

        if not issubclass(self.frame_class, models.BaseTimeFrame):
            raise ImproperlyConfigured("Frame class %s does not extend BaseTimeFrame" % self.frame_class.__name__)

        # Make sure the time frame has a duration set properly
        if not isinstance(self.frame_class.DURATION, datetime.timedelta):
            raise ImproperlyConfigured("Frame class %s does not provide DURATION property" % self.frame_class.__name__)

    def get_rq_job(self):
        jobs = scheduler.get_jobs()
        for job in jobs:
            if job.meta.get('analysis.task.key') == self.key:
                return job

    def schedule(self, cancel_first=True):
        """
        Schedule this analysis task.
        """

        if cancel_first:
            # First cancel any old jobs
            self.cancel()

        # Use the analysis duration as the interval
        interval = self.frame_class.DURATION.total_seconds()

        now = datetime.datetime.now()

        job = scheduler.schedule(
            scheduled_time=now,
            interval=interval,
            func=create_frames,
            args=[self.key]
        )

        job.meta['analysis.task.key'] = self.key
        job.save()

        logger.info("Scheduled task '%s' every %d seconds", self.name, interval)

        return True

    def cancel(self):
        """
        Stop this task.
        """
        job = self.get_rq_job()

        if job:
            scheduler.cancel(job)
            job.delete()
            logger.info("Cancelled task '%s'", self.name)

            return True

        return False

    @classmethod
    def get(cls, key=None):
        if key:
            return _tasks_config[key]
        else:
            return _tasks_config.values()


_tasks_config = {}
# Load the tasks from settings
for key in settings.TIME_FRAME_TASKS:
    _tasks_config[key] = AnalysisTask(key, settings.TIME_FRAME_TASKS[key])
    _tasks_config[key].validate()


########################
# Functions for doing analysis
########################

def create_frames(task_key):
    """
    Creates any new time frames that are needed.
    Takes as input a task key from the ANALYSIS_TIME_FRAME_TASKS dict.

    First, it checks the time on the newest tweet and the newest frame.
    If there is room for new frames, it adds these.

    Then it searches backwards, looking if there are
    tweets before the earliest frame.
    If there is room, it adds these as well.

    For every new frame, a job is created to analyze it.
    """

    if Tweet.objects.count() == 0:
        logger.info("No tweets to analyze")
        return

    task = AnalysisTask.get(key=task_key)
    frame_class = task.frame_class
    duration = frame_class.DURATION

    logger.info("Creating frames for %s", task.name)

    new_time_frames = []

    # Get the most recent time frame.
    # We'll start analyzing after this.
    latest_analyzed = frame_class.get_latest_end_time()
    if latest_analyzed is None:
        # There are no frames, so we will start with the first tweet.
        latest_analyzed = Tweet.get_earliest_created_at()

        if latest_analyzed is None:
            logger.info("No tweets to analyze")
            return

        latest_analyzed = latest_analyzed.replace(second=0, microsecond=0)  # chop off the small bits

    # Get the latest tweet. We'll stop analyzing here.
    latest_allowable_start = Tweet.get_latest_created_at()
    if latest_allowable_start is None:
        logger.info("No tweets to analyze")
        return
    # but the frame can stop no later than this time so subtract the duration of the frame
    latest_allowable_start -= duration

    # Add any time frames that fit between the most recent time frame and now
    frame_start = latest_analyzed

    if frame_start < latest_allowable_start:
        logger.info("Analyzing from %s to %s", frame_start, latest_allowable_start)

    while frame_start < latest_allowable_start:
        # Create a new global (no word) time frame
        new_time_frames.append(frame_class(start_time=frame_start))
        frame_start += duration

    _insert_and_queue(task_key, new_time_frames)

    # Done looking forwards, now look backwards
    new_time_frames = []

    # Get the oldest tweet
    # We'll start analysis here
    earliest_allowable_start = Tweet.get_earliest_created_at() - duration
    if earliest_allowable_start is None:
        logger.info("No tweets to analyze")
        return

    # Get the oldest time frame
    # We'll stop analysis here
    try:
        earliest = frame_class.get_earliest_start_time()
    except ObjectDoesNotExist:
        logger.info("No backfilling necessary.")
        return

    # Add any time frames that fit between the oldest tweet and the oldest time frame
    frame_start = earliest - duration
    if frame_start > earliest_allowable_start:
        logger.info("Analyzing from %s to %s", earliest_allowable_start, frame_start)

    while frame_start > earliest_allowable_start:
        # go until we've overshot the tweet
        # Create a new global (no word) time frame
        new_time_frames.append(frame_class(start_time=frame_start))
        frame_start -= duration

    _insert_and_queue(task_key, new_time_frames)


def _insert_and_queue(task_key, time_frames):
    """
    Inserts the given TimeFrames into the database
    and creates a job to calculate each one.
    """
    for frame in time_frames:
        frame.save()
        analyze_frame.delay(task_key=task_key, frame_id=frame.pk)
    if time_frames:
        logger.info("Created %d time frames", len(time_frames))


@django_rq.job
def analyze_frame(task_key, frame_id):
    """
    Run the analysis for a frame as part of a task.
    """
    task = AnalysisTask.get(key=task_key)
    logger.info("Running analysis for %s", task.name)

    frame_class = task.frame_class

    frame = frame_class.objects.get(pk=frame_id)

    # Get the tweets for this time frame
    tweets = Tweet.get_created_in_range(frame.start_time, frame.end_time) \
        .filter(retweeted_status_id=None) \
        .order_by('created_at')

    frame.calculate(tweets)

    logger.info('Processed %d tweets for %s #%s', len(tweets), frame_class.__name__, str(frame_id))


@django_rq.job
def cleanup():
    """
    Removes any tweets which have already been analyzed by all tasks.
    """
    num_analyses = len(settings.TIME_FRAME_TASKS)
    deleted = Tweet.delete_analyzed(analyzed_by=num_analyses)
    logger.info("Cleaned %d tweets already covered by %d analyses.", deleted, num_analyses)

