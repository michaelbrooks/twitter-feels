class webserver (
  $app_name_slug,
  $hostname,
  $url_prefix = '/',
  $upstreams = []
) {
  # TODO: add support for url_prefix!

  class { 'nginx':
    package_source => 'http://nginx.org/packages/centos/6/noarch/RPMS/nginx-release-centos-6-0.el6.ngx.noarch.rpm',

    nginx_upstreams => {
      "${app_name_slug}" => {
        members => $upstreams,
      }
    },

    nginx_vhosts => {
      "${hostname}" => {
        proxy  => "http://${app_name_slug}",
        proxy_set_header => ['Host $http_host']
      }
    },
  }
  contain 'nginx'

  # Remove this file since it defines a server we don't need
  file { 'default.conf remove':
    path => "${nginx::params::nx_conf_dir}/conf.d/default.conf",
    ensure => absent,
    require => Package['nginx'],
    notify => Service['nginx'],
  }

}
