from django.contrib.admin.views.decorators import staff_member_required
from django.template.loader import render_to_string
from django.views import generic
import tasks
# Create your views here.
from jsonview.decorators import json_view


class ThermometerView(generic.TemplateView):
    template_name = 'thermometer/main.html'


thermometer = ThermometerView.as_view()
