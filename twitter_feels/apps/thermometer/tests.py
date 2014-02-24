from datetime import timedelta
from django.utils import timezone
from django.test import TestCase
from models import TimeFrame, FeelingWord

# Create your tests here.

class TimeFrameTests(TestCase):

    def _create_three(self):
        duration = timedelta(seconds=60)
        start_time = timezone.now()

        mid = TimeFrame.create_global(
            start_time=start_time,
            time_delta=duration
        )
        mid.save()

        last = TimeFrame.create_global(
            start_time=start_time + duration,
            time_delta=duration
        )
        last.save()

        first = TimeFrame.create_global(
            start_time=start_time - duration,
            time_delta=duration
        )
        first.save()

        return (first, mid, last)

    def test_get_latest_returns_latest(self):
        """
        Make sure we can get the latest time frame.
        """

        first, mid, last = self._create_three()

        latest = TimeFrame.get_latest()

        self.assertEqual(latest, last)

    def test_get_earliest_returns_earliest(self):
        """
        Make sure we can get the earliest time frame.
        """

        first, mid, last = self._create_three()
        earliest = TimeFrame.get_earliest()
        self.assertEqual(earliest, first)

