from fabric.api import local

def _supervisor(command, *args):
    if args:
        local('supervisorctl %s %s' % (command, ' '.join(args)))
    elif command == 'status':
        local('supervisorctl %s' % command)
    else:
        local('supervisorctl %s all' % command)

def stop(*args):
    _supervisor('stop', *args)

def start(*args):
    _supervisor('start', *args)

def restart(*args):
    _supervisor('restart', *args)

def status(*args):
    _supervisor('status', *args)

def refresh_web():
    pid = local('supervisorctl pid web', capture=True)
    local('kill -HUP %s' % pid)

def clear_logs():
    local('echo "" | tee logs/*.log > /dev/null')