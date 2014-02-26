from collections import defaultdict
from datetime import timedelta
from django.db import models
import re
import nltk
import logging

import settings

logger = logging.getLogger('thermometer')


# Regex for matching indicators
from twitter_feels.libs.analysis import BaseTimeFrame, TimedIntervalMixin

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


class TimeFrame(BaseTimeFrame):
    """
    Analyze the percent of tweets for feeling words in this time window.

    This frame tracks the total number of feeling tweets.
    """

    DURATION = settings.TIME_FRAME_DURATION

    # The number of feeling and all tweets in the frame
    feeling_tweets = models.PositiveIntegerField(null=True, blank=True, default=None)
    total_tweets = models.PositiveIntegerField(null=True, blank=True, default=None)

    def calculate(self, tweets):
        """
        Calculates a new time frame from collected Twitter data.
        """

        # Just get the non-rts
        originals = tweets.filter(retweeted_status_id=None)

        # Get all the words we are currently interested in tracking
        indicators = FeelingIndicator.objects.filter(enabled=True)
        feelings = FeelingWord.get_tracked_list()
        feelings_set = set(f.word for f in feelings)

        # Create a dict for holding the counts -- these will be initialized to 0 as needed
        # Index into this with feeling words
        # For example: tweet_counts_by_feeling['fine'] += 1
        tweet_counts_by_feeling = defaultdict(float)

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

                        break  # only one indicator per tweet, please

                    elif indicator_phrase:

                        # we have a match on the indicator but no detectable feeling
                        indicator_matches += 1

                except Exception as e:
                    logger.error("Error parsing tweet: %s", e.message)

        # If more than 20% of the frame was a gap, then consider it missing_data
        missing_data = len(originals) == 0 or (largest_gap.total_seconds() > (self.duration_seconds * 0.2))

        # Create a bunch of new FeelingCount objects to store the per-feeling data.
        feeling_counters = []

        for feeling in feelings:
            if indicator_matches > 0:
                percent = tweet_counts_by_feeling[feeling.word] / indicator_matches
            else:
                percent = 0

            feeling_counters.append(FeelingPercent(
                frame=self,
                feeling=feeling,
                percent=percent,
                start_time=self.start_time,
                feeling_tweets=indicator_matches,
                missing_data=missing_data
            ))

        # Save all the new frames
        FeelingPercent.objects.bulk_create(feeling_counters)

        # This global frame is now done
        self.feeling_tweets = indicator_matches
        self.total_tweets = len(tweets)
        self.mark_done(tweets, missing_data=missing_data)


class FeelingPercent(TimedIntervalMixin, models.Model):
    """
    A class for storing the percent of tweets for a given feeling in a given time frame.
    """

    class Meta:
        index_together = [
            ["missing_data", "feeling"],
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
    def get_average_rates(cls, start=None, end=None):
        """
        Gets the average percentage for each feeling in an interval.
        """
        query = cls.get_in_range(start=start, end=end) \
            .filter(missing_data=False)

        query = query.values('feeling') \
            .annotate(models.Avg('percent')) \
            .order_by('feeling')

        result = [row['percent__avg'] for row in query]

        return result

    @classmethod
    def get_percents_in_interval(cls, start=None, end=None):
        """
        Gets FeelingPercents over an interval.
        Applies sorting etc to generate data useful for the view.
        """
        query = cls.get_in_range(start=start, end=end)

        query = query.order_by('start_time', 'feeling')

        return query
