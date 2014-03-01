#!/bin/bash

# Install supervisord
if ! exists "supervisor"; then
    loggy "Installing git..." "warn"
    yum install -y git
    loggy "Done installing git."
else
    loggy "Git already installed."
fi

