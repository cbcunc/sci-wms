#!/bin/bash
set -e
. /etc/profile

ADMIN_USER=${SCIWMS_USERNAME:-sciwmsuser}
ADMIN_EMAIL=${SCIWMS_EMAIL:-sciwms@example.com}
ADMIN_PASS=${SCIWMS_PASSWORD:-$(pwgen -s -1 16)}
cat << EOF | python manage.py shell >/dev/null 2>&1
from django.contrib.auth.models import User
from django.contrib.auth.models import User
u, _ = User.objects.get_or_create(username='$ADMIN_USER')
u.set_password('$ADMIN_PASS')
u.email = '$ADMIN_EMAIL'
u.is_superuser = True
u.is_staff = True
u.save()
EOF

echo "user:       \"$ADMIN_USER\""
echo "password:   \"$ADMIN_PASS\""
