from django.conf import settings
from datetime import timedelta

MAP_SETTINGS = getattr(settings, 'MAP_SETTINGS', {
    'MAX_DEPTH': 10,
})

# The width of the analysis time frames
MAX_DEPTH = MAP_SETTINGS.get('MAX_DEPTH', 10)
