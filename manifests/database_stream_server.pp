import 'base.pp'

include base

class { 'database':
  database_name => $database_name,
  database_user => $database_user,
  database_password => $database_password,
  login_host => $web_server_host,

  require => Class['base'],
}

# A node for running mysql and the stream
class { "project":
  require => Class['database'],
  processes => [
    "web=0",
    "worker=0",
    "stream=1",
    "scheduler=0"
  ]
}