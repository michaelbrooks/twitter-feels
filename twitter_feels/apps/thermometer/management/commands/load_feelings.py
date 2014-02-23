import logging
from logging.config import dictConfig
from os import path
from optparse import make_option
import csv

from django.core.management.base import BaseCommand
from datetime import timedelta
from django.utils import timezone

from ...models import FeelingWord



# Setup logging if not already configured

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
    Loads feelings from a feelings file into the database.
    """
    option_list = BaseCommand.option_list + (
        make_option(
            '--force',
            action='store_true',
            dest='force',
            default=False,
            help='Ignore existing feelings and insert anyway.'
        ),
        make_option(
            '--delimiter',
            action='store',
            dest='delimiter',
            default='\t',
            help='Delimiter for parsing the feelings file.'
        ),
        make_option(
            '--limit',
            action='store',
            dest='limit',
            default=None,
            type=int,
            help='Just load the first <limit> feelings from the file.'
        ),
    )
    args = '<feelings.txt>'
    help = "Parses the feelings file from We Feel Fine and adds feelings to the database."

    def handle(self, feelings_filename=None, *args, **options):

        try:

            force = options.get('force', False)
            delimiter = options.get('delimiter', '\t')
            limit = options.get('limit', None)

            if not feelings_filename:
                feelings_filename = path.join(path.dirname(__file__), 'feelings.txt')

            existing = FeelingWord.objects.count()
            if existing and not force:
                logger.error("Your database already contains %d FeelingWords! Use --force to ignore.", existing)
                return False

            logger.info("Loading feelings from %s...", feelings_filename)

            # parse the feelings file
            with open(feelings_filename, 'rb') as feelings_file:
                reader = csv.reader(feelings_file, delimiter=delimiter)
                next(reader, None) # skip the header

                feelings = []

                for row in reader:
                    word = row[0]
                    count = row[1]
                    color = row[2]

                    feelings.append(FeelingWord(word=word, color=color))

                    if limit and len(feelings) == limit:
                        break

                FeelingWord.objects.bulk_create(feelings)
                logger.info("Created %d feelings", len(feelings))

        except Exception as e:
            logger.error(e)
