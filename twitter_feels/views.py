from django.views import generic
from twitter_feels.libs.streamer.models import get_streamer_status
from twitter_feels.apps.thermometer.tasks import get_thermometer_status
from django.template.loader import render_to_string
from django.contrib.admin.views.decorators import staff_member_required
from jsonview.decorators import json_view


@json_view
def json_status(request, data):
    """
    Returns a JSON representation of the status, with
    HTML conveniently included.
    """
    data['thermometer']['html'] = render_to_string('thermometer/status.html', data['thermometer'])

    data['streamer']['html'] = render_to_string('streamer/status.html', data['streamer'])
    del data['streamer']['processes']

    return data


class StatusView(generic.TemplateView):
    template_name = 'twitter_feels/status.html'

    def get(self, request, *args, **kwargs):
        status_data = {
            'thermometer': get_thermometer_status(),
            'streamer': get_streamer_status()
        }
        if request.is_ajax():
            return json_status(request, status_data)
        else:
            return self.render_to_response(status_data)


status = StatusView.as_view()


class HomeView(generic.TemplateView):
    template_name = 'twitter_feels/home.html'


home = HomeView.as_view()