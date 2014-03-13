#!/bin/bash


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


function puppet_module_exists {
    # Checks if a puppet module is already installed
    if [ -z "$PUPPET_MODULE_LIST" ]; then
        export PUPPTE_MODULE_LIST=`puppet module list`
    fi

    echo $PUPPET_MODULE_LIST | grep $1 &> /dev/null
    return $?
}

function puppet_module_install {
    # Installs a puppet module if it is not already installed
    if ! puppet_module_exists $1; then
        if [ -z "$2" ]; then
            loggy "Installing Puppet module $1..." "warn"
            puppet module install $1
        else
            if [ -z "$3" ]; then
                loggy "No filename given for $1. Must be like <module_name>-<version>.tar.gz." "error"
                exit 1
            fi

            filename=$3
            loggy "Installing Puppet module $filename from $2..." "warn"
            curl -L -o /tmp/$filename $2
            puppet module install /tmp/$filename
            rm /tmp/$filename
        fi
        loggy "Puppet module $1 installed."
    else
        loggy "Puppet module $1 already installed."
    fi
}
