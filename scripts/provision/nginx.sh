#!/bin/bash

# MySQL
if ! exists "nginx"; then
    loggy "Installing nginx..." "warn"

    NGINX_REPO=nginx-release-centos-6-0.el6.ngx.noarch

    # First install the yum repository
    if ! rpm -qa | grep -qw ${NGINX_REPO}; then
        curl -LO http://nginx.org/packages/centos/6/noarch/RPMS/${NGINX_REPO}.rpm
        yum -y localinstall ${NGINX_REPO}.rpm
        rm ${NGINX_REPO}.rpm
    fi

    # Install nginx
    yum install -y nginx

    loggy "Nginx installed."
fi

# Install nginx service
if ! service_exists "nginx"; then
    loggy "Installing nginx as a service..." "warn"

    # Install redis as a service
    chkconfig nginx on

    loggy "Nginx service installed."
else
    loggy "Nginx service already installed."
fi

# Copy nginx.cnf into place
if different $PROVISION_SCRIPTS/nginx.conf /etc/nginx/nginx.conf; then
    loggy "Installing nginx config file..." "warn"

    cp -p $PROVISION_SCRIPTS/nginx.conf /etc/nginx/nginx.conf
    chown root:root /etc/nginx/nginx.conf
    chmod 644 /etc/nginx/nginx.conf

    # Reload nginx
    loggy "Reloading nginx..." "warn"
    nginx -s reload
    loggy "Nginx reloaded."
else
    loggy "Nginx already configured"
fi

# Copy nginx default.conf into place
# Copy nginx.cnf into place
if different $PROVISION_SCRIPTS/nginx.default.conf /etc/nginx/conf.d/default.conf; then
    loggy "Installing nginx site config file..." "warn"

    cp -p $PROVISION_SCRIPTS/nginx.default.conf /etc/nginx/conf.d/default.conf
    chown root:root /etc/nginx/conf.d/default.conf
    chmod 644 /etc/nginx/conf.d/default.conf

    # Reload nginx
    loggy "Reloading nginx..." "warn"
    nginx -s reload
    loggy "Nginx reloaded."
else
    loggy "Nginx site already configured"
fi

if ! started "nginx"; then
    loggy "Starting nginx..." "warn"
    service nginx start
    loggy "nginx started."
fi
