from django.conf.urls import patterns, url

urlpatterns = patterns('twitter_feels.apps.thermometer.views',
                       url(r'^$', 'thermometer', name='thermometer'),
                       url(r'^data.json$', 'thermometer_json', name='thermometer_json')
)
