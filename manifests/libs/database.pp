
class database (
  $database_name,
  $database_user,
  $database_password,
  $login_host
) {
  # Install a mysql server and database

  class { 'mysql::server':
    package_name => 'mysql-community-server',

    override_options => {
      'mysqld' => {
        'collation-server' => 'utf8mb4_unicode_ci',
        'init_connect' => '"SET NAMES utf8mb4"',
        'character-set-server' => 'utf8mb4',
      },
      'client' => {
        'default-character-set' => 'utf8mb4',
      },
      'mysql' => {
        'default-character-set' => 'utf8mb4',
      },

    },

    databases => {
      "${database_name}" => {
        ensure  => 'present',
        charset => 'utf8mb4',
        collate => 'utf8mb4_unicode_ci',
      },
    },
  }
  contain 'mysql::server'

  class { 'mysql::client':
    package_name => 'mysql-community-client',

    require => Class['mysql::server'],
  }
  contain 'mysql::client'

  $database_user_location = "${database_user}@${login_host}"

  # Permission to log in locally
  mysql_user { "${database_user_location}":
    password_hash => mysql_password($database_password),
    require => Class['mysql::client'],
  }

  # Give the user all privileges
  mysql_grant { "${database_usr_location}/${database_name}.*":
    ensure => 'present',
    privileges => ['ALL'],
    table      => "${database_name}.*",
    user       => $database_user_location,
    require => Class['mysql::client'],
  }

}