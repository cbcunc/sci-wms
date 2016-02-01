#!/bin/bash
sv start redis || exit 1

set -e
. /etc/profile

cd $SCIWMS_ROOT

celery worker \
    -A sciwms \
    -E \
    -Q celery \
    -c 4 \
    -n celery | logger -t worker
