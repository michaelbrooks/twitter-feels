#!/bin/bash

# Install Git
if ! exists "git"; then
    loggy "Installing git..."
    yum install -y git
    loggy "Done installing git."
else
    loggy "Git already installed."
fi

