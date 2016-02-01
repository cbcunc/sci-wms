#!/bin/bash
sv start redis || exit 1
sv start worker || exit 1

set -e
. /etc/profile

cd $SCIWMS_ROOT

celery beat -A sciwms | logger -t beat
