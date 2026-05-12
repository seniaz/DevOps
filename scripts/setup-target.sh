#!/usr/bin/env bash
set -euo pipefail

DB_PASSWORD="${DB_PASSWORD:?Set DB_PASSWORD}"
GHCR_IMAGE="${GHCR_IMAGE:?Set GHCR_IMAGE (e.g. ghcr.io/username/devops)}"

echo "=== Target Node Setup ==="

if ! command -v docker &> /dev/null; then
    apt-get update
    apt-get install -y ca-certificates curl
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
    chmod a+r /etc/apt/keyrings/docker.asc
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] \
      https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
      > /etc/apt/sources.list.d/docker.list
    apt-get update
    apt-get install -y docker-ce docker-ce-cli containerd.io
    systemctl enable --now docker
fi

apt-get install -y mariadb-server mariadb-client nginx
systemctl enable --now mariadb

mariadb -u root << EOF
CREATE DATABASE IF NOT EXISTS mywebapp CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'mywebapp'@'127.0.0.1' IDENTIFIED BY '${DB_PASSWORD}';
GRANT ALL PRIVILEGES ON mywebapp.* TO 'mywebapp'@'127.0.0.1';
FLUSH PRIVILEGES;
EOF
sed -i 's/^bind-address.*/bind-address = 127.0.0.1/' /etc/mysql/mariadb.conf.d/50-server.cnf
systemctl restart mariadb

cat > /etc/nginx/sites-available/mywebapp << 'NGINX'
server {
    listen 80;
    server_name _;
    access_log /var/log/nginx/mywebapp_access.log;
    error_log  /var/log/nginx/mywebapp_error.log;
    location = / {
        proxy_pass http://127.0.0.1:5000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    location /items {
        proxy_pass http://127.0.0.1:5000/items;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    location /health { return 403; }
    location / { return 404; }
}
NGINX
ln -sf /etc/nginx/sites-available/mywebapp /etc/nginx/sites-enabled/mywebapp
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx
systemctl enable nginx

cat > /etc/systemd/system/mywebapp-container.service << EOF
[Unit]
Description=MyWebApp Inventory (containerized)
After=docker.service mariadb.service
Requires=docker.service

[Service]
Type=simple
Restart=on-failure
RestartSec=5
ExecStartPre=-/usr/bin/docker rm -f mywebapp
ExecStart=/usr/bin/docker run --rm --name mywebapp \
    --network host \
    ${GHCR_IMAGE}:stable \
    python -m mywebapp \
      --host 127.0.0.1 --port 5000 \
      --db-host 127.0.0.1 --db-port 3306 \
      --db-user mywebapp \
      --db-password ${DB_PASSWORD} \
      --db-name mywebapp
ExecStop=/usr/bin/docker stop mywebapp

[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload
systemctl enable mywebapp-container.service

for u in ansible teacher operator; do
    id "$u" &>/dev/null || useradd -m -s /bin/bash "$u"
done
id app &>/dev/null || useradd --system --no-create-home --shell /usr/sbin/nologin app

echo "ansible ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/ansible
echo "teacher:12345678" | chpasswd; chage -d 0 teacher; usermod -aG sudo teacher
echo "operator:12345678" | chpasswd; chage -d 0 operator

cat > /etc/sudoers.d/operator << 'SUDOERS'
operator ALL=(ALL) NOPASSWD: /usr/bin/systemctl start mywebapp-container.service
operator ALL=(ALL) NOPASSWD: /usr/bin/systemctl stop mywebapp-container.service
operator ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart mywebapp-container.service
operator ALL=(ALL) NOPASSWD: /usr/bin/systemctl status mywebapp-container.service
operator ALL=(ALL) NOPASSWD: /usr/bin/systemctl reload nginx
SUDOERS

mkdir -p /home/ansible/.ssh
chmod 700 /home/ansible/.ssh
chown -R ansible:ansible /home/ansible/.ssh
echo "14" > /home/ansible/gradebook
chown ansible:ansible /home/ansible/gradebook

echo "=== Setup complete ==="
