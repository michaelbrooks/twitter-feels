from django.contrib.humanize.templatetags.humanize import naturaltime
from django.template.loader import render_to_string
from jsonview.decorators import json_view
from django.views import generic
from django.contrib.admin.views.decorators import staff_member_required

import models


class StatusView(generic.TemplateView):
    template_name = 'status/page.html'

    def get_context_data(self, **kwargs):
        context = {
            'status': {},
            'redis': models.redis_running()
        }
        if context['redis']:
            context['status'] = models.task_status()

        return context


status = StatusView.as_view()

def _process_task_status(status):
    status['badge'] = render_to_string('status/badge.html', {
        "status": status
    })
    status['enqueued_at'] = naturaltime(status['enqueued_at'])


def _get_status_response_data(task=None):
    status = models.task_status(key=task)

    # add rendered badges
    if task:
        _process_task_status(status)
    else:
        for task_status in status.values():
            _process_task_status(task_status)

    return status

@json_view
def json_status(request, task=None):
    """
    Returns a JSON representation of the status, with
    HTML conveniently included.
    """

    return _get_status_response_data(task);


@staff_member_required
@json_view
def start_task(request, task=None):
    if request.method == 'POST':
        models.schedule_task(key=task)
    return _get_status_response_data(task)


@staff_member_required
@json_view
def stop_task(request, task=None):
    if request.method == 'POST':
        models.cancel_task(key=task)
    return _get_status_response_data(task)
