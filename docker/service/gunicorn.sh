#!/bin/bash
sv start redis || exit 1

set -e
. /etc/profile

cd $SCIWMS_ROOT

gunicorn \
    --access-logfile - \
    --error-logfile - \
    --max-requests 100 \
    --graceful-timeout 300 \
    --keep-alive 5 \
    --backlog 50 \
    --log-level warning \
    -t 300 \
    -b 0.0.0.0:$WEB_PORT \
    -w 4 \
    -k tornado \
    -e DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE \
    -n sciwms \
    sciwms.wsgi:application | logger -t gunicorn
