from django.contrib.humanize.templatetags.humanize import naturaltime
from django.template.loader import render_to_string
from jsonview.decorators import json_view
from django.views import generic
from django.contrib.admin.views.decorators import staff_member_required

import models


def _get_status_response_data():
    data = {
        'tasks': {},
        'streamer': {},
        'scheduler': {},
        'workers': {},
        'queues': {},
        'redis': models.redis_running()
    }

    if data['redis']:
        data['tasks'] = models.task_status()
        data['scheduler'] = models.scheduler_status()
        data['workers'] = models.worker_status()
        data['streamer'] = models.stream_status()
        data['queues'] = models.queues_status()

    return data


class StatusView(generic.TemplateView):
    template_name = 'status/page.html'

    def get_context_data(self, **kwargs):
        return _get_status_response_data()


status = StatusView.as_view()


def _process_task_status(task_status):
    task_status['badge'] = render_to_string('status/badge.html', {
        "running": task_status['running']
    })
    task_status['enqueued_at'] = naturaltime(task_status['enqueued_at'])

    return task_status


def _get_task_status_response_data(task):
    """
    Get JSON-ready response data for a single task status.
    """

    status = models.task_status(key=task)

    # add rendered badges
    status = _process_task_status(status)

    return status


def _process_streamer_status(streamer_status):
    return render_to_string('status/streamer.html', {
        'streamer': streamer_status
    })

def _process_queues_status(queues_status):
    return render_to_string('status/queues.html', {
        'queues': queues_status
    })

def _process_workers_status(workers_status):
    return render_to_string('status/workers.html', {
        'workers': workers_status
    })

def _process_general_status(status):
    return render_to_string('status/general.html', status)

@json_view
def json_status(request, task=None):
    """
    Returns a JSON representation of the status, with
    HTML conveniently included.
    """

    if task:
        return _get_task_status_response_data(task)
    else:
        # the whole deal
        data = _get_status_response_data()

        tasks = data['tasks']
        for task in tasks:
            tasks[task] = _process_task_status(tasks[task])

        data['streamer'] = _process_streamer_status(data['streamer'])
        data['queues'] = _process_queues_status(data['queues'])
        data['workers'] = _process_workers_status(data['workers'])
        data['general'] = _process_general_status(data)

        return data

@staff_member_required
@json_view
def start_task(request, task=None):
    if request.method == 'POST':
        models.schedule_task(key=task)
    return _get_task_status_response_data(task)


@staff_member_required
@json_view
def stop_task(request, task=None):
    if request.method == 'POST':
        models.cancel_task(key=task)
    return _get_task_status_response_data(task)
