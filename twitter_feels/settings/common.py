"""
Common Django settings for twitter_feels project.

based on https://github.com/rdegges/django-skel/blob/master/project_name/settings/common.py
"""
import dj_database_url

from os.path import abspath, basename, dirname, join, normpath
from sys import path
import datetime
from os import environ

########## PATH CONFIGURATION
# Absolute filesystem path to the Django project directory:
DJANGO_ROOT = dirname(dirname(abspath(__file__)))

# Absolute filesystem path to the top-level project folder:
SITE_ROOT = dirname(DJANGO_ROOT)

# Site name:
SITE_NAME = basename(DJANGO_ROOT)

# Add our project to our pythonpath, this way we don't need to type our project
# name in our dotted import paths:
path.append(DJANGO_ROOT)
########## END PATH CONFIGURATION


########## DEBUG CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = False

# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
TEMPLATE_DEBUG = DEBUG
########## END DEBUG CONFIGURATION


########## MANAGER CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = (
    ('Your Name', 'your_email@example.com'),
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS
########## END MANAGER CONFIGURATION


########## DATABASE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {'default': dj_database_url.config(default='sqlite://default.db')}
if DATABASES['default']['ENGINE'] == 'django.db.backends.mysql':
    # enable utf8mb4 on mysql
    DATABASES['default']['OPTIONS'] = {'charset': 'utf8mb4'}
########## END DATABASE CONFIGURATION


########## Redis Queue (RQ) CONFIGURATION
RQ_QUEUES = {
    'default': {
        'URL': environ.get('REDIS_URL', 'redis://localhost:6379'),
        'DB': 0,
    },
}
# Warning: Overrides the admin template!
RQ_SHOW_ADMIN_LINK = True
######### END RQ CONFIGURATION


########## GENERAL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#time-zone
TIME_ZONE = 'UTC'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = 'en-us'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-l10n
USE_L10N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = True

# Path to prepend to the start of urls
SITE_PREFIX = environ.get('SITE_PREFIX', '/')
########## END GENERAL CONFIGURATION


########## MEDIA CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = normpath(join(DJANGO_ROOT, 'media'))

# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = '%smedia/' % SITE_PREFIX
########## END MEDIA CONFIGURATION


########## STATIC FILE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = normpath(join(DJANGO_ROOT, 'static'))

# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = '%sstatic/' % SITE_PREFIX

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = (
    normpath(join(DJANGO_ROOT, 'assets')),
)

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)
########## END STATIC FILE CONFIGURATION


########## SECRET CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = r'w9^0h5s9_wr*to*a5i_(8j=u0dnw$n#@(u+&%n&na!d^uivi0^'
########## END SECRET CONFIGURATION


########## FIXTURE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-FIXTURE_DIRS
FIXTURE_DIRS = (
    normpath(join(DJANGO_ROOT, 'fixtures')),
)
########## END FIXTURE CONFIGURATION


########## TEMPLATE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.request',

    # Adds a 'site' variable to every template
    'twitter_feels.context_processors.current_site',
    'twitter_feels.context_processors.debug_mode',
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-loaders
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
TEMPLATE_DIRS = (
    normpath(join(DJANGO_ROOT, 'templates')),
)
########## END TEMPLATE CONFIGURATION


########## MIDDLEWARE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#middleware-classes
MIDDLEWARE_CLASSES = (
    # Default Django middleware.
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)
########## END MIDDLEWARE CONFIGURATION


########## URL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#root-urlconf
ROOT_URLCONF = '%s.urls' % SITE_NAME
########## END URL CONFIGURATION


########## APP CONFIGURATION
DJANGO_APPS = (
    # Default Django apps:
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Useful template tags:
    'django.contrib.humanize',

    # Admin panel and documentation:
    'django.contrib.admin',
    'django.contrib.admindocs',
)

THIRD_PARTY_APPS = (
    # Bootstrap integration
    'bootstrap3',

    # Static file combination:
    'compressor',

    # Django and RQ integration
    'django_rq',

    # Hierarchical navigation template tags
    'lineage',

    # Streaming tweets
    'twitter_stream',

    # Anslysis tasks for the stream
    "stream_analysis",
)

LOCAL_APPS = (

    # A thermometer visualization
    'twitter_feels.apps.thermometer',

    # A thermometer visualization
    'twitter_feels.apps.map',

    # A status monitoring app
    'twitter_feels.apps.status',

    # Utilities for twitter streaming analysis
    'twitter_feels.libs.twitter_analysis'
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS
########## END APP CONFIGURATION


########## LOGGING CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    "formatters": {
        "time_formatter": {
            "format": "%(asctime)s %(levelname)s [%(name)s] %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
            'formatter': 'time_formatter'
        },
        'error_console': {
            'level': 'WARN',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stderr',
            'formatter': 'time_formatter'
        },
        'web_access_log': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins', 'web_access_log'],
            'level': 'ERROR',
            'propagate': True,
        },
        "rq.worker": {
            "handlers": ["console", 'error_console'],
            "level": "ERROR"
        },
        "twitter_stream": {
            "handlers": ["console", 'error_console'],
            "level": "ERROR",
        },
        "twitter_monitor": {
            "handlers": ["console", 'error_console'],
            "level": "WARN"
        },
        "thermometer": {
            "handlers": ["console", 'error_console'],
            "level": "ERROR"
        },
        "stream_analysis": {
            "handlers": ["console", 'error_console'],
            "level": "ERROR",
        },
        'gunicorn.error': {
            'level': 'ERROR',
            'handlers': ['error_console'],
            'propagate': True,
        },
        'gunicorn.access': {
            'level': 'INFO',
            'handlers': ['web_access_log'],
            'propagate': False,
        },
    }
}
########## END LOGGING CONFIGURATION


########## COMPRESSION CONFIGURATION
# See: http://django_compressor.readthedocs.org/en/latest/settings/#django.conf.settings.COMPRESS_ENABLED
COMPRESS_ENABLED = True

# See: http://django-compressor.readthedocs.org/en/latest/settings/#django.conf.settings.COMPRESS_CSS_HASHING_METHOD
COMPRESS_CSS_HASHING_METHOD = 'content'

# See: http://django_compressor.readthedocs.org/en/latest/settings/#django.conf.settings.COMPRESS_CSS_FILTERS
COMPRESS_CSS_FILTERS = [
    'compressor.filters.template.TemplateFilter',
]

# See: http://django_compressor.readthedocs.org/en/latest/settings/#django.conf.settings.COMPRESS_JS_FILTERS
COMPRESS_JS_FILTERS = [
    'compressor.filters.template.TemplateFilter',
]
########## END COMPRESSION CONFIGURATION



########## WSGI CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = 'wsgi.application'
########## END WSGI CONFIGURATION


########## BOOTSTRAP SETTINGS
BOOTSTRAP3 = {
}
########## END BOOTSTRAP SETTINGS


########## SCHEDULED TASKS SETTINGS
ANALYSIS_TIME_FRAME_TASKS = {
    "thermometer": {
        "name": "Thermometer Analysis",
        "frame_class_path": "twitter_feels.apps.thermometer.models.TimeFrame",
    },
    "map": {
        "name": "Map Analysis",
        "frame_class_path": "twitter_feels.apps.map.models.MapTimeFrame",
    },
}
########## END SCHEDULED TASKS SETTINGS


########## THERMOMETER SETTINGS
THERMOMETER_SETTINGS = {
    'TIME_FRAME_DURATION': datetime.timedelta(60),
    # the number of words before and after the indicators to examine
    'WINDOW_AFTER': 5,
    'WINDOW_BEFORE': 2,
    'HISTORICAL_INTERVAL': datetime.timedelta(hours=24),
    'DISPLAY_INTERVAL': datetime.timedelta(minutes=60),
}
########## END THERMOMETER SETTINGS
