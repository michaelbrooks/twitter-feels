#
#  Settings to use in development configuration
#

from common import *

########## DEBUG CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
TEMPLATE_DEBUG = DEBUG
########## END DEBUG CONFIGURATION


########## EMAIL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
########## END EMAIL CONFIGURATION

########## CACHE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#caches
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
########## END CACHE CONFIGURATION

########## TOOLBAR CONFIGURATION
# See: https://github.com/django-debug-toolbar/django-debug-toolbar#installation
INSTALLED_APPS += (
    'debug_toolbar',
)

# See: https://github.com/django-debug-toolbar/django-debug-toolbar#installation
INTERNAL_IPS = ('127.0.0.1',)

# See: https://github.com/django-debug-toolbar/django-debug-toolbar#installation
MIDDLEWARE_CLASSES = (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
) + MIDDLEWARE_CLASSES

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}

DEBUG_TOOLBAR_PATCH_SETTINGS = False
########## END TOOLBAR CONFIGURATION


########## COMPRESSION CONFIGURATION
# See: http://django_compressor.readthedocs.org/en/latest/settings/#django.conf.settings.COMPRESS_ENABLED
COMPRESS_ENABLED = False
########## END COMPRESSION CONFIGURATION


########## LOGGING CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#logging
LOGGING['loggers'] = {
    'django.request': {
        'handlers': ['mail_admins', 'console'],
        'level': 'DEBUG',
        'propagate': True,
    },
    "rq": {
        "handlers": ["console"],
        "level": "DEBUG"
    },
    "twitter_stream": {
        "handlers": ['console'],
        "level": "DEBUG",
    },
    "twitter_monitor": {
        "handlers": ['console'],
        "level": "DEBUG"
    },
    "thermometer": {
        "handlers": ['console'],
        "level": "DEBUG"
    },
    "stream_analysis": {
        "handlers": ['console'],
        "level": "DEBUG",
    }
}
########## END LOGGING CONFIGURATION


########## SCHEDULED TASKS SETTINGS
ANALYSIS_TIME_FRAME_TASKS['demo_vis'] = {
    "name": "Demo Vis Analysis",
    "frame_class_path": "twitter_feels.apps.demo_vis.models.DemoTimeFrame",
}
########## END SCHEDULED TASKS SETTINGS

########## DEMO VIS CONFIG
INSTALLED_APPS += (
    'twitter_feels.apps.demo_vis',
)
########## END DEMO VIS CONFIG