"""
WSGI config for twitter_feels project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os

# https://github.com/kennethreitz/dj-static
from dj_static import Cling

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "twitter_feels.settings")

from django.conf import settings

class PrefixableCling(Cling):
    def get_base_url(self):
        url = super(PrefixableCling, self).get_base_url()
        return url[len(settings.SITE_PREFIX) - 1:]

from django.core.wsgi import get_wsgi_application
application = PrefixableCling(get_wsgi_application())