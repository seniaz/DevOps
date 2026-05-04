#!/usr/bin/env bash

set -euo pipefail

DEFAULT_PASSWORD="12345678"

upsert_human() {
    local name="$1"
    local extra_groups="$2"
    if id -u "$name" >/dev/null 2>&1; then
        echo "    -> user $name already exists"
    else
        local useradd_args=(--create-home --shell /bin/bash)
        if getent group "$name" >/dev/null 2>&1; then
            useradd_args+=(--no-user-group --gid "$name")
        fi
        if [[ -n "$extra_groups" ]]; then
            useradd_args+=(--groups "$extra_groups")
        fi
        useradd "${useradd_args[@]}" "$name"
        echo "$name:$DEFAULT_PASSWORD" | chpasswd
        chage -d 0 "$name"
        echo "    -> created $name (default password: $DEFAULT_PASSWORD, must change on first login)"
    fi
}

upsert_human student sudo
upsert_human teacher sudo

upsert_human operator ""

if id -u app >/dev/null 2>&1; then
    echo "    -> user app already exists"
else
    useradd --system --no-create-home --shell /usr/sbin/nologin app
    echo "    -> created system user app"
fi
