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

    def test_get_latest_respects_word(self):
        """
        Make sure get_latest respects word setting.
        """
        first, mid, last = self._create_three()

        # make a word
        word = FeelingWord(word="test")
        word.save()

        # last will now be associated with the word
        last.word = word
        last.save()

        # "last" should no longer be the latest with no word
        latest = TimeFrame.get_latest()
        self.assertEqual(latest, mid)

        # But if we ask for with the word, it should be
        latest = TimeFrame.get_latest(word=word)
        self.assertEqual(latest, last)

        # Add the word to "mid"
        mid.word = word
        mid.save()

        # Now if we want the last *with* the word, it should still be last
        latest = TimeFrame.get_latest(word=word)
        self.assertEqual(latest, last)

