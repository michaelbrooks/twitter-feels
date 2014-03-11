import 'base.pp'

if $worker_processes == undef {
  $worker_processes = 1
}

if $stream_processes == undef {
  $stream_processes = 1 - $worker_processes
}

# A node for running workers only
include base

class { "project":
  processes => [
    "web=0",
    "worker=${worker_processes}",
    "stream=${stream_processes}",
    "scheduler=0"
  ],

  require => Class['base'],
}
