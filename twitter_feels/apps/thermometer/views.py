from django.views import generic
from django.shortcuts import render
from models import TimeFrame, FeelingWord, FeelingPercent
from django.utils import timezone
from jsonview.decorators import json_view
import json
from itertools import groupby
import settings

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

def get_thermometer_data(selected_feeling_ids=None):


    # The full range of the data
    normal_start = FeelingPercent.get_earliest_start_time()
    normal_end = FeelingPercent.get_latest_end_time()

    # normal number of tweets per minute over all time
    effective_now = timezone.now().replace(second=0, microsecond=0)
    if normal_end:
        effective_now = normal_end

    history_end = effective_now
    history_start = history_end - settings.HISTORICAL_INTERVAL

    display_end = history_end
    # add a little extra data to assist with smoothing
    display_start = display_end - (
    settings.DISPLAY_INTERVAL + settings.TIME_FRAME_DURATION * settings.SMOOTHING_WINDOW_SIZE)

    # Get the time intervals we are dealing with
    intervals = {
        'normal': {
            'start': str(normal_start),
            'end': str(normal_end),
            'duration': (normal_end - normal_start).total_seconds(),
        },
        'historical': {
            'start': str(history_start),
            'end': str(history_end),
            'duration': settings.HISTORICAL_INTERVAL.total_seconds(),
        },
        'display': {
            'start': str(display_start),
            'end': str(display_end),
            'duration': settings.DISPLAY_INTERVAL.total_seconds(),
        },
    }

    # Get the overall statistics
    overall_frames = TimeFrame.get_in_range(start=display_start, end=display_end, calculated=True)
    overall_series = []
    for f in overall_frames:
        overall_series.append({
            'start_time': str(f.start_time),
            'feeling_rate': f.feeling_tweets,
            'total_rate': f.total_tweets,
            'missing_data': f.missing_data,
        })

    overall = {
        'normal': TimeFrame.get_average_rate(),
        'historical': TimeFrame.get_average_rate(start=history_start, end=history_end),
        'display_series': overall_series,
    }

    if selected_feeling_ids is None:
        selected_feeling_ids = FeelingPercent.get_top_feeling_ids(limit=settings.DEFAULT_FEELINGS)

    print selected_feeling_ids

    # Get the data for each selected feeling

    # Normal percents for each feeling
    normal_percents = FeelingPercent.get_average_percents(feeling_ids=selected_feeling_ids)

    # Historical percents for each feeling
    history_percents = FeelingPercent.get_average_percents(start=history_start, end=history_end,
                                                           feeling_ids=selected_feeling_ids)

    # Percent per minute for the past display interval, ordered by feeling, time
    feeling_percents = FeelingPercent.get_percents_in_interval(start=display_start, end=display_end,
                                                               feeling_ids=selected_feeling_ids)

    feeling_data = []
    for feeling_id, feeling_group in groupby(feeling_percents, lambda fr: fr.feeling_id):

        # Holds the percent for each time point
        percents = []

        for i, fp in enumerate(feeling_group):
            percents.append({
                'start_time': str(fp.start_time),
                'percent': fp.percent,
            })

        feeling_data.append({
            'feeling_id': feeling_id,
            'normal': normal_percents[feeling_id],
            'historical': history_percents[feeling_id],
            'display_series': percents,
        })

    return {
        'intervals': intervals,
        'overall': overall,
        'selected_feelings': feeling_data,
    }


class ThermometerView(generic.TemplateView):
    template_name = 'thermometer/main.html'

    def get_context_data(self, **kwargs):
        return {
            'all_feelings': json.dumps(get_all_feelings()),
        }


thermometer = ThermometerView.as_view()


@json_view
def thermometer_json(request):
    return get_thermometer_data()


def thermometer_data(request):
    data = get_thermometer_data()
    return render(request, 'thermometer/data.html', {
        'data_json': json.dumps(data, indent=3)
    })