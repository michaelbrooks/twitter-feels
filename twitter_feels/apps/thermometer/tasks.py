# For tasks that can be run as background jobs.
from collections import defaultdict
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from models import TimeFrame, FeelingIndicator, FeelingWord
from twitter_feels.libs.streamer.models import Tweet
from datetime import timedelta
import django_rq
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


def create_tasks():
    """
    Determines what aggregation buckets need to be calculated.

    First, it checks the time on the newest tweet and the newest frame.
    If there is room for new frames, it adds these.

    Then it searches backwards, looking if there are
    tweets before the earliest frame.
    """

    if Tweet.objects.count() == 0:
        logger.info("No tweets to analyze")
        return

    duration = settings.TIME_FRAME_DURATION

    new_time_frames = []

    # Get the most recent global time frame.
    # We'll start analyzing after this.
    try:
        latest_analyzed = TimeFrame.get_latest().end_time
    except ObjectDoesNotExist:
        try:
            # There are no frames, so we will start with the first tweet.
            latest_analyzed = Tweet.objects.earliest(field_name='created_at').created_at
            latest_analyzed = latest_analyzed.replace(second=0, microsecond=0)  # chop off the small bits
        except ObjectDoesNotExist:
            logger.info("No tweets to analyze")
            return

    # Get the latest tweet. We'll stop analyzing here.
    try:
        latest_allowable_start = Tweet.objects.latest(field_name='created_at').created_at
        # but the frame can stop no later than this time so subtract the duration of the frame
        latest_allowable_start -= duration
    except ObjectDoesNotExist:
        logger.info("No tweets to analyze")
        return

    # Add any time frames that fit between the most recent time frame and now
    frame_start = latest_analyzed

    if frame_start < latest_allowable_start:
        logger.info("Analyzing from %s to %s", frame_start, latest_allowable_start)
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

    # Get the oldest tweet
    # We'll start analysis here
    try:
        earliest_allowable_start = Tweet.objects.earliest(field_name='created_at').created_at - duration
    except ObjectDoesNotExist:
        logger.info("No tweets to analyze")
        return

    # Get the oldest time frame
    # We'll stop analysis here
    try:
        earliest = TimeFrame.get_earliest().start_time
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
    indicators = FeelingIndicator.objects.filter(enabled=True)
    feelings = FeelingWord.get_tracked_list()
    feelings_set = set(f.word for f in feelings)

    # Create a dict for holding the counts -- these will be initialized to 0 as needed
    # Index into this with feeling words
    # For example: tweet_counts_by_feeling['fine'] += 1
    tweet_counts_by_feeling = defaultdict(float)

    # Go through all the tweets in the interval
    tweets = Tweet.get_created_in_range(globalframe.start_time, globalframe.end_time)\
        .filter(retweeted_status_id=None)\
        .order_by('created_at')

    # The number of tweets that matched an indicator but did NOT contain a recognized feeling.
    indicator_matches = 0
    largest_gap = timedelta(seconds=0)
    last_tweet_time = None
    for tweet in tweets:

        # Detecting gaps in the data
        if last_tweet_time:
            gap = tweet.created_at - last_tweet_time
            if gap > largest_gap:
                largest_gap = gap

        last_tweet_time = tweet.created_at

        # find out if an indicator matches
        for indicator in indicators:

            try:
                indicator_phrase, feeling_word = indicator.extract_feeling(tweet.text, feelings_set)

                if feeling_word:
                    # we have a valid feeling for this indicator
                    tweet_counts_by_feeling[feeling_word] += 1
                    indicator_matches += 1

                    break  # only one indicator per tweet, please

                elif indicator_phrase:

                    # we have a match on the indicator but no detectable feeling
                    indicator_matches += 1

            except Exception as e:
                logger.error("Error parsing tweet: %s", e.message)

    # If more than 20% of the frame was a gap, then consider it incomplete
    incomplete = len(tweets) == 0 or largest_gap.total_seconds() > globalframe.duration_seconds * 0.2

    # Create a bunch of new data frames
    all_new_frames = []

    for feeling in feelings:
        if indicator_matches > 0:
            percent = tweet_counts_by_feeling[feeling.word] / indicator_matches
        else:
            percent = 0

        all_new_frames.append(globalframe.create_subframe(
            feeling=feeling,
            tweets=percent,
            calculated=True,
            incomplete=incomplete
        ))

    # Save all the new frames
    TimeFrame.objects.bulk_create(all_new_frames)

    # This global frame is now done
    globalframe.tweets = indicator_matches
    globalframe.calculated = True
    globalframe.incomplete = incomplete
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
        .filter(word=None, calculated=True)

    # Delete the tweets in each of these frames
    tweets_cleaned = 0
    frames_cleaned = 0
    for frame in frames:
        tweets = Tweet.get_created_in_range(frame.start_time, frame.end_time)
        if len(tweets):
            tweets_cleaned += len(tweets)
            frames_cleaned += 1
            tweets.delete()

    logger.info("Cleaned %d tweets for %d frames.", tweets_cleaned, frames_cleaned)
