from django.conf import settings
from datetime import timedelta

DEBUG = settings.DEBUG

MAP_SETTINGS = getattr(settings, 'MAP_SETTINGS', {
    'MAX_DEPTH': 10,
    'KEEP_DATA_FOR': timedelta(hours=24)
})

# The width of the analysis time frames
MAX_DEPTH = MAP_SETTINGS.get('MAX_DEPTH', 10)

KEEP_DATA_FOR = MAP_SETTINGS.get('KEEP_DATA_FOR', timedelta(hours=24))
