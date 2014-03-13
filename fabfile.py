import os

from fabric.api import local
from fabric.context_managers import lcd
from fabric.state import env
from fabric import utils

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

    manage('runserver')


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


def updatedb():
    """Runs syncdb and migrate."""
    manage('syncdb')
    manage('migrate')


def shell():
    """Open a Django shell"""
    manage('shell')


def generate_supervisor_conf(app='my_app', port=8000, log=None, user=None, **kwargs):
    """
    honcho export --user ${user_name} \
                  --port ${web_server_port} \
                  --log ${log_dir} \
                  --app ${app_name} \
                  --concurrency ${concurrency} \
                  supervisord /tmp &&
                sed -i 's;^command=;command=${workon_home}/${app_name}/bin/;g' /tmp/${app_name}.conf &&
                sed -i 's;^\\[program:${app_name}-;\\[program:;g' /tmp/${app_name}.conf &&
                sed -i 's;${log_dir}/\\([^.]\\+\\)-1;${log_dir}/\\1;g' /tmp/${app_name}.conf &&
                grep -v '^\\[group:${app_name}' /tmp/${app_name}.conf > /tmp/${app_name}-2.conf &&
                grep -v '^programs=${app_name}-' /tmp/${app_name}-2.conf > /tmp/${app_name}.conf &&
                cat /tmp/supervisor.${app_name}.conf-top /tmp/${app_name}.conf > ${supervisor_conf} &&
                rm /tmp/${app_name}*.conf
    """

    if user is None:
        import getpass

        user = getpass.getuser()

    if log is None:
        log = os.path.join(root_dir, 'logs')

    if kwargs:
        concurrency = ','.join(['%s=%s' % (process, count) for process, count in kwargs.iteritems()])
    else:
        concurrency = ""

    with lcd(root_dir):
        # Generate a partial supervisord conf file
        tmpconf = "/tmp/%s.conf" % app

        export_cmd = 'honcho export --user %(user)s --port %(port)s --log %(log)s --app %(app)s '
        if concurrency:
            export_cmd += '--concurrency=%(concurrency)s '
        export_cmd += 'supervisord /tmp'

        local(export_cmd % {
            'user': user,
            'app': app,
            'port': port,
            'log': log,
            'concurrency': concurrency,
        })

        # Set absolute paths to commands
        virtual_env = os.environ['VIRTUAL_ENV']
        local('sed -i "s;^command=;command=%(virtual_env)s/bin/;g" %(tmpconf)s' % {
            'virtual_env': virtual_env,
            'tmpconf': tmpconf,
        })

        # Remove app names from stuff
        local(r'sed -i "s;\[program:%(app)s-;\[program:;g" %(tmpconf)s' % {
            'app': app,
            'tmpconf': tmpconf,
        })

        # Remove number from log filenames
        local(r'sed -i "s;%(log)s/\([^.]\+\)-1;%(log)s/\1;g" %(tmpconf)s' % {
            'log': log,
            'tmpconf': tmpconf,
        })

        # Remove program group
        local(r'grep -v "^\[group:%(app)s" %(tmpconf)s > %(tmpconf)s-1' % {
            'app': app,
            'tmpconf': tmpconf
        })
        local(r'grep -v "^programs=%(app)s-" %(tmpconf)s-1 > %(tmpconf)s' % {
            'app': app,
            'tmpconf': tmpconf
        })
