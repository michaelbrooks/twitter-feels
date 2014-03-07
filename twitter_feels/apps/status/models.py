import logging
from collections import defaultdict

import redis
from django.utils import timezone
import django_rq
import rq

from stream_analysis import AnalysisTask, cleanup
from twitter_stream.models import Tweet, StreamProcess, FilterTerm
from twitter_feels.libs.twitter_analysis.models import TweetStream

logger = logging.getLogger('status')
scheduler = django_rq.get_scheduler()


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

    tasks = AnalysisTask.get()
    num_tweet_tasks = 0
    for t in tasks:
        if t.STREAM_CLASS == TweetStream:
            num_tweet_tasks += 1
    analyzed_count = TweetStream.count_analyzed(num_analyses=num_tweet_tasks)

    return {
        'running': running,
        'terms': [t.term for t in terms],
        'processes': processes,
        'tweet_count': Tweet.objects.count(),
        'analyzed_count': analyzed_count
    }


def _task_status(task):
    result = {
        "key": task.key,
        "name": task.name,
        "time_frame_path": task.frame_class_path,
        "duration": task.frame_class.DURATION.total_seconds(),
        "frame_count": task.frame_class.count_completed(),
        "avg_time": task.frame_class.get_average_analysis_time(),
        "running": False,
        "enqueued_at": None
    }

    job = task.get_rq_job()
    if job:
        result["running"] = True
        result["enqueued_at"] = job.enqueued_at

    return result


def task_status(key=None):
    """
    Returns status if there is a scheduled task with the given key.
    If no key is given, returns a dictionary containing the status of all tasks.

    Status is a dictionary with the task info
    as well as keys "enqueued_at" (datetime) and "running" (True/False).
    """
    if key:
        task = AnalysisTask.get(key=key)
        if task:
            return _task_status(task)
    else:
        tasks = AnalysisTask.get()
        result = dict()
        for task in tasks:
            result[task.key] = _task_status(task)
        return result


def cancel_task(key=None):
    """
    Cancels any scheduled task by key.
    If no key is provided, cancels all scheduled tasks
    (those created with this system).
    """
    if key:
        task = AnalysisTask.get(key=key)
        if task:
            task.cancel()
    else:
        for task in AnalysisTask.get():
            task.cancel()


def schedule_task(key=None, cancel_first=True):
    """
    Schedule a task.
    If no key is given, schedules all configured tasks.
    """
    if key:
        task = AnalysisTask.get(key=key)
        if task:
            task.schedule(cancel_first=cancel_first)
    else:
        for task in AnalysisTask.get():
            task.schedule(cancel_first=cancel_first)


def clean_tweets():
    """Clean old tweets we don't need anymore."""
    cleanup.delay()