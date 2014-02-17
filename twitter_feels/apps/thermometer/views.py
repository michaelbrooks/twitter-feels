from django.contrib.admin.views.decorators import staff_member_required
from django.template.loader import render_to_string
from django.views import generic
import tasks
# Create your views here.
from jsonview.decorators import json_view


class ThermometerView(generic.TemplateView):
    template_name = 'thermometer/main.html'


thermometer = ThermometerView.as_view()


@json_view
def current_status(request):
    # add some rendered stuff so we don't have to do it on the client
    response = tasks.get_thermometer_status()
    response['html'] = render_to_string('thermometer/status.html', response)
    return response


@staff_member_required
def start_scheduler(request):
    if request.method == 'POST':
        tasks.schedule_create_tasks()
    return current_status(request)


@staff_member_required
def stop_scheduler(request):
    if request.method == 'POST':
        tasks.cancel_create_tasks()
    return current_status(request)