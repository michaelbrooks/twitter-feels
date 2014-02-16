# For tasks that can be run as background jobs.
import django_rq
from django.core.exceptions import ObjectDoesNotExist
from datetime import timedelta, datetime
from django.utils import timezone
from models import TimeFrame, FeelingPrefix, FeelingWord
from twitter_feels.libs.streamer.models import Tweet
import settings

import logging

logger = logging.getLogger('thermometer')


def _insert_and_queue(time_frames):
    """
    Inserts the given TimeFrames into the database
    and creates a job to calculate each one.
    """
    for frame in time_frames:
        frame.save()
        aggregate.delay(frame_id=frame.pk)


def schedule_create_tasks():
    now = datetime.now()
    duration = settings.TIME_FRAME_DURATION

    scheduler = django_rq.get_scheduler()
    job = scheduler.schedule(
        scheduled_time=now,
        func=create_tasks,
        interval=duration.total_seconds(),
    )

    logger.info('Scheduled job %s', str(job.id))


def cancel_create_tasks():
    scheduler = django_rq.get_scheduler()
    jobs = scheduler.get_jobs()

    for job in jobs:
        scheduler.cancel(job)
        logger.info("Cancelled job %s", str(job.id))
    if not len(jobs):
        logger.info("No jobs to cancel")


def create_tasks():
    """
    Determines what aggregation buckets need to be calculated.

    First it searches forward, looking for new tweets that haven't been
    processed yet.

    Then it searches backwards, looking for old tweets that haven't
    been processed yet.
    """

    duration = settings.TIME_FRAME_DURATION

    new_time_frames = []

    # Get the most recent global time frame (no associated word)
    try:
        latest = TimeFrame.get_latest().end_time
    except ObjectDoesNotExist:
        try:
            latest = Tweet.objects.earliest(field_name='created_at').created_at
        except ObjectDoesNotExist:
            latest = timezone.now()

        latest = latest.replace(second=0, microsecond=0)  # chop off the small bits

    # Get the current time
    now = timezone.now()
    latest_allowable_start = now - duration

    # Add any time frames that fit between the most recent time frame and now
    frame_start = latest
    while frame_start < latest_allowable_start:
        # Create a new global (no word) time frame
        new_time_frames.append(TimeFrame.create_global(
            start_time=frame_start,
            time_delta=duration
        ))

        frame_start += duration

    _insert_and_queue(new_time_frames)
    logger.info("Created %d forward time frames", len(new_time_frames))

    # Done looking forwards, now look backwards
    new_time_frames = []

    if Tweet.objects.count():
        # Get the oldest tweet
        first_tweet = Tweet.objects.earliest(field_name='created_at')

        earliest_allowable_start = first_tweet.created_at - duration

        # Get the oldest time frame
        try:
            earliest = TimeFrame.get_earliest().start_time
        except ObjectDoesNotExist:
            earliest = timezone.now().replace(second=0)  # chop off the seconds portion

        # Add any time frames that fit between the oldest tweet and the oldest time frame
        frame_start = earliest - duration
        while frame_start > earliest_allowable_start:
            # go until we've overshot the tweet

            # Create a new global (no word) time frame
            new_time_frames.append(TimeFrame.create_global(
                start_time=frame_start,
                time_delta=duration
            ))

            frame_start -= duration

    _insert_and_queue(new_time_frames)
    logger.info("Created %d backward time frames", len(new_time_frames))


@django_rq.job
def aggregate(frame_id, cleanup_when_done=False):
    """
    Calculates a new time frame from collected Twitter data.
    """

    # Get the global (no word) frame that we are building off of
    globalframe = TimeFrame.objects.get(pk=frame_id)

    # Get all the words we are currently interested in tracking
    # words = FeelingWord.objects.filter(enabled=True)
    # prefixes = FeelingPrefix.objects.filter(enabled=True)
    #
    # # Create a ton of empty frames -- one for each word
    # all_new_frames = []
    # frames_by_word = {}
    # for word in words:
    #     frame = globalframe.create_subframe(word=word, tweet_count=0)
    #     all_new_frames.append(frame)
    #     frames_by_word[word.word] = frame
    #
    # # And... one for each prefix
    # frames_by_prefix = {}
    # # And one for each (prefix, word)
    # frames_by_word_by_prefix = {}
    # for prefix in prefixes:
    #     frame = globalframe.create_subframe(prefix=prefix, tweet_count=0)
    #     all_new_frames.append(frame)
    #     frames_by_prefix[prefix.prefix] = frame
    #
    #     frames_by_word_by_prefix[prefix.prefix] = {}
    #     for word in words:
    #         frame = globalframe.create_subframe(prefix=prefix, word=word, tweet_count=0)
    #         all_new_frames.append(frame)
    #         frames_by_word_by_prefix[prefix.prefix][word.word] = frame
    #
    # # Go through all the tweets in the interval
    tweets = Tweet.get_created_in_range(globalframe.start_time, globalframe.end_time)
    # for tweet in tweets:
    #
    #     # find out which prefix matches and get the next word
    #     for prefix in prefixes:
    #
    #         next_word = prefix.get_next_word(tweet.text)
    #         if next_word:
    #             next_word = next_word.lower()
    #
    #             # Update the frame for this prefix
    #             frames_by_prefix[prefix.prefix].tweet_count += 1
    #
    #             # Check if the following word is in our set
    #             if next_word in frames_by_word:
    #                 # update the frame for this word
    #                 frames_by_word[next_word].tweet_count += 1
    #
    #                 # update the frame for this (prefix, word)
    #                 frames_by_word_by_prefix[prefix.prefix][word.word].tweet_count += 1
    #
    # # Save all the new frames
    # TimeFrame.objects.bulk_create(all_new_frames)

    # This global frame is now done
    globalframe.tweet_count = len(tweets)
    globalframe.save()

    logger.info('Processed %d tweets for frame %s', len(tweets), str(frame_id))

    if cleanup_when_done:
        tweets.delete()
        logger.info("Tweets deleted")


@django_rq.job
def cleanup():
    """
    Removes any tweets for time frames that have already been aggregated.
    """

    # Get every global frame that has already been processed
    frames = TimeFrame.objects \
        .filter(word=None, tweet_count__isnull=False)

    # Delete the tweets in each of these frames
    for frame in frames:
        tweets = Tweet.get_created_in_range(frame.start_time, frame.end_time)
        tweets.delete()
