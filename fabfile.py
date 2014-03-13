import os

from fabric.api import local
from fabric.context_managers import lcd
from fabric import utils

root_dir = os.path.dirname(os.path.realpath(__file__))

def _supervisor(command, *args):
    with lcd(root_dir):
        if args:
            local('supervisorctl %s %s' % (command, ' '.join(args)))
        elif command == 'status':
            local('supervisorctl %s' % command)
        else:
            local('supervisorctl %s all' % command)

def stop(*args):
    """Stop one or more supervisor processes"""
    _supervisor('stop', *args)

def start(*args):
    """Start one or more supervisor processes"""
    _supervisor('start', *args)

def restart(*args):
    """Restart one or more supervisor processes"""
    _supervisor('restart', *args)

def status(*args):
    """Get the status of one or more supervisor processes"""
    _supervisor('status', *args)

def refresh_web():
    """Trigger's Gunicorn's 'hot refresh' feature."""
    with lcd(root_dir):
        pid = local('supervisorctl pid web', capture=True)
        local('kill -HUP %s' % pid)

def clear_logs():
    """Empties the log files"""
    with lcd(root_dir):
        local('echo "" | tee logs/*.log > /dev/null')

def watch(process):
    """Watch the log output from a process using tail -f."""
    with lcd(root_dir):
        local('tail -f logs/%s.log -s 0.5' % process)


def pip_refresh(file='requirements/dev.txt'):
    """Refresh pip from the requirements file"""
    with lcd(root_dir):
        local('pip install -r %s' % file)

def syncdb():
    """Shortcut for honcho run manage.py syncdb"""
    with lcd(root_dir):
        local('honcho run ./manage.py syncdb')

def dev_web():
    """Runs the Django development webserver"""

    # Stop the gunicorn process
    stop('web')

    with lcd(root_dir):
        local('honcho run ./manage.py runserver')

def dump_key(file='.twitter_api_key.json'):
    """Dump a Twitter API key to a fixture file (defaults to .twitter_api_key.json)"""
    with lcd(root_dir):
        local('honcho run ./manage.py dumpdata twitter_stream.ApiKey --indent=3 > %s' % file)

def load_key(file='.twitter_api_key.json'):
    """Load a Twitter API key from a previously-exported fixture (defaults to .twitter_api_key.json)"""
    with lcd(root_dir):

        # Make sure it is a legit key file
        try:
            with open(file, 'rb') as jsonfile:
                if not 'twitter_stream.apikey' in jsonfile.read():
                    utils.abort('File %s does not contain an Api Key' % file)
        except IOError, e:
            utils.abort('Cannot read file %s: %s' % (file, e))

        local('honcho run ./manage.py loaddata %s' % file)

        restart('stream')
