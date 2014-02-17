"""
Defines a context processor that detects the current site.
"""

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