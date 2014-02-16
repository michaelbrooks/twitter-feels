from django.conf import settings
from datetime import timedelta

TIME_FRAME_DURATION = getattr(settings, 'TIME_FRAME_DURATION', timedelta(seconds=60))
