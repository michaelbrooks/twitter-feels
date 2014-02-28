#!/bin/bash

# http://ptylr.com/2013/11/05/installing-configuring-redis-in-centos-6-from-source/

REDIS_VERSION=2.8.6

# Install redis
if ! exists "redis-server"; then
    loggy "Installing Redis $REDIS_VERSION..."

    # Download and compile
    curl -LO http://download.redis.io/releases/redis-${REDIS_VERSION}.tar.gz
    tar zxf redis-${REDIS_VERSION}.tar.gz
    cd redis-${REDIS_VERSION}
    make && make install
    cd ..

    loggy "Done installing Redis."
else
    loggy "Redis already installed."
fi

# Install redis service
if ! service_exists "redis"; then
    loggy "Installing Redis as a service..."

    # Install redis as a service
    mkdir -p /etc/redis
    mkdir -p /var/redis
    cp -p $PROVISION_SCRIPTS/redis_init_script /etc/init.d/redis

    chkconfig --add redis
    chkconfig redis on

    loggy "Redis service installed."
else
    loggy "Redis service already installed."
fi

# Copy redis.conf into place
if different $PROVISION_SCRIPTS/redis.conf /etc/redis/redis.conf; then
    loggy "Installing redis config file..."

    # Make the data dir
    mkdir -p /var/lib/redis

    cp -p $PROVISION_SCRIPTS/redis.conf /etc/redis/redis.conf
    chmod 644 /etc/redis/redis.cnf

    loggy "Restarting redis..."
    service redis restart
    loggy "Redis restarted."
else
    loggy "Redis already configured."
fi

if ! started "redis"; then
    loggy "Starting Redis..."
    service redis start
    loggy "Redis started."
fi

redis-cli ping