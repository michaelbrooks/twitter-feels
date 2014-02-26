from collections import defaultdict
from datetime import timedelta
from django.db import models
import re
import nltk
import logging

import settings

logger = logging.getLogger('thermometer')


# Regex for matching indicators
from twitter_feels.libs.analysis import BaseTimeFrame

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
    Tweet percent for feeling word in a specific time window.

    If the feeling is None, then the TimeFrame is a "global frame", and the
    tweets field represents the total number of tweets that matched any indicator,
    but where NO particular feeling was detected.
    """

    DURATION = settings.TIME_FRAME_DURATION

    class Meta:
        index_together = [
            ["missing_data", "feeling"],
            ["calculated", "start_time", "feeling"]
        ]

    # The word whose frequency we are counting, or none for the total tweet count
    feeling = models.ForeignKey(FeelingWord, null=True, default=None, blank=True)

    # The percent of tweets with this feeling
    # If it is a global frame, this holds the ABSOLUTE NUMBER of tweets in the frame
    tweets = models.FloatField(null=True, blank=True, default=None)

    def create_subframe(self, feeling=None, tweets=None, calculated=False, missing_data=False):
        """
        Make a duplicate of this frame but with the feeling set.
        """
        return TimeFrame(
            start_time=self.start_time,
            feeling=feeling,
            tweets=tweets,
            calculated=calculated,
            missing_data=missing_data
        )

    def calculate(self, tweets):
        """
        Calculates a new time frame from collected Twitter data.
        """

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

        # If more than 20% of the frame was a gap, then consider it missing_data
        missing_data = len(tweets) == 0 or (largest_gap.total_seconds() > (self.duration_seconds * 0.2))

        # Create a bunch of new data frames to store the per-feeling data.
        sub_frames = []

        for feeling in feelings:
            if indicator_matches > 0:
                percent = tweet_counts_by_feeling[feeling.word] / indicator_matches
            else:
                percent = 0

            sub_frames.append(self.create_subframe(
                feeling=feeling,
                tweets=percent,
                calculated=True,
                missing_data=missing_data
            ))

        # Save all the new frames
        TimeFrame.objects.bulk_create(sub_frames)

        # This global frame is now done
        self.tweets = indicator_matches
        self.mark_done(missing_data=missing_data)


    ######
    # Class methods specific to the thermometer views.
    ######

    @classmethod
    def get_average_rates(cls, start=None, end=None):
        """
        Gets the average percentage for each feeling in an interval.
        """
        query = cls.get_frames(start=start, end=end) \
            .filter(missing_data=False, feeling__isnull=False)

        query = query.values('feeling') \
            .annotate(models.Avg('tweets')) \
            .order_by('feeling')

        result = [row['tweets__avg'] for row in query]

        return result

    @classmethod
    def get_frames_in_interval(cls, start=None, end=None):
        """
        Gets the count of each feeling at time frames over an interval.
        Applies sorting etc to generate data useful for the view.
        """
        query = super(TimeFrame, cls).get_frames(start, end, calculated=True)

        query = query.order_by('start_time', 'feeling')

        return query
