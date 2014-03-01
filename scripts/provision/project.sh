#!/bin/bash

loggy "Creating project virtualenv..."

# bash environment global setup
cp -p $PROVISION_SCRIPTS/bashrc /home/vagrant/.bashrc
su - vagrant -c "mkdir -p /home/vagrant/.pip_download_cache"

# virtualenv setup for project
su - vagrant -c "/usr/local/bin/virtualenv $VIRTUALENV_DIR && \
    echo $PROJECT_DIR > $VIRTUALENV_DIR/.project && \
    PIP_DOWNLOAD_CACHE=/home/vagrant/.pip_download_cache $VIRTUALENV_DIR/bin/pip install -r $PROJECT_DIR/requirements/dev.txt"

loggy "Virtualenv created at $VIRTUALENV_DIR"

# Place .env in project directory
cp -p $PROVISION_SCRIPTS/dev.env $PROJECT_DIR/.env

echo "workon $VIRTUALENV_NAME" >> /home/vagrant/.bashrc

# Set execute permissions on manage.py, as they get lost if we build from a zip file
chmod a+x $PROJECT_DIR/manage.py

# Django project setup
su - vagrant -c "source $VIRTUALENV_DIR/bin/activate && cd $PROJECT_DIR && honcho ./manage.py syncdb --noinput && honcho ./manage.py migrate"

loggy "Project setup complete."