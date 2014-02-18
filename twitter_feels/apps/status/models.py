from datetime import datetime, timedelta
import logging
import redis
import django_rq

import settings


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