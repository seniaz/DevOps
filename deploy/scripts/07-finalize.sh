#!/usr/bin/env bash

set -euo pipefail

: "${STUDENT_NUMBER:?STUDENT_NUMBER must be exported}"

echo "    -> writing /home/student/gradebook"
echo "${STUDENT_NUMBER}" > /home/student/gradebook
chown student:student /home/student/gradebook
chmod 0644 /home/student/gradebook

for default_user in ubuntu debian centos cloud-user fedora; do
    if id -u "$default_user" >/dev/null 2>&1; then
        echo "    -> locking default user '$default_user'"
        usermod -L "$default_user" || true
        usermod -s /usr/sbin/nologin "$default_user" || true
    fi
done

systemctl start mywebapp.socket

sleep 1
curl --silent --fail --max-time 5 http://127.0.0.1/health/alive >/dev/null 2>&1 \
    || echo "    -> (warmup curl skipped — try again in a few seconds)"

echo
echo "    socket status:"
systemctl --no-pager --lines=0 status mywebapp.socket || true
echo
echo "    service status (after warmup):"
systemctl --no-pager --lines=3 status mywebapp.service || true
