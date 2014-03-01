#!/bin/bash

# http://ptylr.com/2013/11/05/installing-configuring-redis-in-centos-6-from-source/

REDIS_VERSION=2.8.6

# Install redis
if ! exists "redis-server"; then
    loggy "Installing Redis $REDIS_VERSION..." "warn"

    # Download and compile
    curl -LO http://download.redis.io/releases/redis-${REDIS_VERSION}.tar.gz
    tar zxf redis-${REDIS_VERSION}.tar.gz
    cd redis-${REDIS_VERSION}
    make && make install
    cd ..

    rm -rf redis-${REDIS_VERSION} redis-${REDIS_VERSION}.tar.gz

    loggy "Done installing Redis."
else
    loggy "Redis already installed."
fi

# Copy redis.conf into place
if different $PROVISION_SCRIPTS/redis.conf /etc/redis/redis.conf; then
    loggy "Installing redis config file..." "warn"

    # Make the data dir
    mkdir -p /var/lib/redis

    cp -p $PROVISION_SCRIPTS/redis.conf /etc/redis/redis.conf
    chown root:root /etc/redis/redis.conf
    chmod 644 /etc/redis/redis.conf

    if started "redis"; then
        loggy "Restarting redis..." "warn"
        service redis restart
        loggy "Redis restarted."
    fi
else
    loggy "Redis already configured."
fi

# Install redis service
if ! service_exists "redis" || different $PROVISION_SCRIPTS/redis_init_script /etc/init.d/redis; then
    loggy "Installing Redis as a service..." "warn"

    # Install redis as a service
    mkdir -p /etc/redis
    mkdir -p /var/redis
    cp -p $PROVISION_SCRIPTS/redis_init_script /etc/init.d/redis
    chown root:root /etc/init.d/redis
    chmod 755 /etc/init.d/redis

    chkconfig --add redis
    chkconfig redis on

    loggy "Redis service installed."
else
    loggy "Redis service already installed."
fi

if ! started "redis"; then
    loggy "Starting Redis..." "warn"
    service redis start
    loggy "Redis started."
fi


if [ "`redis-cli ping 2> /dev/null`" = "PONG" ]; then
    loggy "Redis server is reachable."
else
    loggy "Redis server is not reachable!" "error"
fi