#!/bin/bash
set -e
. /etc/profile

python manage.py migrate --noinput
