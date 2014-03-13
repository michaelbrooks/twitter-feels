#!/bin/bash

# Script to install Puppet

PROJECT_DIR=$1
source $PROJECT_DIR/scripts/provision/functions.sh

if ! exists 'puppet'; then
    loggy "Installing Puppet..." "warn"
    rpm -ivh https://yum.puppetlabs.com/el/6/products/x86_64/puppetlabs-release-6-7.noarch.rpm
    yum install puppet -y
    loggy "Puppet installed."
else
    loggy "Puppet already installed."
fi

export PUPPET_MODULE_LIST=`puppet module list`

puppet_module_install 'puppetlabs-stdlib'
puppet_module_install 'puppetlabs-mysql'
puppet_module_install 'jfryman-nginx'
puppet_module_install 'redis' 'https://github.com/michaelbrooks/puppet-redis/archive/master.tar.gz' 'thomasvandoren-redis-0.0.9.tar.gz'
puppet_module_install 'gini-archive'
