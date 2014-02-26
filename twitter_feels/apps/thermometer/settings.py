from django.conf import settings
from datetime import timedelta

THERMOMETER_SETTINGS = getattr(settings, 'THERMOMETER_SETTINGS', {
    'TIME_FRAME_DURATION': timedelta(60),
    # the number of words before and after the indicators to examine
    'WINDOW_AFTER': 5,
    'WINDOW_BEFORE': 2,
    'HISTORICAL_INTERVAL': timedelta(hours=24),
    'DISPLAY_INTERVAL': timedelta(minutes=60),
})

# The width of the analysis time frames
TIME_FRAME_DURATION = getattr(THERMOMETER_SETTINGS, 'TIME_FRAME_DURATION', timedelta(seconds=60))

# the number of words before and after the indicators to examine
WINDOW_AFTER = getattr(THERMOMETER_SETTINGS, 'WINDOW_AFTER', 5)
WINDOW_BEFORE = getattr(THERMOMETER_SETTINGS, 'WINDOW_BEFORE', 2)

# The time to show as the mid-term average on the thermometers
HISTORICAL_INTERVAL = getattr(THERMOMETER_SETTINGS, 'HISTORICAL_INTERVAL', timedelta(hours=24))

# The interval to show in the timeline
DISPLAY_INTERVAL = getattr(THERMOMETER_SETTINGS, 'DISPLAY_INTERVAL', timedelta(minutes=60))