#!/bin/bash

# replace - with _
DB_NAME=${PROJECT_NAME//-/_}
DB_USER=$DB_NAME
DB_PASSWORD=$DB_USER

# MySQL
if ! exists "mysql"; then
    loggy "Installing MySQL..." "warn"

    MYSQL_REPO=mysql-community-release-el6-5.noarch

    # First install the yum repository
    if ! rpm -qa | grep -qw ${MYSQL_REPO}; then
        curl -LO http://dev.mysql.com/get/${MYSQL_REPO}.rpm
        yum -y localinstall ${MYSQL_REPO}.rpm
        rm ${MYSQL_REPO}.rpm
    fi

    # Update components from the new repo
    yum -y update

    # Then install mysql, and mysql-devel (needed to build mysql-python later)
    yum install -y mysql-server mysql-devel

    # Make mysql start automatically
    chkconfig mysqld on

    # mysql_secure_installation

    if ! exists "mysql"; then
        loggy "MySQL failed to install!" "error"
    else:
        # To secure the installation
        loggy "MySQL installed."
    fi
else
    loggy "MySQL already installed."
fi

# Copy my.cnf into place
if different $PROVISION_SCRIPTS/my.cnf /etc/my.cnf; then
    loggy "Installing MySQL config file..." "warn"

    cp -p $PROVISION_SCRIPTS/my.cnf /etc/my.cnf
    chown root:root /etc/my.cnf
    chmod 644 /etc/my.cnf

    # Reload mysql
    loggy "Restarting MySQL..." "warn"
    service mysqld restart
    loggy "MySQL restarted."
else
    loggy "MySQL already configured"
fi

if ! started "mysqld"; then
    loggy "Starting MySQL..." "warn"
    service mysqld start

    if ! started "mysql"; then
        loggy "MySQL failed to start!" "error"
    else:
        loggy "MySQL started."
    fi
fi

# mysql setup for project
echo "CREATE DATABASE IF NOT EXISTS $DB_NAME;" | mysql -u root
echo "GRANT ALL PRIVILEGES ON $DB_NAME.* TO $DB_USER@localhost IDENTIFIED BY '$DB_PASSWORD';" | mysql -u root
echo "GRANT ALL PRIVILEGES ON $DB_NAME.* TO $DB_USER@127.0.0.1 IDENTIFIED BY '$DB_PASSWORD';" | mysql -u root
loggy "Created database $DB_NAME for user $DB_USER"

