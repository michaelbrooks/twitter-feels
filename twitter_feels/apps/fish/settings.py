from django.conf import settings
from datetime import timedelta

FISH_SETTINGS = getattr(settings, 'FISH_SETTINGS', {
    'PERCENT_AS_EXAMPLES': 0.3,
    'TIME_FRAME_DURATION': timedelta(seconds=60)
})

# The width of the analysis time frames
PERCENT_AS_EXAMPLES = FISH_SETTINGS.get('PERCENT_AS_EXAMPLES', 0.3)

# The granularity/frequency of analysis
TIME_FRAME_DURATION = FISH_SETTINGS.get('TIME_FRAME_DURATION', timedelta(seconds=60))
