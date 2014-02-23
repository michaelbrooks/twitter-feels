from django.conf import settings
from datetime import timedelta

TIME_FRAME_DURATION = getattr(settings, 'TIME_FRAME_DURATION', timedelta(seconds=60))

# the number of words before and after the indicators to examine
WINDOW_AFTER = 5
WINDOW_BEFORE = 2