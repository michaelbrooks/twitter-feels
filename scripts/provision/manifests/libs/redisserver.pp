
class redisserver (
  $redis_port = 6379,
  $redis_bind_address = '127.0.0.1',
  $redis_password = undef
) {

  class { 'redis':
    version            => "2.8.7",
  }
  contain 'redis'

  redis::instance { 'redis-${redis_port}':
    redis_port         => $redis_port,
    redis_bind_address => $redis_host,
    redis_password     => $redis_password,

    require => Class['redis'],
  }
}
