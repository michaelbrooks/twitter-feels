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
TIME_FRAME_DURATION = THERMOMETER_SETTINGS.get('TIME_FRAME_DURATION', timedelta(seconds=60))

# the number of words before and after the indicators to examine
WINDOW_AFTER = THERMOMETER_SETTINGS.get('WINDOW_AFTER', 5)
WINDOW_BEFORE = THERMOMETER_SETTINGS.get('WINDOW_BEFORE', 2)

# The time to show as the mid-term average on the thermometers
HISTORICAL_INTERVAL = THERMOMETER_SETTINGS.get('HISTORICAL_INTERVAL', timedelta(hours=24))

# The interval to show in the timeline
DISPLAY_INTERVAL = THERMOMETER_SETTINGS.get('DISPLAY_INTERVAL', timedelta(minutes=60))

# The number of feelings to show by default
DEFAULT_FEELINGS = THERMOMETER_SETTINGS.get('DEFAULT_FEELINGS', 5)

# The size of the moving average window used to display timelines
SMOOTHING_WINDOW_SIZE = THERMOMETER_SETTINGS.get('SMOOTHING_WINDOW_SIZE', 10)