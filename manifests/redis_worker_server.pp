include 'base.pp'

# A node for running redis and workers
include base

class { 'redisserver':
  redis_port => $redis_port,
  redis_bind_address => $redis_host,
  redis_password => $redis_password,

  require => Class['base'],
}

class { "project":
  require => Class['redisserver'],
  processes => [
    "web=0",
    "worker=1",
    "stream=0",
    "scheduler=1"
  ]
}