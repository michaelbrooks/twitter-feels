#!/bin/bash

# Install python 2.7.6
# see: http://toomuchdata.com/2014/02/16/how-to-install-python-on-centos/
_PYTHON=python2.7
if ! exists $_PYTHON; then
    loggy "Installing $_PYTHON..." "warn"

    yum -y groupinstall "Development tools"
    # https://gist.github.com/hangtwenty/5546945
    yum -y install zlib-devel  # gen'l reqs
    yum -y install bzip2-devel openssl-devel ncurses-devel  # gen'l reqs
    yum -y install mysql-devel  # req'd to use MySQL with python ('mysql-python' package)
    yum -y install libxml2-devel libxslt-devel  # req'd by python package 'lxml'
    yum -y install unixODBC-devel  # req'd by python package 'pyodbc'
    yum -y install sqlite sqlite-devel  # you will be sad if you don't install this before compiling python, and later need it.

    curl -LO http://python.org/ftp/python/2.7.6/Python-2.7.6.tar.xz
    tar xf Python-2.7.6.tar.xz
    cd Python-2.7.6
    ./configure --prefix=/usr/local --enable-unicode=ucs4 --enable-shared LDFLAGS="-Wl,-rpath /usr/local/lib"
    make && make altinstall

    cd ..
    rm -rf Python-2.7.6 Python-2.7.6.tar.gx

    loggy "Done installing $_PYTHON."
else
    loggy "$_PYTHON already installed."
fi

_PIP=pip2.7
if ! exists $_PIP; then
    loggy "Installing $_PIP..." "warn"

    # Install pip and setuptools
    curl -L https://raw.github.com/pypa/pip/master/contrib/get-pip.py | $_PYTHON
    loggy "Done installing $_PIP."
else
    loggy "$_PIP already installed."
fi

# virtualenv global setup
_VIRTUALENV=virtualenv-2.7
if ! exists $_VIRTUALENV; then
    loggy "Installing $_VIRTUALENV..." "warn"
    $_PIP install virtualenv virtualenvwrapper
    loggy "$_VIRTUALENV installed."
else
    loggy "$_VIRTUALENV already installed."
fi
