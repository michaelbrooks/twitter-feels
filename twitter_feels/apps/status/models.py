import logging
from collections import defaultdict

import redis
from django.utils import timezone
import django_rq
import rq, rq.queue, rq.job, rq.exceptions

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
        if t.get_frame_class().STREAM_CLASS == TweetStream:
            num_tweet_tasks += 1

    analyzed_count = TweetStream().count_analyzed(num_analyses=num_tweet_tasks)

    return {
        'running': running,
        'terms': [t.term for t in terms],
        'processes': processes,
        'tweet_count': Tweet.objects.count(),
        'analyzed_count': analyzed_count
    }


def _task_status(task):
    frame_class = task.get_frame_class()
    result = {
        "key": task.key,
        "name": task.name,
        "time_frame_path": task.frame_class_path,
        "duration": frame_class.DURATION.total_seconds(),
        "frame_count": frame_class.count_completed(),
        "avg_time": frame_class.get_average_analysis_time(),
        "running": False,
        "most_recent": frame_class.get_latest_end_time()
    }

    job = task.get_rq_job()
    if job:
        result["running"] = True

    return result


def task_status(key=None):
    """
    Returns status if there is a scheduled task with the given key.
    If no key is given, returns a dictionary containing the status of all tasks.

    Status is a dictionary with the task info
    as well as "running" (True/False).
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


def requeue_failed():
    """Requeue jobs in the failed queue."""
    connection = django_rq.get_connection()
    failed_queue = rq.queue.get_failed_queue(connection)
    job_ids = failed_queue.job_ids

    requeued = 0
    for job_id in job_ids:

        try:
            job = rq.job.Job.fetch(job_id, connection=connection)
        except rq.job.NoSuchJobError:
            # Silently ignore/remove this job and return (i.e. do nothing)
            failed_queue.remove(job_id)
            continue

        if job.status == rq.job.Status.FAILED:
            failed_queue.requeue(job_id)
            requeued += 1
        else:
            failed_queue.remove(job_id)

    logger.info("Requeued %d failed jobs", requeued)

    return requeued


def clear_failed():
    """Clear jobs in the failed queue."""
    connection = django_rq.get_connection()
    failed_queue = rq.queue.get_failed_queue(connection)
    job_ids = failed_queue.job_ids

    cleared = 0
    for job_id in job_ids:

        try:
            job = rq.job.Job.fetch(job_id, connection=connection)
        except rq.job.NoSuchJobError:
            # Silently ignore/remove this job and return (i.e. do nothing)
            failed_queue.remove(job_id)
            continue

        job.cancel()
        cleared += 1

    logger.info("Cleared %d failed jobs", cleared)

    return cleared


def clean_tweets():
    """Clean old tweets we don't need anymore."""
    cleanup.delay()