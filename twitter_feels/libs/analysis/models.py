import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db import models


class BaseTimeFrame(models.Model):
    """
    Describes a frame of analysis, a fixed interval of time.
    It has a start and a duration.

    Any properties added on subclasses should have default
    values set!
    """

    # Tells Django not to make a table for this abstract class.
    class Meta:
        abstract = True

    # A timedelta representing the size of these time frames.
    # They will all be the same.
    DURATION = datetime.timedelta(minutes=1)

    # The time when this time frame starts.
    start_time = models.DateTimeField(db_index=True)

    # True if this frame has been calculated
    calculated = models.BooleanField(default=False)

    # True if we think the data for this frame is missing data
    missing_data = models.BooleanField(default=True)


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
    # Instance methods
    #######

    def calculate(self, tweets):
        """
        Perform the analysis procedure that results in
        'calculated' being set to true.

        Should be overridden in derived classes.
        The implementation should set 'calculated'
        and save the model.

        The 'tweets' parameter is a query set (iterable) over
        all of the tweets enclosed in this time frame.
        """
        self.calculated = True
        self.save()

    def mark_done(self, missing_data=False):
        """
        Marks the time frame as calculated.
        missing_data can also be set.
        """
        self.calculated = True
        self.missing_data = missing_data
        self.save()

    def __unicode__(self):
        """Printing for Django admin / debugging"""
        return "[%s, %s]"


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
    def get_frames(cls, start=None, end=None, calculated=None):
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
