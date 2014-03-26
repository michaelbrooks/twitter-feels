import sys
from optparse import make_option

from django.core.management.base import BaseCommand
from django.contrib.humanize.templatetags.humanize import naturaltime

from datetime import timedelta, datetime
from django.utils import timezone
from twitter_feels.apps.map.models import TreeNode, TweetChunk
from twitter_feels.apps.map import settings


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is one of "yes" or "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' " \
                             "(or 'y' or 'n').\n")


class Command(BaseCommand):
    """
    Loads feelings from a feelings file into the database.
    """
    option_list = BaseCommand.option_list + (
        make_option(
            '--batch-size',
            action='store',
            dest='batch_size',
            default='10000',
            help='Amount of data to delete at once'
        ),
    )
    help = "Deletes old nodes and chunks from the map tables."

    def handle(self, *args, **options):

        batch_size = int(options.get('batch_size', 10000))

        TweetChunk.cleanup(batch_size=batch_size, reset=True)
        TreeNode.cleanup(batch_size=batch_size, reset=True)

