from django.conf.urls import patterns, url

urlpatterns = patterns('twitter_feels.apps.map.views',
                       # The main page of your vis
                       url(r'^$', 'page_view', name='map'),
                       url(r'^query.html$', 'map_results_html', name='map_results_html'),
                       url(r'^fast_query.html$', 'fast_map_results_html', name='fast_map_results_html'),
                       url(r'^faster_query.html$', 'faster_map_results_html', name='faster_map_results_html'),
                       url(r'^query.json$', 'map_results_json', name='map_results_json'),
                       url(r'^fast_query.json$', 'fast_map_results_json', name='fast_map_results_json'),
                       url(r'^faster_query.json$', 'faster_map_results_json', name='faster_map_results_json'),
                       url(r'^example_tweet.html', 'example_tweet_html', name='map_example_tweet_html'),
                       url(r'^example_tweet.json$', 'example_tweet_json', name='map_example_tweet_json'),
)
