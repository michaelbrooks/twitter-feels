from django.conf.urls import patterns, url

urlpatterns = patterns('twitter_feels.apps.map.views',
                       # The main page of your vis
                       url(r'^$', 'page_view', name='map'),
                       # A url where you can get json data for your vis
                       url(r'^data.json$', 'map_json', name='map_json')
)
