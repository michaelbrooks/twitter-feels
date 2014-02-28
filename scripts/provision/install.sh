#!/bin/bash

# Script to set up a Django project on Vagrant.

# Installation settings

PROJECT_NAME=$1

DB_NAME=$PROJECT_NAME
VIRTUALENV_NAME=$PROJECT_NAME

PROJECT_DIR=/home/vagrant/$PROJECT_NAME
VIRTUALENV_DIR=/home/vagrant/.virtualenvs/$PROJECT_NAME
PROVISION_SCRIPTS=$PROJECT_DIR/scripts/provision

function loggy {
    # Prints a message in green with lots of space around it.
    echo ""
    echo -e "\e[32m"$1
    echo -e "\e[0m"
}

function exists {
    # Checks if a command exists, returns a status code
    command -v $1 > /dev/null
    return $?
}

function started {
    # Checks if a service is running
    service $1 status > /dev/null
    return $?
}

function different {
    # Wrapper around diff that flips the return value
    ! diff $1 $2 > /dev/null
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

# Install essential packages from yum
# if this hasn't been done more recently than 24 hours ago
if older_than "/home/vagrant/.vagrant_updated" 1440; then
    loggy "Updating packages..."
    yum update -y
    date > /home/vagrant/.vagrant_updated
    loggy "Done updating packages."
else
    loggy "Packages were updated recently."
fi

source $PROVISION_SCRIPTS/git.sh
source $PROVISION_SCRIPTS/python.sh
source $PROVISION_SCRIPTS/mysql.sh
source $PROVISION_SCRIPTS/redis.sh


# Node.js, CoffeeScript and LESS
#if ! command -v npm; then
#    wget http://nodejs.org/dist/v0.10.0/node-v0.10.0.tar.gz
#    tar xzf node-v0.10.0.tar.gz
#    cd node-v0.10.0/
#    ./configure && make && make install
#    cd ..
#    rm -rf node-v0.10.0/ node-v0.10.0.tar.gz
#fi
#if ! command -v coffee; then
#    npm install -g coffee-script
#fi
#if ! command -v lessc; then
#    npm install -g less
#fi


# bash environment global setup
cp -p $PROVISION_SCRIPTS/bashrc /home/vagrant/.bashrc
su - vagrant -c "mkdir -p /home/vagrant/.pip_download_cache"

exit 0
# virtualenv setup for project
su - vagrant -c "/usr/local/bin/virtualenv $VIRTUALENV_DIR && \
    echo $PROJECT_DIR > $VIRTUALENV_DIR/.project && \
    PIP_DOWNLOAD_CACHE=/home/vagrant/.pip_download_cache $VIRTUALENV_DIR/bin/pip install -r $PROJECT_DIR/requirements/dev.txt"

echo "workon $VIRTUALENV_NAME" >> /home/vagrant/.bashrc

# Set execute permissions on manage.py, as they get lost if we build from a zip file
chmod a+x $PROJECT_DIR/manage.py

# Django project setup
su - vagrant -c "source $VIRTUALENV_DIR/bin/activate && cd $PROJECT_DIR && ./manage.py syncdb --noinput && ./manage.py migrate"