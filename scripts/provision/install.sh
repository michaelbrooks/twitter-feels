#!/bin/bash

# Script to set up a Django project on Vagrant.
# https://github.com/torchbox/vagrant-django-template/blob/master/etc/install/install.sh

# Installation settings
PROJECT_NAME=$1

VIRTUALENV_NAME=$PROJECT_NAME

PROJECT_DIR=/home/vagrant/$PROJECT_NAME
VIRTUALENV_DIR=/home/vagrant/.virtualenvs/$PROJECT_NAME
PROVISION_SCRIPTS=$PROJECT_DIR/scripts/provision

# Add /usr/local to PATH so we can find Python and Redis
export PATH=/usr/local/bin:/usr/local/sbin:$PATH

source $PROVISION_SCRIPTS/functions.sh
source $PROVISION_SCRIPTS/system.sh
source $PROVISION_SCRIPTS/git.sh
source $PROVISION_SCRIPTS/mysql.sh
source $PROVISION_SCRIPTS/redis.sh
source $PROVISION_SCRIPTS/nginx.sh
source $PROVISION_SCRIPTS/python.sh

if [ "$2" = "base" ]; then
    echo "Project settings not initialized."
    echo "Run 'vagrant package --base my-virtual-machine' to package as a vagrant box."
else
    source $PROVISION_SCRIPTS/project.sh
fi

exit 0