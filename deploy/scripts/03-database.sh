#!/usr/bin/env bash

set -euo pipefail

: "${DB_PASSWORD:?DB_PASSWORD must be exported}"

MYSQL_CONF="/etc/mysql/mariadb.conf.d/50-server.cnf"
if [[ -f "$MYSQL_CONF" ]]; then
    if grep -Eq '^\s*bind-address' "$MYSQL_CONF"; then
        sed -i 's/^\s*bind-address.*/bind-address = 127.0.0.1/' "$MYSQL_CONF"
    else
        sed -i '/^\[mysqld\]/a bind-address = 127.0.0.1' "$MYSQL_CONF"
    fi
    echo "    -> $MYSQL_CONF: bind-address = 127.0.0.1"
fi

systemctl enable --now mariadb
echo "    -> waiting for mariadb to be ready..."
for _ in $(seq 1 30); do
    if mariadb-admin ping >/dev/null 2>&1 || mysqladmin ping >/dev/null 2>&1; then
        break
    fi
    sleep 1
done

echo "    -> creating database and user"
mariadb <<SQL
CREATE DATABASE IF NOT EXISTS mywebapp
    CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'mywebapp'@'localhost'
    IDENTIFIED BY '${DB_PASSWORD}';
ALTER USER 'mywebapp'@'localhost'
    IDENTIFIED BY '${DB_PASSWORD}';
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, INDEX, DROP
    ON mywebapp.* TO 'mywebapp'@'localhost';
FLUSH PRIVILEGES;
SQL

echo "    -> database 'mywebapp' ready, user 'mywebapp'@'localhost' configured"
