from django.conf.urls import patterns, url

urlpatterns = patterns('twitter_feels.apps.demo_vis.views',
                       # The main page of your vis
                       url(r'^$', 'page_view', name='demo_vis'),
                       # A url where you can get json data for your vis
                       url(r'^data.json$', 'demo_vis_json', name='demo_vis_json')
)
