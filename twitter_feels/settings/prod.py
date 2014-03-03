"""
Production settings.
Based on https://github.com/rdegges/django-skel/blob/master/project_name/settings/prod.py
"""
from os import environ
from common import *

# Below are things we might need to deal with later
########## EMAIL CONFIGURATION
########## DATABASE CONFIGURATION
########## CACHE CONFIGURATION
########## STORAGE CONFIGURATION

########## REDIS CONFIGURATION

########## SECRET CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = environ.get('SECRET_KEY', SECRET_KEY)
########## END SECRET CONFIGURATION


########## DEBUG CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
# Just to make totally sure...
DEBUG = False

# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
TEMPLATE_DEBUG = DEBUG
########## END DEBUG CONFIGURATION

########## COMPRESSION CONFIGURATION
# See: http://django_compressor.readthedocs.org/en/latest/settings/#django.conf.settings.COMPRESS_ENABLED
COMPRESS_ENABLED = True
########## END COMPRESSION CONFIGURATION
