from django.views import generic
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from jsonview.decorators import json_view

import tasks

# Create your views here.
class ThermometerView(generic.TemplateView):
    template_name= 'thermometer/main.html'

thermometer = ThermometerView.as_view()

@json_view
def scheduler_status(request):
    return {
        "status": tasks.scheduler_status()
    }


@staff_member_required
def start_scheduler(request):
    if request.method == 'POST':
        tasks.schedule_create_tasks()
    return scheduler_status(request)


@staff_member_required
def stop_scheduler(request):
    if request.method == 'POST':
        tasks.cancel_create_tasks()
    return scheduler_status(request)