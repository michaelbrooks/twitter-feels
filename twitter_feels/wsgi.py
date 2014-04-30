"""
WSGI config for twitter_feels project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os
import env_file

env_file.load()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "twitter_feels.settings")

# https://github.com/kennethreitz/dj-static
import dj_static
from django.conf import settings
from django.contrib.staticfiles.handlers import StaticFilesHandler as DebugHandler

class PrefixableDebugHandler(DebugHandler):
    def get_base_url(self):
        url = super(PrefixableDebugHandler, self).get_base_url()
        if url.startswith(settings.SITE_PREFIX):
            url = url[len(settings.SITE_PREFIX) - 1:]
        return url

    def get_response(self, request):
        if request.path.startswith(settings.SITE_PREFIX):
            request.path = request.path[len(settings.SITE_PREFIX) - 1:]
        return super(PrefixableDebugHandler, self).get_response(request)

class PrefixableCling(dj_static.Cling):
    """WSGI middleware that intercepts calls to the static files
    directory, as defined by the STATIC_URL setting, and serves those files.
    """

    def __init__(self, application, base_dir=None):
        super(PrefixableCling, self).__init__(application, base_dir=base_dir)
        try:
            self.debug_cling = PrefixableDebugHandler(application, base_dir=base_dir)
        except TypeError:
            self.debug_cling = PrefixableDebugHandler(application)

    def get_base_url(self):
        url = super(PrefixableCling, self).get_base_url()
        if url.startswith(settings.SITE_PREFIX):
            url = url[len(settings.SITE_PREFIX) - 1:]
        return url

from django.core.wsgi import get_wsgi_application
application = PrefixableCling(get_wsgi_application())
