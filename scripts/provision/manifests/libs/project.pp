import 'python.pp'

class project (
  $processes = []
) {
  require python

  class { 'project::params':
    python_exe => $python::build::python_exe,
    virtualenv_exe => $python::virtualenv::virtualenv_exe,
    pip_exe => $python::pip::pip_exe,
    python_dir => $python::target_dir,
    require => Class['python'],
  }

  contain project::env
  contain project::virtualenv
  contain project::shell
  contain project::requirements

  class { 'project::supervisor':
    processes => $processes,
  }
  contain 'project::supervisor'

  Class['python'] ->
  Class['project::env'] ->
  Class['project::virtualenv'] ->
  Class['project::requirements'] ->
  Class['project::supervisor']

}

class project::env {
  # Create a .env file

  $database_url = "mysql://${database_user}:${database_password}@${database_host}/${database_name}"
  $redis_url = "redis://redisuser:${redis_password}@${redis_host}:${redis_port}"

  file { ".env":
    path => "${project_dir}/.env",
    content => template("${scripts_dir}/templates/default.env.erb"),
    owner => $user_name,
    group => $user_name,
  }
}

class project::params(
  $python_exe = 'python',
  $virtualenv_exe = 'virtualenv',
  $pip_exe = 'pip',
  $python_dir = '/usr/local'
) {
  $pip_download_cache = "${user_home}/.pip_download_cache"
  $workon_home = "${user_home}/.virtualenvs"
  $virtualenvwrapper_sh = "${python_dir}/bin/virtualenvwrapper.sh"

  $environment = [
    "VIRTUALENVWRAPPER_PYTHON=${python_exe}",
    "VIRTUALENVWRAPPER_VIRTUALENV=${virtualenv_exe}",
    "WORKON_HOME=${workon_home}",
    "PIP_DOWNLOAD_CACHE=${pip_download_cache}"
  ]
}

class project::virtualenv () inherits project::params {
  # Create the virtualenv

  file { $pip_download_cache:
    path => $pip_download_cache,
    ensure => "directory",
    owner => $user_name,
    group => $user_name,
  }

  exec { "mkvirtualenv":
    command => "source ${virtualenvwrapper_sh} &&
                mkvirtualenv -a ${project_dir} ${app_name}",

    creates => "${workon_home}/${app_name}",

    provider => "shell",
    user => $user_name,
    environment => $environment,

    require => File[$pip_download_cache]
  }

}

class project::shell () inherits project::params {
  # Set up the user's bashrc

  $bashrc = "${user_home}/.bashrc"
  $fab_complete_sh = "${scripts_dir}/provision/fab_complete.sh"

  file { $bashrc:
    path => $bashrc,
    ensure => "present",
    content => template("${scripts_dir}/templates/bashrc.erb"),
  }
}

class project::requirements () inherits project::params {
  # Setup pip and django stuff

  file { 'copy requirements':
    ensure => 'directory',
    path => "/tmp/requirements",
    source => "${project_dir}/requirements",
    recurse => true,

    owner => $user_name,
    group => $user_name,

    notify => Exec['install requirements'],
  }

  $requirements_file = "/tmp/requirements/${django_environment}.txt"

  exec { "install requirements":
    command => "source ${virtualenvwrapper_sh} &&
                workon ${app_name} &&
                pip install -r ${requirements_file}",

    provider => "shell",
    user => $user_name,
    environment => $environment,

    refreshonly => true,
    require => File['copy requirements']
  }

  # Set up the database schema
  exec { "fab updatedb":
    command => "source ${virtualenvwrapper_sh} &&
                workon ${app_name} &&
                fab updatedb:--noinput",

    provider => "shell",
    user => $user_name,
    environment => $environment,

    require => Exec['install requirements'],
  }

  if $django_environment == 'dev' {
    exec { "load starter data":
      command => "source ${virtualenvwrapper_sh} &&
                  workon ${app_name} &&
                  fab dev_data",

      provider => "shell",
      user => $user_name,
      environment => $environment,

      require => Exec['fab updatedb'],
    }
  } else {
    notify{ "No initial data loaded. You'll need to run manage.py createsuperuser.": }
  }
}

class project::supervisor (
  $processes = []
) inherits project::params {

  $supervisor_conf = "${project_dir}/supervisord.conf"
  $log_dir = "${project_dir}/logs"


  # Make sure there's a directory for logs
  file { $log_dir:
    ensure => "directory",
    owner => $user_name,
    group => $user_name,
  }

  $concurrency = join($processes, ',')

  # Generate a supervisor script from the Procfile
  $fab_args = "user=${user_name},app=${app_name},${concurrency}"
  exec { "supervisor conf":
    command => "source ${virtualenvwrapper_sh} &&
                workon ${app_name} &&
                fab generate_supervisor_conf:${fab_args}",

    creates => $supervisor_conf,

    provider => "shell",
    user => $user_name,
    environment => $environment,

    notify => Service[$app_name],
  }

  # Make sure there's a directory for pids and sockets
  file { "/var/run/${app_name}":
    ensure => "directory",
    owner => $user_name,
    group => $user_name,

    notify => Service[$app_name],
  }

  # Set up the supervisor upstart script
  file { "${app_name} upstart":
    path => "/etc/init/${app_name}.conf",
    content => template("${scripts_dir}/templates/upstart.init.erb"),

    notify => Service[$app_name],
  }

  # Start the service
  service { $app_name:
    hasstatus  => true,
    hasrestart => true,
    start      => "/sbin/initctl start ${app_name}",
    stop       => "/sbin/initctl stop ${app_name}",
    restart    => "/sbin/initctl restart ${app_name}",
    status     => "/sbin/initctl status ${app_name} | grep '/running' 1>/dev/null 2>&1",
    ensure => 'running',
    require => [
      Exec["supervisor conf"],
      File["${app_name} upstart"],
      File[$log_dir],
      File["/var/run/${app_name}"]
    ],
  }

}