import logging
from collections import defaultdict

import redis
from django.utils import timezone
from django.db import models
import django_rq
import rq, rq.queue, rq.job, rq.exceptions

from stream_analysis import AnalysisTask, cleanup, get_stream_cutoff_times
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

            job_type = j.func_name

            if job_type.endswith('create_frames'):
                if 'analysis.task.key' in j.meta:
                    job_type = "create_frames[%s]" % j.meta.get('analysis.task.key', '?')
                else:
                    job_type = j.get_call_string().replace('stream_analysis.utils.', 'scheduler:')
            elif job_type.endswith('analyze_frame'):
                if 'analysis.task.key' in j.meta:
                    job_type = "analyze_frame[%s]" % j.meta.get('analysis.task.key', '?')
                else:
                    job_type = j.get_call_string()
            else:
                job_type = j.get_call_string()

            func_count[job_type] += 1
            state_count[j.status] += 1

        #TODO: Fix this nasty hack -- rq doesn't use UTC
        if oldest:
            oldest = timezone.make_aware(oldest, timezone.get_default_timezone())

        func_count = sorted(func_count.items())

        result[q.name] = {
            'name': q.name,
            'count': q.count,
            'oldest': oldest,
            'state_count': dict(state_count),
            'func_count': func_count
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

    stream_class_memory_cutoffs = get_stream_cutoff_times()

    tweet_count = Tweet.objects.count()
    analyzed_count = None
    for stream_class, cutoff_time in stream_class_memory_cutoffs.iteritems():
        if stream_class == TweetStream:
            analyzed_count = TweetStream().count_before(cutoff_time)

    stream = TweetStream()
    earliest_time = stream.get_earliest_stream_time()
    latest_time = stream.get_latest_stream_time()

    avg_rate = None
    if earliest_time is not None and latest_time is not None:
        avg_rate = float(tweet_count) / (latest_time - earliest_time).total_seconds()

    return {
        'running': running,
        'terms': [t.term for t in terms],
        'processes': processes,
        'tweet_count': tweet_count,
        'analyzed_count': analyzed_count,
        'earliest': earliest_time,
        'latest': latest_time,
        'avg_rate': avg_rate
    }


def _task_status(task):
    frame_class = task.get_frame_class()

    stats = frame_class.get_performance_stats()

    most_recent = frame_class.objects\
        .filter(calculated=True)\
        .aggregate(latest_start_time=models.Max('start_time'))
    most_recent = most_recent['latest_start_time']

    result = {
        "key": task.key,
        "name": task.name,
        "time_frame_path": task.frame_class_path,
        "duration": frame_class.DURATION.total_seconds(),
        "frame_count": frame_class.count_completed(),
        "avg_analysis_time": stats['analysis_time'],
        "avg_cleanup_time": stats['cleanup_time'],
        "running": False,
        "most_recent": most_recent,
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

        # Delete jobs for this task
        task_key = job.meta.get('analysis.task.key')
        if task_key:
            task = AnalysisTask.get(task_key)
            frame_id = job.meta.get('analysis.frame.id')
            if task and frame_id:
                # Delete the corresponding frame
                frame_class = task.get_frame_class()
                try:
                    frame_class.objects.filter(pk=frame_id, calculated=False).delete()
                except Exception as e:
                    logger.warn(e, exc_info=True)

        job.cancel()
        cleared += 1

    logger.info("Cleared %d failed jobs", cleared)

    return cleared


def clean_tweets():
    """Clean old tweets we don't need anymore."""
    cleanup.delay()
