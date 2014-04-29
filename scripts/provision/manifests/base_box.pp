# Configure a default box with everything pre-installed

import 'base.pp'

include base

class { 'database':
  database_name => $database_name,
  database_user => $database_user,
  database_password => $database_password,
  login_host => $web_server_host,

  require => Class['base'],
}

class { 'redisserver':
  redis_port => $redis_port,
  redis_bind_address => $redis_host,
  redis_password => $redis_password,

  require => Class['base'],
}

class { 'webserver':
  app_name_slug => $app_name_slug,
  upstreams => ["${web_server_host}:${web_server_port}"],
  hostname => $web_hostname,
  url_prefix => $url_prefix,

  require=> Class['base'],
}

include python
