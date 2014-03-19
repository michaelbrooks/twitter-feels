from django.template import RequestContext
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.template.loader import render_to_string
from jsonview.decorators import json_view
from django.views import generic
from django.contrib.admin.views.decorators import staff_member_required

import models


def _render_to_string_request(request, template, dictionary):
    """
    Wrapper around render_to_string that includes the request context
    This is necessary to get all of the TEMPLATE_CONTEXT_PROCESSORS
    activated in the template.
    """
    context = RequestContext(request, dictionary)
    return render_to_string(template, context_instance=context)


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


status = staff_member_required(StatusView.as_view())


def _process_task_status(request, task_status):
    task_status['badge'] = _render_to_string_request(request, 'status/badge.html', {
        "running": task_status['running']
    })
    task_status['most_recent'] = naturaltime(task_status['most_recent'])

    return task_status


def _get_task_status_response_data(request, task):
    """
    Get JSON-ready response data for a single task status.
    """

    stat = models.task_status(key=task)

    # add rendered badges
    stat = _process_task_status(request, stat)

    return stat


def _process_streamer_status(request, streamer_status):
    return _render_to_string_request(request, 'status/streamer.html', {
        'streamer': streamer_status
    })


def _process_queues_status(request, queues_status):
    return _render_to_string_request(request, 'status/queues.html', {
        'queues': queues_status
    })


def _process_workers_status(request, workers_status):
    return _render_to_string_request(request, 'status/workers.html', {
        'workers': workers_status
    })


def _process_general_status(request, status):
    return _render_to_string_request(request, 'status/general.html', status)


@staff_member_required
@json_view
def json_status(request, task=None):
    """
    Returns a JSON representation of the status, with
    HTML conveniently included.
    """

    if task:
        return _get_task_status_response_data(request, task)
    else:
        # the whole deal
        data = _get_status_response_data()

        tasks = data['tasks']
        for task in tasks:
            tasks[task] = _process_task_status(request, tasks[task])

        data['streamer'] = _process_streamer_status(request, data['streamer'])
        data['queues'] = _process_queues_status(request, data['queues'])
        data['workers'] = _process_workers_status(request, data['workers'])
        data['general'] = _process_general_status(request, data)

        return data


@staff_member_required
@json_view
def start_task(request, task=None):
    if request.method == 'POST':
        models.schedule_task(key=task)
    return _get_task_status_response_data(request, task)


@staff_member_required
@json_view
def stop_task(request, task=None):
    if request.method == 'POST':
        models.cancel_task(key=task)
    return _get_task_status_response_data(request, task)

@staff_member_required
@json_view
def clean_tweets(request):
    if request.method == 'POST':
        models.clean_tweets()
    status = models.stream_status()
    return _process_streamer_status(request, status)

@staff_member_required
@json_view
def requeue_failed(request):
    if request.method == 'POST':
        models.requeue_failed()

    queue_status = models.queues_status()

    return _process_queues_status(request, queue_status)

@staff_member_required
@json_view
def clear_failed(request):
    if request.method == 'POST':
        models.clear_failed()

    queue_status = models.queues_status()

    return _process_queues_status(request, queue_status)