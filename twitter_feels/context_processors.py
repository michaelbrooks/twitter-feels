"""
Defines a context processor that detects the current site.
"""
from django.conf import settings
from django.contrib.sites.models import Site


def current_site(request):
    """
    A context processor to add the current site to the Context
    """
    try:
        site = Site.objects.get_current()
        return {
            'site': site,
        }
    except Site.DoesNotExist:
        # always return a dict, no matter what!
        return {'site': ''} # an empty string


def debug_mode(request):
    """
    Adds a "debug_mode" setting to the context.
    """
    return {
        'debug_mode': settings.DEBUG
    }

def external_urls(request):
    """
    Adds an external_urls dict to the context.
    """
    return {
        'external_urls': getattr(settings, 'EXTERNAL_URLS', {})
    }