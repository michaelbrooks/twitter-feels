import 'base.pp'

# A node for running a web server only
include base

class { 'webserver':
  app_name_slug => $app_name_slug,
  upstreams => ["${web_server_host}:${web_server_port}"],
  hostname => $web_hostname,
  url_prefix => $url_prefix,

  require => Class['base']
}

class { "project":
  require => Class['webserver'],
  processes => [
    "web=1",
    "worker=0",
    "stream=0",
    "scheduler=0"
  ]
}