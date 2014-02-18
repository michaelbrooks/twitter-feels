from datetime import datetime, timedelta
import logging
import redis
from collections import defaultdict
from django.utils import timezone

import django_rq
import rq

import settings
from twitter_feels.libs.streamer.models import Tweet, StreamProcess, FilterTerm


logger = logging.getLogger('status')
scheduler = django_rq.get_scheduler()


def schedule_task(key=None, cancel_first=True):
    """
    Schedule a task.
    If no key is given, schedules all configured tasks.
    """

    if not key:
        # First cancel any old jobs
        cancel_task()

        # start all the tasks
        scheduled = 0
        for key in settings.SCHEDULED_TASKS:
            # schedule recursively
            if schedule_task(key, cancel_first=False):
                scheduled += 1

        if scheduled != len(settings.SCHEDULED_TASKS):
            logger.warn("Could not schedule all the tasks")
            return False
        return True
    else:

        if cancel_first:
            # First cancel any old jobs
            cancel_task(key)

        # find the referenced task
        task = settings.SCHEDULED_TASKS[key]
        interval = task['interval']
        path = task['path']
        target = task['target']

        now = datetime.now()

        job = scheduler.schedule(
            scheduled_time=now,
            func=target,
            interval=interval,
        )

        job.meta['status.key'] = key
        job.save()

        logger.info("Scheduled task '%s' (%s) every %d seconds", key, path, interval)

        return True


def _task_status(key, jobs):
    if not key:

        # get task_status recursively
        result = dict((k, _task_status(key=k, jobs=jobs))
                      for k in settings.SCHEDULED_TASKS)

    else:
        task = settings.SCHEDULED_TASKS[key]

        result = {
            "key": key,
            "name": task['name'],
            "path": task['path'],
            "interval": task['interval'],
            "running": False,
            "enqueued_at": None
        }

        for job in jobs:
            if job.meta.get('status.key') == key:
                result["running"] = True
                result["enqueued_at"] = job.enqueued_at
                break

    return result


def _cancel_task(key, jobs):
    if not key:

        # cancel tasks recursively
        cancelled = sum((_cancel_task(key=k, jobs=jobs) for k in settings.SCHEDULED_TASKS), 0)

        if not cancelled:
            logger.info("No tasks to cancel")
        else:
            logger.info("Cancelled %d tasks", cancelled)
    else:
        cancelled = 0

        for job in jobs:

            if job.meta.get('status.key') == key:
                # it has the name we are looking for
                scheduler.cancel(job)
                job.delete()
                logger.info("Cancelled task '%s'", job.meta.get('status.key'))
                cancelled += 1

    return cancelled


def task_status(key=None):
    """
    Returns status if there is a scheduled task with the given key.
    If no key is given, returns a dictionary containing the status of all tasks.

    Status is a dictionary with the task info
    as well as keys "enqueued_at" (datetime) and "running" (True/False).
    """
    jobs = scheduler.get_jobs()
    return _task_status(key=key, jobs=jobs)


def cancel_task(key=None):
    """
    Cancels any scheduled task by key.
    If no key is provided, cancels all scheduled tasks
    (those created with this system).
    """

    jobs = scheduler.get_jobs()
    return _cancel_task(key=key, jobs=jobs)


def redis_running():
    try:
        scheduler.connection.ping()
        return True
    except redis.ConnectionError:
        return False


def scheduler_status():
    if scheduler.connection.exists(scheduler.scheduler_key) and \
            not scheduler.connection.hexists(scheduler.scheduler_key, 'death'):
        return True
    else:
        return False


def queues_status():
    queues = rq.Queue.all(connection=django_rq.get_connection())
    result = {}
    for q in queues:
        jobs = q.get_jobs()

        oldest = None
        state_count = defaultdict(int)
        func_count = defaultdict(int)

        for j in jobs:
            if j.status != 'finished' and (not oldest or j.created_at < oldest):
                oldest = j.created_at

            func_count[j.func_name] += 1
            state_count[j.status] += 1

        #TODO: Fix this nasty hack -- rq doesn't use UTC
        if oldest:
            oldest = timezone.make_aware(oldest, timezone.get_default_timezone())

        result[q.name] = {
            'name': q.name,
            'count': q.count,
            'oldest': oldest,
            'state_count': dict(state_count),
            'func_count': dict(func_count)
        }
    return result


def worker_status():
    workers = rq.Worker.all(connection=django_rq.get_connection())
    worker_data = []
    running = False
    for w in workers:
        if not w.stopped:
            running = True

        worker_data.append({
            'name': w.name,
            'state': w.state,
            'stopped': w.stopped,
            'queues': w.queue_names(),
        })

    result = {
        "workers": worker_data,
        "running": running
    }

    return result


def stream_status():
    terms = FilterTerm.objects.filter(enabled=True)
    processes = StreamProcess.get_current_stream_processes()
    running = False
    for p in processes:
        if p.status == StreamProcess.STREAM_STATUS_RUNNING:
            running = True
            break

    return {
        'running': running,
        'terms': [t.term for t in terms],
        'processes': processes,
        'tweet_count': Tweet.objects.count()
    }
