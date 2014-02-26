import logging
from logging.config import dictConfig

from django.core.management.base import BaseCommand


# Setup logging if not already configured
from ...utils import cleanup

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
    Removes old tweets we no longer need.
    """

    help = "Removes tweets we no longer need."

    def handle(self, *args, **options):

        try:
            cleanup()
        except Exception as e:
            logger.error(e)
