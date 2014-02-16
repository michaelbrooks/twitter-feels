from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'twitter_feels.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^thermometer/', include('twitter_feels.apps.thermometer.urls')),
    url(r'^admin/rq/', include('django_rq.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
