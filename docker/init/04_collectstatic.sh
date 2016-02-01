#!/bin/bash
set -e
. /etc/profile

python manage.py collectstatic --noinput -v 0
