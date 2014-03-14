from django.conf.urls import patterns, url

urlpatterns = patterns('twitter_feels.apps.thermometer.views',
                       url(r'^$', 'thermometer', name='thermometer'),
                       url(r'^feelings.json', 'feelings_json', name='thermometer_feelings_json'),
                       url(r'^feelings.html', 'feelings_html', name='thermometer_feelings_html'),
                       url(r'^update.json$', 'update_json', name='thermometer_update_json'),
                       url(r'^update.html$', 'update_html', name='thermometer_update_html')
)
