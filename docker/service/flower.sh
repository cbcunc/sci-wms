#!/bin/bash
sv start redis || exit 1
sv start worker || exit 1

set -e
. /etc/profile

cd $SCIWMS_ROOT

flower -A sciwms --log_to_stderr | logger -t flower
