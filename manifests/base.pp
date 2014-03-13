# Default settings
$app_name_slug = regsubst($app_name, '-', '_', 'G')

$web_hostname = 'localhost'
$web_server_port = 8000
$web_server_host = 'localhost'
$url_prefix = '/'

$redis_port = 6379
$redis_host = '127.0.0.1'
$redis_password = md5($redis_host)

$database_host = 'localhost'
# Replace - with _
$database_name = $app_name_slug
$database_user = $database_name
$database_password = $database_user

import 'libs/database.pp'
import 'libs/webserver.pp'
import 'libs/redisserver.pp'
import 'libs/python.pp'
import 'libs/project.pp'


class base {
  exec { "yum update -y":
    path => "/usr/bin",
  }

  package { "git":
    ensure  => present,
  }

  package { 'mysql-community-release':
    ensure => 'installed',
    source => 'http://dev.mysql.com/get/mysql-community-release-el6-5.noarch.rpm',
    provider => 'rpm'
  }

}
