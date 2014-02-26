from django.views import generic
from jsonview.decorators import json_view
from django.utils import timezone
from datetime import timedelta
import times
import models


class DemoView(generic.TemplateView):
    template_name = 'demo_vis/page.html'


page_view = DemoView.as_view()


@json_view
def demo_vis_json(request):
    # Load the 20 most recent frames
    frames = models.DemoTimeFrame.get_most_recent(limit=20)

    result = []
    for frame in frames:
        # The @json_view decorator can only automatically
        # serialize certain Pyton data types -- it can't handle datetimes.
        # Convert to strings or unix timestamps as here.
        unixtime = times.to_unix(frame.start_time)
        result.append((unixtime, frame.tweet_count))

    return result