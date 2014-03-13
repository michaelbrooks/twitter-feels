from django.conf.urls import patterns, url

urlpatterns = patterns('twitter_feels.apps.status.views',
                       url(r'^$', 'status', name='status'),
                       url(r'^get$', 'json_status', name='get_status'),
                       url(r'^get/(?P<task>[\w]+)$', 'json_status', name='get_task_status'),
                       url(r'^start/(?P<task>[\w]+)', 'start_task', name='start_task'),
                       url(r'^stop/(?P<task>[\w]+)', 'stop_task', name='stop_task'),
                       url(r'^clean', 'clean_tweets', name='status_clean_tweets'),
                       url(r'^requeue', 'requeue_failed', name='status_requeue_failed')
)
