from django.db import models

# Create your models here.

class FeelingGroup(models.Model):
    """
    Represents a group of related feelings, such as "anger" or "happiness".
    """
    name = models.CharField(max_length=250)


class FeelingWord(models.Model):
    """
    A feeling word such as "fine" or "better" or "angry".
    """

    # The word itself
    word = models.CharField(max_length=250)

    # A higher-level feeling group
    group = models.ForeignKey(FeelingGroup, null=True, default=None)


class TimeFrame(models.Model):
    """
    Tweet count for a specific word in a specific time window.
    """

    # Some slightly redundant timing info for convenience
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    duration_seconds = models.PositiveIntegerField()

    # The word whose frequency we are counting, or none for the total tweet count
    word = models.ForeignKey(FeelingWord, null=True)
    tweet_count = models.PositiveIntegerField(default=0)
