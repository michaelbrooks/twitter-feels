from django.conf import settings
from datetime import timedelta

DEBUG = settings.DEBUG

MAP_SETTINGS = getattr(settings, 'MAP_SETTINGS', {
    'MAX_DEPTH': 10,
    'KEEP_DATA_FOR': timedelta(hours=24),
    'NODE_FREEZE_INTERVAL': timedelta(minutes=3)
})

# The width of the analysis time frames
MAX_DEPTH = MAP_SETTINGS.get('MAX_DEPTH', 10)

# The amount of time to keep data around
KEEP_DATA_FOR = MAP_SETTINGS.get('KEEP_DATA_FOR', timedelta(hours=24))

# Nodes are frozen for this much time whenever
# they are created or touched to prevent race conditions
NODE_FREEZE_INTERVAL = MAP_SETTINGS.get('NODE_FREEZE_INTERVAL', timedelta(minutes=3))
