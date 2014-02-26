import logging
from logging.config import dictConfig
from optparse import make_option

from django.core.management.base import BaseCommand


# Setup logging if not already configured
from ...utils import backfill_tasks, AnalysisTask

logger = logging.getLogger('analysis')
if not logger.handlers:
    dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            "analysis": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
            },
        },
        "analysis": {
            "handlers": ["analysis"],
            "level": "DEBUG"
        }
    })


class Command(BaseCommand):
    """
    Fills in analysis frames for old tweets.
    """
    option_list = BaseCommand.option_list + (
        make_option(
            '--force',
            action='store_true',
            dest='force',
            default=False,
            help='Backfill even if analyses are not running.'
        ),
    )
    help = "Fills in analysis frames for old tweets, for any running analyses or specified key."
    args = "<task_key>"

    def handle(self, task_key=None, *args, **options):

        force = options.get('force', False)

        try:
            if not task_key:
                tasks = AnalysisTask.get()
                for task in tasks:
                    if force or task.get_rq_job():
                        backfill_tasks(task.key)
            else:
                task = AnalysisTask.get(key=task_key)
                if force or task.get_rq_job():
                    backfill_tasks(task.key)
                else:
                    logger.warn("Task %s is not running! Use --force to ignore.", task.name)
        except Exception as e:
            logger.error(e)
