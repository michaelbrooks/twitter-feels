from django.views import generic
from models import TimeFrame, FeelingWord, FeelingPercent
from django.utils import timezone
from jsonview.decorators import json_view
import json
from itertools import groupby
import settings


def get_thermometer_data():
    # the feelings
    feelings = FeelingWord.get_tracked_list().order_by('id')
    feelings_data = []
    for f in feelings:
        feelings_data.append({
            'id': f.id,
            'word': f.word,
            'color': f.color,
            'hidden': f.hidden
        })

    # normal number of tweets per minute over all time
    effective_now = timezone.now()
    normal_start = FeelingPercent.get_earliest_start_time()
    normal_end = FeelingPercent.get_latest_end_time()
    if normal_end:
        effective_now = normal_end

    normal_percents = FeelingPercent.get_average_rates()

    # number of tweets per minute in the past historical interval
    history_end = effective_now.replace(second=0, microsecond=0)
    history_start = history_end - settings.HISTORICAL_INTERVAL
    history_percents = FeelingPercent.get_average_rates(start=history_start)

    # number of tweets per minute for the past display interval
    display_end = history_end
    # add a little extra data to assist with smoothing
    display_start = display_end - (settings.DISPLAY_INTERVAL + settings.TIME_FRAME_DURATION * 10)

    feeling_percents = FeelingPercent.get_in_range(start=display_start)
    feeling_data = []
    for start_time, time_group in groupby(feeling_percents, lambda fr: fr.start_time):

        group_feelings = []
        missing_data = False
        total = 0

        for i, fp in enumerate(time_group):
            if i == 0:
                # only do this once - it is the same for every feeling
                missing_data = fp.missing_data
                total = fp.feeling_tweets

            group_feelings.append(fp.percent)

        feeling_data.append({
            'start_time': str(start_time),
            'feeling_percents': group_feelings,
            'total_count': total,
            'missing_data': missing_data
        })

    return {
        'recent': {
            'query_start': str(display_start),
            'query_end': str(display_end),
            'frame_duration': settings.TIME_FRAME_DURATION.total_seconds(),
            'frames': feeling_data,
            'notes': """A set of recent frames of fixed duration.
            The order of entries in the 'feeling_percents' array in each frame corresponds
            to ordering the feelings by id.
            The 'missing_data' value indicates whether more than 20% of the frame was empty."""
        },
        'normal': {
            'start': str(normal_start),
            'end': str(normal_end),
            'feeling_percents': normal_percents,
            'notes': """Gives the average percent of each feeling over
             all available data.  The 'feeling_percents' correspond to the ordering of the feelings by id.
             Does not include frames with missing data in the average."""
        },
        'historical': {
            'start': str(history_start),
            'end': str(history_end),
            'interval': settings.HISTORICAL_INTERVAL.total_seconds(),
            'feeling_percents': history_percents,
            'notes': """Gives average percent of each feeling over
             a historical interval. The 'feeling_percents' correspond to the ordering of the feelings by id.
             Does not include frames with missing data in the average."""
        },
        'feelings': feelings_data
    }


class ThermometerView(generic.TemplateView):
    template_name = 'thermometer/main.html'

    def get_context_data(self, **kwargs):
        data = get_thermometer_data()
        return {
            'json_data': json.dumps(data),
            'data': data
        }


thermometer = ThermometerView.as_view()


@json_view
def thermometer_json(request):
    return get_thermometer_data()
