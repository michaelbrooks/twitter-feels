
class python (
  # Which python to compile
  $version = '2.7.6',
  # Where to install to
  $target_dir = '/usr/local'
) {

  contain python::build
  contain python::pip
  contain python::virtualenv
  contain python::supervisor

  Class['python::build'] ->
  Class['python::pip'] ->
  Class['python::virtualenv'] ->
  Class['python::supervisor']
}

class python::build::libs {
  # Installs some things needed to build python
  # Do not include this class unless you are class python::build!

  include base

  # Make sure the development tools are installed
  # http://projects.puppetlabs.com/issues/5175
  # Not very elegant, but it's a work around
  exec { 'yum Group Install':
    unless  => '/usr/bin/yum grouplist "Development tools" | /bin/grep "^Installed Groups"',
    command => '/usr/bin/yum -y groupinstall "Development tools"',
    require => Class['base']
  }

  $libs = [
    "zlib-devel", "bzip2-devel", "openssl-devel", "ncurses-devel",
    "libxml2-devel", "libxslt-devel", "unixODBC-devel",
    "sqlite", "sqlite-devel", 'mysql-community-devel',
    "readline-devel"
  ]
  package { $libs:
    ensure => "installed",
    require => Exec['yum Group Install']
  }
}

class python::build {
  # Builds Python
  # Do not include this class unless you are class python!
  # The version code appended to the python executable
  $short_version_code = regsubst($python::version, '^(\d\.\d)\.\d$','\1')

  # The full path to the python executable we are trying to build
  $python_exe = "${python::target_dir}/bin/python${short_version_code}"

  # The command that tests if the python version we are building already exists
  $python_missing_command = "[[ $(${python_exe} --version 2>&1) != 'Python ${python::version}' ]]"

  include python::build::libs

  exec { "Install Python-${python::version}":
    command => "${scripts_dir}/provision/python.sh ${python::version} ${python::target_dir} ${python_exe}",
    creates => $python_exe,
    onlyif => $python_missing_command,
    provider => "shell",
    timeout => 0,
    require => Class['python::build::libs']
  }
}

class python::pip {
  # Installs pip
  # Do not include this class unless you are class python!

  $pip_exe = "${python::target_dir}/bin/pip"
  $pip_missing_command = "! command -v ${pip_exe} 2>&1 > /dev/null"

  exec { "install pip":
    command => "curl -L https://raw.github.com/pypa/pip/master/contrib/get-pip.py | ${python::build::python_exe}",
    onlyif => $pip_missing_command,
    provider => "shell",
  }
}

class python::virtualenv {
  # Installs virtualenv and virtualenvwrapper
  # Do not include this class unless you are class python!

  $virtualenv_exe = "${python::target_dir}/bin/virtualenv"
  $virtualenvwrapper_missing_command = "! (
    (${python::pip::pip_exe} freeze | grep -e '^virtualenvwrapper==' > /dev/null)
    (command -v ${virtualenv_exe} > /dev/null)
  )"

  exec { 'install virtualenvwrapper':
    command => "${python::pip::pip_exe} install virtualenvwrapper",
    onlyif => $virtualenvwrapper_missing_command,
    provider => "shell",
  }
}

class python::supervisor {
  # Installs supervisor globally
  # Do not include this class unless you are class python!
  $supervisord_exe = "${python::target_dir}/bin/supervisord"
  $supervisor_missing_command = "! (command -v ${supervisord_exe} > /dev/null)"

  exec { 'install supervisor':
    command => "${python::pip::pip_exe} install supervisor",
    onlyif => $supervisor_missing_command,
    provider => "shell",
  }
}
