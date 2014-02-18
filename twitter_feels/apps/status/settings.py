from django.conf import settings
from datetime import timedelta as _td
from django.core.exceptions import ImproperlyConfigured
import re
from django.utils import importlib

# Add something like this to your settings
# The keys must be word-like.
# STATUS_SCHEDULED_TASKS = {
#     "thermometer": {
#         "name": "Thermometer",
#         "path": "twitter_feels.apps.thermometer.tasks.create_tasks",
#         "interval": 30
#     },
#      # timedeltas also work
#     "other": {
#         "name": "Something Else",
#         "path": "some.other.task",
#         "interval": timedelta(seconds=93)
#     },
# }


SCHEDULED_TASKS = getattr(settings, 'STATUS_SCHEDULED_TASKS', {})

def _import_attribute(name):
    """Return an attribute from a dotted path name (e.g. "path.to.func")."""
    module_name, attribute = name.rsplit('.', 1)
    module = importlib.import_module(module_name)
    return getattr(module, attribute)


_task_key = re.compile('\w+')
# Check the tasks
for key, task in SCHEDULED_TASKS.iteritems():
    # The keys must be word-like
    if not _task_key.match(key):
        raise ImproperlyConfigured("Key %s in STATUS_SCHEDULED_TASKS is not word-like." % key)

    # Try locating the target function
    try:
        task['target'] = _import_attribute(task['path'])
    except Exception:
        raise ImproperlyConfigured("Path for %s in STATUS_SCHEDULED_TASKS is not reachable" % key)

    if not isinstance(task['name'], basestring):
        raise ImproperlyConfigured("Name for %s in STATUS_SCHEDULED_TASKS is not a string" % key)

    # Convert all intervals into seconds
    if isinstance(task['interval'], _td):
        task['interval'] = task['interval'].total_seconds()
    elif not isinstance(task['interval'], (int, float, long)):
        raise ImproperlyConfigured("Interval for %s in STATUS_SCHEDULED_TASKS is not a number" % key)

