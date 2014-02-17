from django.db import models
import re


class FeelingGroup(models.Model):
    """
    Represents a group of related feelings, such as "anger" or "happiness".
    """
    name = models.CharField(max_length=250)

    def __unicode__(self):
        return self.name


class FeelingPrefix(models.Model):
    """
    A feeling prefix such as "I feel" or "You need"
    """

    prefix = models.CharField(max_length=250)

    enabled = models.BooleanField(default=True)

    def __unicode__(self):
        return self.prefix

    def __init__(self, *args, **kwargs):
        super(FeelingPrefix, self).__init__(*args, **kwargs)
        self._reg = None

    def get_next_word(self, text):
        """
        Returns the word following this term in the text,
        or None if the term is not in the text at all.
        """

        if not self._reg:
            exp = (r"([^\w]|^)"   # something that is not wordy
                   r"%s"       # the term/phrase
                   r"([^\w]+)"    # another non-wordy bit
                   r"(\w*)"       # the word we care about
                   r"([^\w]|$)")  # another non-wordy bit
            self._target_group = 3
            self._reg = re.compile(exp % re.escape(self.prefix), re.IGNORECASE & re.MULTILINE)

        match = self._reg.search(text)
        if match:
            return match.group(self._target_group)

        return None


class FeelingWord(models.Model):
    """
    A feeling word such as "fine" or "better" or "angry".
    """

    # The word itself
    word = models.CharField(max_length=250)

    # A higher-level feeling group
    group = models.ForeignKey(FeelingGroup, null=True, default=None, blank=True)

    enabled = models.BooleanField(default=True)

    def __unicode__(self):
        return self.word


class TimeFrame(models.Model):
    """
    Tweet count for a specific word in a specific time window.
    """

    # Some slightly redundant timing info for convenience
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    duration_seconds = models.PositiveIntegerField()

    # The prefix and word whose frequency we are counting, or none for the total tweet count
    prefix = models.ForeignKey(FeelingPrefix, null=True, default=None, blank=True)
    word = models.ForeignKey(FeelingWord, null=True, default=None, blank=True)

    # The number of tweets
    tweet_count = models.PositiveIntegerField(null=True, blank=True, default=None)
    calculated_at = models.DateTimeField(null=True, blank=True, default=None)

    @classmethod
    def create_global(cls, start_time, time_delta):
        """
        Creates a TimeFrame without a word/prefix assigned.
        """
        return cls(
            start_time=start_time,
            end_time=start_time + time_delta,
            duration_seconds=time_delta.total_seconds(),
            word=None,
            prefix=None,
            tweet_count=None
        )

    def create_subframe(self, word=None, prefix=None, tweet_count=None):
        """
        Make a duplicate of this frame but with the word and/or prefix set.
        """
        return TimeFrame(
            start_time=self.start_time,
            end_time=self.end_time,
            duration_seconds=self.duration_seconds,
            word=word,
            prefix=prefix,
            tweet_count=tweet_count
        )

    @classmethod
    def get_latest(cls, word=None, prefix=None):
        """
        Returns the latest timeframe for the given word.
        """
        return cls.objects \
            .filter(word=word, prefix=prefix) \
            .latest(field_name='start_time')

    @classmethod
    def get_earliest(cls, word=None, prefix=None):
        """
        Returns the earliest timeframe for the given word.
        """
        return cls.objects \
            .filter(word=word, prefix=prefix) \
            .earliest(field_name='start_time')

    def __unicode__(self):
        return "%s %s, %d tweets at %s" % (self.prefix, self.word, self.tweet_count or 0, self.start_time)