#!/bin/bash
set -e

export DJANGO_SECRET_KEY=$(pwgen -s -B -1 40)
echo $DJANGO_SECRET_KEY > /etc/container_environment/DJANGO_SECRET_KEY

if [ "$SETTINGS" == "dev" ]; then
    conda install -y --file requirements-dev.txt
fi
