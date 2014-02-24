from django.views import generic
from django.core.exceptions import ObjectDoesNotExist
from models import TimeFrame, FeelingWord
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
    try:
        normal_start = TimeFrame.get_earliest().start_time
        normal_end = TimeFrame.get_latest().end_time
    except ObjectDoesNotExist:
        normal_start = None
        normal_end = None
    normal_counts = TimeFrame.get_average_rates()

    # number of tweets per minute in the past historical interval
    history_end = timezone.now().replace(second=0, microsecond=0)
    history_start = history_end - settings.HISTORICAL_INTERVAL
    historical_counts = TimeFrame.get_average_rates(start=history_start)

    # number of tweets per minute for the past display interval
    display_end = history_end
    display_start = display_end - settings.DISPLAY_INTERVAL
    frames = TimeFrame.get_frames(start=display_start)
    frame_data = []
    for start_time, frame_group in groupby(frames, lambda fr: fr.start_time):

        group_feelings = []
        incomplete = False
        total = 0

        for fr in frame_group:
            group_feelings.append(fr.tweet_count)
            incomplete = fr.incomplete
            total += fr.tweet_count

        frame_data.append({
            'start_time': str(start_time),
            'feeling_counts': group_feelings,
            'total_count': total,
            'incomplete': incomplete
        })

    return {
        'frames': {
            'query_start': str(display_start),
            'query_end': str(display_end),
            'frame_duration': settings.TIME_FRAME_DURATION.total_seconds(),
            'data': frame_data,
            'notes': """A set of recent count frames of fixed duration.
            The order of entries in the 'feeling_counts' array in each data frame corresponds
            to ordering the feelings by id, with the NULL feelings entry at the front.
            The 'incomplete' value indicates whether more than 20% of the frame was empty."""
        },
        'normal': {
            'start': str(normal_start),
            'end': str(normal_end),
            'feeling_counts': normal_counts,
            'notes': """Gives the average counts over all available data.  The 'feeling_counts' correspond
            to the ordering of the feelings by id, with a NULL feelings entry at the front.
            Does not include incomplete frames in the average."""
        },
        'historical': {
            'start': str(history_start),
            'end': str(history_end),
            'interval': settings.HISTORICAL_INTERVAL.total_seconds(),
            'feeling_counts': historical_counts,
            'notes': """Gives average counts over a historical interval. The 'feeling_counts' correspond
            to the ordering of the feelings by id, with a NULL feelings entry at the front.
            Does not include incomplete frames in the average."""
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
