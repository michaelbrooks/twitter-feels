from django.conf import settings
from datetime import timedelta

TIME_FRAME_DURATION = getattr(settings, 'TIME_FRAME_DURATION', timedelta(seconds=60))

# the number of words before and after the indicators to examine
WINDOW_AFTER = getattr(settings, 'WINDOW_AFTER', 5)
WINDOW_BEFORE = getattr(settings, 'WINDOW_BEFORE', 2)

HISTORICAL_INTERVAL = getattr(settings, 'HISTORICAL_INTERVAL', timedelta(hours=24))
DISPLAY_INTERVAL = getattr(settings, 'DISPLAY_INTERVAL', timedelta(minutes=60))