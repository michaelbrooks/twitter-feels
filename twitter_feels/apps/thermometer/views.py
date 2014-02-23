from django.contrib.admin.views.decorators import staff_member_required
from django.template.loader import render_to_string
from django.views import generic
import tasks
# Create your views here.
from jsonview.decorators import json_view
from models import TimeFrame

class ThermometerView(generic.TemplateView):
    template_name = 'thermometer/main.html'

    def get_context_data(self, **kwargs):

        global_frames = TimeFrame.get_global_frames().order_by('start_time')

        frames = [{
            'time': f.start_time,
            'total': f.tweet_count
        } for f in global_frames]

        return {
            'frames': frames
        }


thermometer = ThermometerView.as_view()
