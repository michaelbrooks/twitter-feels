import logging
from logging.config import dictConfig

from django.core.management.base import BaseCommand
from datetime import timedelta
from django.utils import timezone


# Setup logging if not already configured
from ...tasks import cleanup

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
    Removes old tweets we no longer need.
    """

    help = "Removes tweets we no longer need."

    def handle(self, *args, **options):

        try:
            cleanup()
        except Exception as e:
            logger.error(e)
