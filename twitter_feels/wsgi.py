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

class PrefixableCling(dj_static.Cling):
    """WSGI middleware that intercepts calls to the static files
    directory, as defined by the STATIC_URL setting, and serves those files.

    NOTE: Overriding the constructor to fix a bug
    """
    def __init__(self, application, base_dir=None):
        super(PrefixableCling, self).__init__(application, base_dir=base_dir)
        self.debug_cling = dj_static.DebugHandler(application, base_dir=base_dir)

    def get_base_url(self):
        url = super(PrefixableCling, self).get_base_url()
        return url[len(settings.SITE_PREFIX) - 1:]

from django.core.wsgi import get_wsgi_application
application = PrefixableCling(get_wsgi_application())
