from django.db import models
import re
import nltk
from settings import WINDOW_AFTER, WINDOW_BEFORE

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
            before_tokens = nltk.word_tokenize(first_half)[-WINDOW_BEFORE:]
            after_tokens = nltk.word_tokenize(second_half)[:WINDOW_AFTER]

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


class TimeFrame(models.Model):
    """
    Tweet percent for feeling word in a specific time window.

    If the feeling is None, then the TimeFrame is a "global frame", and the
    tweets field represents the total number of tweets that matched any indicator,
    but where NO particular feeling was detected.
    """

    class Meta:
        index_together = [
            ["incomplete", "feeling"],
            ["calculated", "end_time", "feeling"]
        ]

    # Some slightly redundant timing info for convenience
    start_time = models.DateTimeField(db_index=True)
    end_time = models.DateTimeField(db_index=True)
    duration_seconds = models.PositiveIntegerField()

    # The word whose frequency we are counting, or none for the total tweet count
    feeling = models.ForeignKey(FeelingWord, null=True, default=None, blank=True)

    # The percent of tweets with this feeling
    # If it is a global frame, this holds the ABSOLUTE NUMBER of tweets in the frame
    tweets = models.FloatField(null=True, blank=True, default=None)

    # True if this frame has been calculated
    calculated = models.BooleanField(default=False)

    # True if we think the data for this frame is incomplete
    incomplete = models.BooleanField(default=True)

    @classmethod
    def create_global(cls, start_time, time_delta):
        """
        Creates a TimeFrame without a feeling assigned.
        """
        return cls(
            start_time=start_time,
            end_time=start_time + time_delta,
            duration_seconds=time_delta.total_seconds(),
            feeling=None,
            tweets=None,
            calculated=False,
            incomplete=True
        )

    def create_subframe(self, feeling=None, tweets=None, calculated=False, incomplete=False):
        """
        Make a duplicate of this frame but with the feeling set.
        """
        return TimeFrame(
            start_time=self.start_time,
            end_time=self.end_time,
            duration_seconds=self.duration_seconds,
            feeling=feeling,
            tweets=tweets,
            calculated=calculated,
            incomplete=incomplete
        )

    @classmethod
    def get_latest(cls):
        """
        Returns the latest timeframe for the given word.
        """
        return cls.objects \
            .latest(field_name='start_time')

    @classmethod
    def get_earliest(cls):
        """
        Returns the earliest timeframe for the given word.
        """
        return cls.objects \
            .earliest(field_name='start_time')

    @classmethod
    def get_average_rates(cls, start=None, end=None):
        """
        Gets the average percentage for each feeling.
        """
        query = cls.objects \
            .filter(incomplete=False, feeling__isnull=False)

        if end:
            query = query.filter(start_time__lt=end)
        if start:
            query = query.filter(end_time__gt=start)

        query = query.values('feeling')\
            .annotate(models.Avg('tweets')) \
            .order_by('feeling')

        result = [row['tweets__avg'] for row in query]

        return result

    @classmethod
    def get_frames(cls, start=None, end=None):
        """
        Gets the count of each feeling at time frames over an interval.
        """
        query = cls.objects.filter(calculated=True)

        if end:
            query = query.filter(start_time__lt=end)
        if start:
            query = query.filter(end_time__gt=start)

        query = query.order_by('end_time', 'feeling')

        return query

    def __unicode__(self):
        return "[%s, %s] %s (%d tweets)" % (self.start_time, self.end_time, self.feeling, self.tweets or 0)