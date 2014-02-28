#!/bin/bash

# Install essential packages from yum
# if this hasn't been done more recently than 24 hours ago
if older_than "/home/vagrant/.vagrant_updated" 1440; then
    loggy "Updating packages..." "warn"
    yum update -y
    date > /home/vagrant/.vagrant_updated
    loggy "Done updating packages."
else
    loggy "Packages were updated recently."
fi
