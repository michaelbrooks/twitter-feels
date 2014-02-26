import datetime
import time
from django.core.exceptions import ObjectDoesNotExist
from django.db import models

class TimedIntervalMixin(models.Model):
    """
    Provides several convenient methods for working with models that have
    a start_time field and a DURATION property.
    """

    # Tells Django not to make a table for this abstract class.
    class Meta:
        abstract = True

    # A timedelta representing the size of these time frames.
    # They will all be the same.
    DURATION = datetime.timedelta(minutes=1)

    # The time when this time frame starts.
    start_time = models.DateTimeField(db_index=True)

    #######
    # Object properties - for convenience.
    #######

    @property
    def duration(self):
        """
        Get the duration (a timedelta) of this time frame.
        """
        return type(self).DURATION

    @property
    def duration_seconds(self):
        """
        Get the duration in seconds of this time frame.
        """
        return type(self).DURATION.total_seconds()

    @property
    def end_time(self):
        """
        The end time for this time frame.
        """
        return self.start_time + self.duration


    #######
    # Class methods
    #######

    @classmethod
    def get_latest(cls):
        """
        Returns the latest time frame, or None.
        """
        try:
            return cls.objects \
                .latest(field_name='start_time')
        except ObjectDoesNotExist:
            return None

    @classmethod
    def get_earliest(cls):
        """
        Returns the earliest time frame, or None.
        """
        try:
            return cls.objects \
                .earliest(field_name='start_time')
        except ObjectDoesNotExist:
            return None

    @classmethod
    def get_latest_end_time(cls):
        """
        Returns end time of the latest time frame.
        This is much more efficient than get_latest().end_time.
        """
        result = cls.objects.aggregate(latest_start_time=models.Max('start_time'))
        if result['latest_start_time']:
            return result['latest_start_time'] + cls.DURATION
        else:
            return None

    @classmethod
    def get_earliest_start_time(cls):
        """
        Returns the start time of the earliest time frame.
        This is much more efficient than get_earliest().start_time.
        """
        result = cls.objects.aggregate(earliest_start_time=models.Min('start_time'))
        return result['earliest_start_time']

    @classmethod
    def get_in_range(cls, start=None, end=None, calculated=None):
        """
        Returns a queryset that provides all of the frames.

        If start and end are provided, only frames overlapping
        with the time specified will be returned.

        May be filtered to only calculated frames.
        """

        query = cls.objects.all()

        if calculated is not None:
            query = query.filter(calculated=calculated)

        if end:
            query = query.filter(start_time__lt=end)

        if start:
            # We only have a start_time field, so modify "start"
            # to reflect the duration.
            query = query.filter(start_time__gt=start - cls.DURATION)

        return query


class BaseTimeFrame(TimedIntervalMixin, models.Model):
    """
    Describes a frame of analysis, a fixed interval of time.
    It has a start and a duration.

    Any properties added on subclasses should have default
    values set!
    """

    # Tells Django not to make a table for this abstract class.
    class Meta:
        abstract = True

    # True if this frame has been calculated
    calculated = models.BooleanField(default=False)

    # True if we think the data for this frame is missing data
    missing_data = models.BooleanField(default=True)

    # The time in seconds taken by analysis. Before calculated=True, this is analysis start time.
    analysis_time = models.FloatField(default=None, null=True, blank=True)


    #######
    # Instance methods
    #######

    def calculate(self, tweets):
        """
        Perform the analysis procedure that results in
        'calculated' being set to true.

        Should be overridden in derived classes.
        The implementation should call mark_done(tweets)
        with all of the tweets that you wouldn't mind
        being deleted.

        The 'tweets' parameter is a query set (iterable) over
        all of the tweets enclosed in this time frame.
        This includes RTs and everything.
        """
        self.mark_done(tweets)

    def mark_started(self):
        """Saves the current time, indicating analysis is beginning."""
        self.analysis_time = time.time()
        self.save()

    def mark_done(self, tweets, missing_data=False):
        """
        Marks the time frame as calculated.
        Marks the tweets and analyzed.

        The missing_data field can also be set to indicate
        if the time frame had complete data.
        """

        self.calculated = True
        self.missing_data = missing_data

        # Calculate the time taken for analysis
        if self.analysis_time:
            self.analysis_time = time.time() - self.analysis_time

        self.save()

        # Increase the analyzed_by count on the tweets
        tweets.update(analyzed_by=models.F('analyzed_by') + 1)


    def __unicode__(self):
        """Printing for Django admin / debugging"""
        return "[%s, %s]"

    @classmethod
    def get_average_analysis_time(cls, start=None, end=None):
        """Returns the average time taken to analyze these time frames."""

        query = cls.get_in_range(start=start, end=end, calculated=True)

        result = query.aggregate(average_analysis_time=models.Avg('analysis_time'))
        return result['average_analysis_time']

    @classmethod
    def count_completed(cls):
        """Counts the number of completed frames of this type."""
        query = cls.get_in_range(calculated=True)
        return query.count()