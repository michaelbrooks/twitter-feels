"""
WSGI config for twitter_feels project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os

def read_env(envFile='.env'):
    try:
        with open(envFile) as f:
            content = f.read()
    except IOError:
        content = ''

    import re
    for line in content.splitlines():
        m1 = re.match(r'\A([A-Za-z_0-9]+)=(.*)\Z', line)
        if m1:
            key, val = m1.group(1), m1.group(2)

            m2 = re.match(r"\A'(.*)'\Z", val)
            if m2:
                val = m2.group(1)

            m3 = re.match(r'\A"(.*)"\Z', val)
            if m3:
                val = re.sub(r'\\(.)', r'\1', m3.group(1))

            os.environ.setdefault(key, val)

read_env()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "twitter_feels.settings")

# https://github.com/kennethreitz/dj-static
from dj_static import Cling

from django.conf import settings

class PrefixableCling(Cling):
    def get_base_url(self):
        url = super(PrefixableCling, self).get_base_url()
        return url[len(settings.SITE_PREFIX) - 1:]

from django.core.wsgi import get_wsgi_application
application = PrefixableCling(get_wsgi_application())
