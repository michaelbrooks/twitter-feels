import os
import sys

from fabric.api import local
from fabric.context_managers import lcd, hide
from fabric.state import env
from fabric import utils
import time

root_dir = os.path.dirname(os.path.realpath(__file__))


def _supervisor(command, *args, **kwargs):
    capture = kwargs.get('capture', False)
    with lcd(root_dir):
        if args:
            local('supervisorctl %s %s' % (command, ' '.join(args)), capture=capture)
        elif command == 'status':
            local('supervisorctl %s' % command, capture=capture)
        else:
            local('supervisorctl %s all' % command, capture=capture)


def _jinja_render(template_path, values):
    """Render a template. Expects path relative to root_dir."""
    from jinja2 import Template, Environment, FileSystemLoader
    environment = Environment(loader=FileSystemLoader(root_dir))

    template = environment.get_template(template_path)
    return template.render(values)


def _read_env():
    sys.path.append(root_dir)
    from twitter_feels import env_file
    return env_file.read()


def run(process):
    """Run a process from the Procfile directly (not through supervisor)."""

    _supervisor('stop', process, capture=True)

    with lcd(root_dir):
        local('honcho start %s' % process)


def manage(*args):
    """Run manage.py with the given arguments"""
    with lcd(root_dir):
        local('honcho run ./manage.py %s' % (' '.join(args)))


def dev_web():
    """Runs the Django development webserver"""

    # Stop the gunicorn process
    stop('web')

    env = _read_env()

    manage('runserver', env.get('PORT', ''))

def rq_dashboard():
    """Starts the RQ Dashboard webserver"""

    # Stop the web process
    stop('web')

    env = _read_env()

    with lcd(root_dir):
        local('rq-dashboard -p %s -u %s' % (env.get('PORT', '9181'), env.get('REDIS_URL', 'redis://localhost:6379')))

def jasmine():
    """Run the jasmine test server. Stops the web process first to open the port."""
    stop('web')

    env = _read_env()

    with lcd(root_dir):
        local('jasmine -p %s' % env.get('PORT', ''))

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


def scale_worker(number):
    """Scale the workers to the given number of processes."""
    with lcd(root_dir):
        local(
            r'sed -i -r -e "/^\[program:%(process)s\]/ { n ; s/^numprocs=[[:digit:]]+/numprocs=%(number)s/ }" supervisord.conf' % {
                'process': 'worker',
                'number': number
            })
        _supervisor('update')


def refresh_web():
    """Trigger's Gunicorn's 'hot refresh' feature."""
    with lcd(root_dir):
        pid = local('supervisorctl pid web', capture=True)
        local('kill -HUP %s' % pid)


def count_web():
    """Get the current gunicorn web worker count"""
    with lcd(root_dir):
        with hide('running'):
            count = int(local('ps -C gunicorn --no-headers | wc -l', capture=True))

        if count > 0:
            count -= 1

        if count == 1:
            print ("There is %d gunicorn worker running" % count)
        else:
            print ("There are %d gunicorn workers running" % count)

        return count


def scale_web(direction='up'):
    """Scale up or down the gunicorn web workers"""
    with lcd(root_dir):

        before = count_web()

        with hide('running'):
            pid = local('supervisorctl pid web', capture=True)

            if direction == 'up':
                print ("Scaling up gunicorn workers for master pid %s..." % pid)
                local('kill -TTIN %s' % pid)
            elif direction == 'down':
                if before > 1:
                    print ("Scaling down gunicorn workers for master pid %s..." % pid)
                    local('kill -TTOU %s' % pid)
                else:
                    print ("There is only one web worker running. Use fab stop:web to kill gunicorn.")
                    return
            else:
                raise Exception("Direction argument must be 'up' or 'down'")

        time.sleep(1)
        count = count_web()
        if count == before:
            print ("Changes may not be immediately reflected. Check 'fab count_web' in a moment.")


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


def dump_key(file='.twitter_api_key.json'):
    """Dump a Twitter API key to a fixture file (defaults to .twitter_api_key.json)"""
    manage('dumpdata', 'twitter_stream.ApiKey', '--indent=3', '>', file)


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

        manage('loaddata', file)

        restart('stream')


def dev_data():
    """Loads some fixtures for getting the development environment set up fast."""
    manage('loaddata', 'thermometer_devdata')
    manage('loaddata', 'vagrant_superuser')


def init_south(app):
    """Set up South migrations on an app"""
    manage('syncdb')
    manage('convert_to_south', app)


def new_migration(app):
    """Auto-generate a new migration for an app."""
    manage('schemamigration', app, '--auto')


def updatedb(*args):
    """Runs syncdb and migrate."""
    manage('syncdb', *args)
    manage('migrate', *args)


def shell():
    """Open a Django shell"""
    manage('shell')


def generate_supervisor_conf(user=None, app=None, **kwargs):
    """
    Generates a new supervisord.conf file.
    """

    if user is None:
        import getpass

        user = getpass.getuser()

    if app is None:
        app = os.path.split(root_dir)[1]

    path = os.environ.get('PATH', None)
    if not path:
        raise Exception("No $PATH set???")

    processes = {
        'worker': 1,
        'web': 1,
        'stream': 1,
        'scheduler': 1,
    }
    processes.update(kwargs)

    with lcd(root_dir):
        virtualenv_bin = os.path.dirname(os.path.realpath(sys.executable))

        newconf = _jinja_render('scripts/templates/supervisord.conf', {
            'project_dir': root_dir,
            'app_name': app,
            'virtualenv_bin': virtualenv_bin,
            'user_name': user,
            'processes': processes,
            'path': path
        })

        # Back up first
        local('mv supervisord.conf supervisord.conf~')

        with open('supervisord.conf', 'w') as outfile:
            outfile.write(newconf)

        print ("Saved to supervisord.conf (old file backed up to supervisord.conf~)")