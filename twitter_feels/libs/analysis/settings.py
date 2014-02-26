from django.conf import settings


# Add something like this to your settings
# The keys must be word-like.
# ANALYSIS_TIME_FRAME_TASKS = {
#     "thermometer": {
#         "name": "Thermometer",
#         "frame_class_path": "twitter_feels.apps.thermometer.models.TimeFrame",
#     },
#     "other": {
#         "name": "Something Else",
#         "frame_class_path": "some.other.OtherTimeFrame",
#     },
# }


TIME_FRAME_TASKS = getattr(settings, 'ANALYSIS_TIME_FRAME_TASKS', {})

