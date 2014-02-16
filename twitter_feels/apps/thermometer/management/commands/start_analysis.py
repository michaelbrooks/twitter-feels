import logging
from logging.config import dictConfig

from django.core.management.base import BaseCommand
from datetime import timedelta
from django.utils import timezone


# Setup logging if not already configured
from ...tasks import schedule_create_tasks

logger = logging.getLogger('thermometer')
if not logger.handlers:
    dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            "thermometer": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
            },
        },
        "thermometer": {
            "handlers": ["thermometer"],
            "level": "DEBUG"
        }
    })


class Command(BaseCommand):
    """
    Starts the thermometer analysis cycle.
    """

    help = "Starts the thermometer analysis cycle."

    def handle(self, *args, **options):

        try:
            schedule_create_tasks()
        except Exception as e:
            logger.error(e)
