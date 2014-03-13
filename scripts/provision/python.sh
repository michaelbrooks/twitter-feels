#!/bin/bash

# Install python 2.7.6
# see: http://toomuchdata.com/2014/02/16/how-to-install-python-on-centos/

set -e

PYTHON_VERSION=$1
INSTALL_TARGET=$2
PYTHON_EXE=$3

MY_DIR=`dirname $0`
source $MY_DIR/functions.sh


loggy "Installing Python $PYTHON_VERSION..." "warn"

PACKAGE_NAME=Python-$PYTHON_VERSION
PACKAGE_URL=http://python.org/ftp/python/$PYTHON_VERSION/$PACKAGE_NAME.tar.xz
PACKAGE_DIR='/usr/src'

if ! [ -e $PACKAGE_DIR/$PACKAGE_NAME.tar.xz ]; then
    curl -L -o $PACKAGE_DIR/$PACKAGE_NAME.tar.xz  $PACKAGE_URL
fi

# Extract
SRC_DIR='/tmp'
tar -xJf $PACKAGE_DIR/$PACKAGE_NAME.tar.xz -C $SRC_DIR

# Configure
cd $SRC_DIR/$PACKAGE_NAME
$SRC_DIR/$PACKAGE_NAME/configure --prefix=$INSTALL_TARGET --enable-unicode=ucs4 --enable-shared LDFLAGS="-Wl,-rpath ${INSTALL_TARGET}/lib"

# Install
/usr/bin/make && /usr/bin/make altinstall

cd $SRC_DIR
rm -rf $SRC_DIR/$PACKAGE_NAME $PACKAGE_DIR/$PACKAGE_NAME.tar.xz

if exists $PYTHON_EXE; then
    loggy "Python ${PYTHON_VERSION} installed to ${PYTHON_EXE}."
    exit 0
else
    loggy "Failed to install Python ${PYTHON_VERSION} to ${PYTHON_EXE}!" "error"
    exit 1
fi
