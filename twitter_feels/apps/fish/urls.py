from django.conf.urls import patterns, url

urlpatterns = patterns('twitter_feels.apps.fish.views',
                       # The main page of your vis
                       url(r'^$', 'page_view', name='fish')
)
