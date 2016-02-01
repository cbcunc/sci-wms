#!/bin/bash
set -e

chown redis:redis /var/lib/redis
exec /sbin/setuser redis /usr/bin/redis-server /etc/redis/redis.conf
