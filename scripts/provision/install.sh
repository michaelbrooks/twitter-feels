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

function loggy {
    # Prints a message in green with lots of space around it.
    # If the 2nd parameter is error, message is red
    # http://misc.flogisoft.com/bash/tip_colors_and_formatting
    echo ""

    case "$2" in
        error)
            # Red text
            color="\e[31m"
            ;;
        warn)
            # Red text
            color="\e[33m"
            ;;
        *)
            # Green text
            color="\e[32m"
            ;;
    esac

    echo -e $color$1
    echo -e "\e[0m"
}

function exists {
    # Checks if a command exists, returns a status code
    command -v $1 &> /dev/null
    return $?
}

function started {
    # Checks if a service is running
    service $1 status | grep "running" &> /dev/null
    return $?
}

function service_exists {
    service $1 status &> /dev/null
    return $?
}

function different {
    # Wrapper around diff that flips the return value
    ! diff $1 $2 &> /dev/null
    return $?
}

function older_than {
    # Returns true if the file is older than a number of minutes
    # `find -cmin -N` returns the filename if its status changed more recently than N minutes
    # [ -z ... ] returns true if the result of find is an empty string
    # so it returns true if the file was NOT changed more recently than N minutes, i.e. it is older than N.
    [ -z `find $1 -cmin -$2 2> /dev/null` ]
    return $?
}

source $PROVISION_SCRIPTS/system.sh
source $PROVISION_SCRIPTS/git.sh
source $PROVISION_SCRIPTS/mysql.sh
source $PROVISION_SCRIPTS/redis.sh
source $PROVISION_SCRIPTS/nginx.sh
source $PROVISION_SCRIPTS/python.sh
source $PROVISION_SCRIPTS/project.sh

exit 0