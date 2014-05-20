from collections import defaultdict
from datetime import timedelta
import random
import re
import logging

from django.db import models

import nltk
import times
import settings
from twitter_feels.libs.twitter_analysis import TweetTimeFrame
from stream_analysis import TimedIntervalMixin


logger = logging.getLogger('thermometer')


# Regex for matching indicators

INDICATOR_REG_TEMPLATE = (r"([^\w]|^)"   # something that is not wordy
                          r"%s"          # the term/phrase
                          r"([^\w]|$)")  # another non-wordy bit

# The number of match groups contained in the regex
INDICATOR_REG_GROUP_COUNT = 2


class FeelingIndicator(models.Model):
    """
    A feeling indicator such as "I feel" or "I am feeling".
    """

    phrase = models.CharField(max_length=250)

    enabled = models.BooleanField(default=True)

    def __unicode__(self):
        return self.phrase

    def __init__(self, *args, **kwargs):
        super(FeelingIndicator, self).__init__(*args, **kwargs)
        self._reg = None

    def extract_feeling(self, text, feelings_set):
        """
        Given the text of a tweet and a set of all valid FeelingWords,
        returns a tuple of strings: (indicator phrase, valid feeling).

        If the indicator isn't present, returns (None, None).
        If it is present but no feeling is identified, returns (indicator phrase, None).

        Raises an exception if something goes wrong splitting the text.
        """

        # First compile the split regex
        if not self._reg:
            exp = INDICATOR_REG_TEMPLATE % re.escape(self.phrase)
            self._reg = re.compile(exp, re.IGNORECASE & re.MULTILINE)

        # split the text in two around the indicator
        segments = self._reg.split(text.lower(), maxsplit=1)

        if len(segments) == 2 + INDICATOR_REG_GROUP_COUNT:
            first_half = segments[0]
            second_half = segments[3]

            # tokenize the phrases
            before_tokens = nltk.word_tokenize(first_half)[-settings.WINDOW_BEFORE:]
            after_tokens = nltk.word_tokenize(second_half)[:settings.WINDOW_AFTER]

            # see if any of the words are in the word set
            # search afterwards then backwards before
            before_tokens.reverse()
            for token in after_tokens + before_tokens:
                if token in feelings_set:
                    return self.phrase, token

            # The indicator matched but no feeling found
            return self.phrase, None

        elif len(segments) > 1:
            raise Exception("Unexpected result from split: %s" % (str(segments)))

        # The indicator didn't match
        return None, None


class FeelingWord(models.Model):
    """
    A feeling word such as "fine" or "better" or "angry".
    """

    # The word itself
    word = models.CharField(max_length=250)

    # Disable tracking of this word
    untracked = models.BooleanField(default=False)

    # Disable display of this word
    hidden = models.BooleanField(default=False)

    # Display color for this feeling word
    color = models.CharField(max_length=25)


    def __unicode__(self):
        return self.word

    @classmethod
    def get_tracked_list(cls):
        return cls.objects.filter(untracked=False)


class TimeFrame(TweetTimeFrame):
    """
    Analyze the percent of tweets for feeling words in this time window.

    This frame tracks the total number of feeling tweets.
    """

    DURATION = settings.TIME_FRAME_DURATION

    # The number of feeling and all tweets in the frame
    feeling_tweets = models.PositiveIntegerField(null=True, blank=True, default=None)
    total_tweets = models.PositiveIntegerField(null=True, blank=True, default=None)

    def calculate(self, stream_data):
        """
        Calculates a new time frame from collected Twitter data.
        """

        # Just get the non-rts
        originals = stream_data.filter(retweeted_status_id=None)

        # Get all the words we are currently interested in tracking
        indicators = FeelingIndicator.objects.filter(enabled=True)
        feelings = FeelingWord.get_tracked_list()
        feelings_set = set(f.word for f in feelings)

        # Create a dict for holding the counts -- these will be initialized to 0 as needed
        # Index into this with feeling words
        # For example: tweet_counts_by_feeling['fine'] += 1
        tweet_counts_by_feeling = defaultdict(float)

        # Check if this is on an example collection interval
        examples = None
        if times.to_unix(self.start_time) % settings.EXAMPLE_INTERVAL.total_seconds() == 0:
            examples = defaultdict(list)

        # The number of tweets that matched an indicator but did NOT contain a recognized feeling.
        indicator_matches = 0
        largest_gap = timedelta(seconds=0)
        last_tweet_time = None
        for tweet in originals:

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

                        # If we're collecting examples, do so
                        if examples is not None:
                            examples[feeling_word].append(tweet)

                        break  # only one indicator per tweet, please

                    elif indicator_phrase:

                        # we have a match on the indicator but no detectable feeling
                        indicator_matches += 1

                except Exception as e:
                    logger.error("Error parsing tweet: %s", e.message)

        # If more than 20% of the frame was a gap, then consider it missing_data
        self.missing_data = len(originals) == 0 or (largest_gap.total_seconds() > (self.duration_seconds * 0.2))

        # Create a bunch of new FeelingCount objects to store the per-feeling data.
        feeling_counters = []
        example_tweets = []

        for feeling in feelings:
            if indicator_matches > 0:
                percent = tweet_counts_by_feeling[feeling.word] / indicator_matches
            else:
                percent = 0

            feeling_percent = FeelingPercent(
                frame=self,
                feeling=feeling,
                percent=percent,
                start_time=self.start_time,
                feeling_tweets=indicator_matches,
                missing_data=self.missing_data
            )

            # Choose an example if there are any
            if examples is not None and examples[feeling.word]:
                example = random.choice(examples[feeling.word])
                example_tweets.append(ExampleTweet.from_tweet(tweet=example, feeling=feeling, frame=self))

            feeling_counters.append(feeling_percent)

        # Save all the new frames
        FeelingPercent.objects.bulk_create(feeling_counters)

        if example_tweets:
            ExampleTweet.objects.bulk_create(example_tweets)

        # This global frame is now done
        self.feeling_tweets = indicator_matches
        self.total_tweets = len(stream_data)
        return stream_data

    @classmethod
    def get_average_rate(cls, start=None, end=None):
        """
        Gets the average rates in an interval.
        """
        query = cls.get_in_range(start=start, end=end, calculated=True) \
            .filter(missing_data=False)

        query = query.aggregate(models.Avg('feeling_tweets'), models.Avg('total_tweets')) \

        return {
            'feeling_tweets': query['feeling_tweets__avg'],
            'total_tweets': query['total_tweets__avg'],
        }

    @classmethod
    def get_frames_in_interval(cls, start=None, end=None):
        """
        Gets TimeFrame data over an interval, sorted by time.
        """
        return cls.get_in_range(start=start, end=end).order_by('start_time')


class FeelingPercent(TimedIntervalMixin, models.Model):
    """
    A class for storing the percent of tweets for a given feeling in a given time frame.
    """

    class Meta:
        index_together = [
            # TODO: figure out if feeling -> start_time would be faster
            # since we order by feeling, start_time in one of the queries
            # are other queries using this?
            ["start_time", "missing_data", "feeling"]
        ]

    DURATION = TimeFrame.DURATION

    frame = models.ForeignKey(TimeFrame)

    # The word whose frequency we are counting, or none for the total tweet count
    feeling = models.ForeignKey(FeelingWord, null=True, default=None, blank=True)

    # The percent of tweets with this feeling
    percent = models.FloatField(null=True, blank=True, default=None)

    ## Fields shared with TimeFrame to avoid joins

    # True if we think the data for this frame is missing data
    missing_data = models.BooleanField(default=True)

    # Total number of feeling tweets (of which percent is a percent)
    feeling_tweets = models.PositiveIntegerField(null=True, blank=True, default=None)

    @classmethod
    def get_average_percents(cls, start=None, end=None, feeling_ids=None):
        """
        Gets the average percentage for each feeling in an interval.
        """
        query = cls.get_in_range(start=start, end=end, feeling_ids=feeling_ids) \
            .filter(missing_data=False)

        query = query.values('feeling') \
            .annotate(models.Avg('percent')) \
            .order_by('feeling')

        result = {}

        for row in query:
            result[row['feeling']] = row['percent__avg']

        return result

    @classmethod
    def get_percents_in_interval(cls, start=None, end=None, feeling_ids=None):
        """
        Gets FeelingPercents over an interval.
        Applies sorting etc to generate data useful for the view.
        """
        query = cls.get_in_range(start=start, end=end, feeling_ids=feeling_ids)

        query = query.order_by('feeling', 'start_time')

        return query

    @classmethod
    def get_top_feeling_ids(cls, start=None, end=None, limit=5):
        """
        Get the feeling ids with the highest average rates in the time interval.
        """

        query = cls.get_in_range(start=start, end=end)

        query = query.filter(missing_data=False) \
            .values('feeling') \
            .annotate(models.Avg('percent')) \
            .order_by('-percent__avg') \

        if limit:
            query = query[:limit]

        ids = [r['feeling'] for r in query]

        return ids

    @classmethod
    def get_in_range(cls, start=None, end=None, calculated=None, feeling_ids=None):
        """
        Get the FeelingPercents in the interval, optionally filtered by a list of feeling ids.
        """
        query = super(FeelingPercent, cls).get_in_range(start, end, calculated)

        if feeling_ids:
            query = query.filter(feeling_id__in=feeling_ids)

        return query


class ExampleTweet(models.Model):
    """A subset of tweet fields"""

    class Meta:
        index_together = [
            ["feeling", "created_at"]
        ]

    tweet_id = models.BigIntegerField()
    text = models.CharField(max_length=250)

    user_id = models.BigIntegerField()
    user_screen_name = models.CharField(max_length=50)
    user_name = models.CharField(max_length=150)

    created_at = models.DateTimeField()

    # The time frame this is an example for, for easier rendering
    frame = models.ForeignKey(TimeFrame)

    # The feeling this is an example of for faster queries
    feeling = models.ForeignKey(FeelingWord)

    @classmethod
    def from_tweet(cls, tweet, feeling, frame):
        """Construct an ExampleTweet from a Tweet model"""

        return ExampleTweet(
            tweet_id=tweet.tweet_id,
            text=tweet.text,
            user_id=tweet.user_id,
            user_screen_name=tweet.user_screen_name,
            user_name=tweet.user_name,
            created_at=tweet.created_at,
            frame=frame,
            feeling=feeling
        )


    @classmethod
    def get_in_range(cls, start=None, end=None, feeling_ids=None):
        """
        Gets FeelingPercents over an interval.
        Applies sorting etc to generate data useful for the view.
        """

        query = cls.objects.all()

        if end:
            query = query.filter(created_at__lt=end)

        if start:
            query = query.filter(created_at__gte=start)

        if feeling_ids:
            query = query.filter(feeling_id__in=feeling_ids)

        query = query.order_by('feeling', 'created_at')

        return query
