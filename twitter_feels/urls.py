from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'twitter_feels.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', 'twitter_feels.views.home', name='home'),
    url(r'^status/', include('twitter_feels.apps.status.urls')),
    url(r'^thermometer/', include('twitter_feels.apps.thermometer.urls')),
    url(r'^map/', include('twitter_feels.apps.map.urls')),
    url(r'^fish/', include('twitter_feels.apps.fish.urls')),
    url(r'^admin/rq/', include('django_rq.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns('', url(r'^demo_vis/', include('twitter_feels.apps.demo_vis.urls')))
    import debug_toolbar
    urlpatterns += patterns('', url(r'^__debug__/', include(debug_toolbar.urls)))