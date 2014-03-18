from django.views import generic
from django.shortcuts import render
from models import TimeFrame, FeelingWord, FeelingPercent, ExampleTweet
from django.utils import timezone
from jsonview.decorators import json_view
import json
from itertools import groupby
import settings
import times
from collections import defaultdict

def get_all_feelings():
    # Get all of the feelings
    feelings = FeelingWord.get_tracked_list().order_by('id')
    feelings_json = []
    for f in feelings:
        feelings_json.append({
            'id': f.id,
            'word': f.word,
            'hidden': f.hidden
        })
    return feelings_json


def df(dt):
    """Format a datetime to something JS likes"""
    return 1000 * times.to_unix(dt)


def get_thermometer_data(selected_feeling_ids=[]):
    # The full range of the data
    normal_start = FeelingPercent.get_earliest_start_time()
    normal_end = FeelingPercent.get_latest_end_time()

    if normal_start is None:
        normal_start = timezone.now().replace(second=0, microsecond=0)
        normal_end = normal_start

    history_end = normal_end
    history_start = history_end - settings.HISTORICAL_INTERVAL

    recent_end = normal_end
    # add a little extra data to assist with smoothing
    recent_start = recent_end - settings.DISPLAY_INTERVAL

    # Get the time intervals we are dealing with
    intervals = {
        'normal': {
            'start': df(normal_start),
            'end': df(normal_end),
            'duration': (normal_end - normal_start).total_seconds(),
        },
        'historical': {
            'start': df(history_start),
            'end': df(history_end),
            'duration': settings.HISTORICAL_INTERVAL.total_seconds(),
        },
        'recent': {
            'start': df(recent_start),
            'end': df(recent_end),
            'duration': settings.DISPLAY_INTERVAL.total_seconds(),
            'frame_width': TimeFrame.DURATION.total_seconds(),
        },
    }

    # Get the overall statistics
    overall_frames = TimeFrame.get_in_range(start=recent_start, end=recent_end, calculated=True)
    overall_series = []
    for f in overall_frames:
        overall_series.append({
            'start_time': df(f.start_time),
            'feeling_rate': f.feeling_tweets,
            'total_rate': f.total_tweets,
            'missing_data': f.missing_data,
        })

    overall = {
        'normal': TimeFrame.get_average_rate(),
        'historical': TimeFrame.get_average_rate(start=history_start, end=history_end),
        'recent_series': overall_series,
    }

    if not selected_feeling_ids:
        selected_feeling_ids = FeelingPercent.get_top_feeling_ids(limit=settings.DEFAULT_FEELINGS)

    # Get the data for each selected feeling

    # Normal percents for each feeling
    normal_percents = FeelingPercent.get_average_percents(feeling_ids=selected_feeling_ids)

    # Historical percents for each feeling
    history_percents = FeelingPercent.get_average_percents(start=history_start, end=history_end,
                                                           feeling_ids=selected_feeling_ids)


    # Get a dictionary from feeling id -> list of examples for that feeling
    example_tweets = ExampleTweet.get_in_range(start=recent_start, end=recent_end, feeling_ids=selected_feeling_ids)
    examples_by_feeling = defaultdict(list)
    for feeling_id, feeling_group in groupby(example_tweets, lambda fr: fr.feeling_id):

        examples_for_feeling = []
        for i, ex in enumerate(feeling_group):
            examples_for_feeling.append({
                'tweet_id': ex.tweet_id,
                'text': ex.text,
                'user_id': ex.user_id,
                'user_screen_name': ex.user_screen_name,
                'user_name': ex.user_name,
                'created_at': df(ex.created_at),
                'frame_id': ex.frame_id
            })

        examples_by_feeling[feeling_id] = examples_for_feeling



    # Percent per minute for the past recent interval, ordered by feeling, time
    # This recent_start_smoothed compensates for eventual smoothing
    recent_start_smoothed = recent_start - settings.TIME_FRAME_DURATION * settings.SMOOTHING_WINDOW_SIZE
    feeling_percents = FeelingPercent.get_percents_in_interval(start=recent_start_smoothed, end=recent_end,
                                                               feeling_ids=selected_feeling_ids)

    # We'll fill this in according to the ordering of selected_feeling_ids
    selected_feelings = [None] * len(selected_feeling_ids)
    for feeling_id, feeling_group in groupby(feeling_percents, lambda fr: fr.feeling_id):

        # Holds the percent for each time point
        percents = []
        feeling_word = None
        feeling_color = None

        for i, fp in enumerate(feeling_group):

            if not feeling_word:
                feeling_word = fp.feeling.word
                feeling_color = fp.feeling.color

            percents.append({
                'frame_id': fp.frame_id,
                'start_time': df(fp.start_time),
                'percent': fp.percent,
                'missing_data': fp.missing_data,
            })

        position = selected_feeling_ids.index(feeling_id)
        selected_feelings[position] = {
            'feeling_id': feeling_id,
            'word': feeling_word,
            'color': feeling_color,
            'normal': normal_percents[feeling_id],
            'historical': history_percents[feeling_id],
            'recent_series': percents,
            'examples': examples_by_feeling[feeling_id]
        }

    return {
        'intervals': intervals,
        'overall': overall,
        'selected_feelings': selected_feelings,
    }


class ThermometerView(generic.TemplateView):
    template_name = 'thermometer/main.html'

    def get_context_data(self, **kwargs):
        return {
            'all_feelings': json.dumps(get_all_feelings()),
        }


thermometer = ThermometerView.as_view()


@json_view
def update_json(request):

    feelings = request.GET.get('feelings').split(',')
    feelings = [f for f in feelings if len(f)]

    return get_thermometer_data(feelings)


def update_html(request):
    data = get_thermometer_data()
    return render(request, 'thermometer/data.html', {
        'data_json': json.dumps(data, indent=3)
    })


@json_view
def feelings_json(request):
    return get_all_feelings()


def feelings_html(request):
    data = get_all_feelings()
    return render(request, 'thermometer/data.html', {
        'data_json': json.dumps(data, indent=3)
    })
