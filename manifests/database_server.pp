import 'base.pp'

# A node for running mysql only
include base

class { 'database':
  database_name => $database_name,
  database_user => $database_user,
  database_password => $database_password,
  login_host => $web_server_host,

  require => Class['base'],
}
