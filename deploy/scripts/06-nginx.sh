#!/usr/bin/env bash

set -euo pipefail

: "${REPO_DIR:?REPO_DIR must be exported}"
: "${APP_PORT:?APP_PORT must be exported}"

rm -f /etc/nginx/sites-enabled/default

echo "    -> installing /etc/nginx/sites-available/mywebapp"
install -o root -g root -m 0644 \
    "$REPO_DIR/deploy/nginx/mywebapp.conf" \
    /etc/nginx/sites-available/mywebapp

sed -i -E "s|proxy_pass http://127\.0\.0\.1:[0-9]+|proxy_pass http://127.0.0.1:${APP_PORT}|g" \
    /etc/nginx/sites-available/mywebapp

ln -sf /etc/nginx/sites-available/mywebapp /etc/nginx/sites-enabled/mywebapp

echo "    -> validating nginx config"
nginx -t

systemctl enable nginx
systemctl restart nginx
echo "    -> nginx listening on :80, proxying to 127.0.0.1:${APP_PORT}"
