from django.conf.urls import patterns, url

urlpatterns = patterns('twitter_feels.apps.thermometer.views',
                       url(r'^$', 'thermometer', name='thermometer'),
                       url(r'^status$', 'scheduler_status', name='thermometer_status'),
                       url(r'^start$', 'start_scheduler', name='thermometer_start'),
                       url(r'^stop$', 'stop_scheduler', name='thermometer_stop'),
)
