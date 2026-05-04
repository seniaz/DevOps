#!/usr/bin/env bash

set -euo pipefail

: "${REPO_DIR:?REPO_DIR must be exported}"
: "${APP_PORT:?APP_PORT must be exported}"

echo "    -> installing systemd units"
install -o root -g root -m 0644 \
    "$REPO_DIR/deploy/systemd/mywebapp.service" \
    /etc/systemd/system/mywebapp.service

install -o root -g root -m 0644 \
    "$REPO_DIR/deploy/systemd/mywebapp.socket" \
    /etc/systemd/system/mywebapp.socket

sed -i -E "s|^ListenStream=127\.0\.0\.1:[0-9]+|ListenStream=127.0.0.1:${APP_PORT}|" \
    /etc/systemd/system/mywebapp.socket

systemctl daemon-reload
systemctl enable mywebapp.socket
systemctl restart mywebapp.socket

echo "    -> installing operator sudoers drop-in"
install -o root -g root -m 0440 \
    "$REPO_DIR/deploy/sudoers/operator" \
    /etc/sudoers.d/operator
visudo -c -f /etc/sudoers.d/operator

echo "    -> systemd + sudoers configured"
