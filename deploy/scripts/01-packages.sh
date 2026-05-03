#!/usr/bin/env bash

set -euo pipefail

export DEBIAN_FRONTEND=noninteractive

echo "    -> apt update + base packages"
apt-get update -qq
apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    gnupg \
    software-properties-common \
    sudo \
    openssl

if ! command -v python3.12 >/dev/null 2>&1 \
   || ! python3.12 -c 'import sys; assert sys.version_info[:3] >= (3,12,10)' 2>/dev/null
then
    echo "    -> enabling deadsnakes PPA for python3.12.10"
    if ! grep -Rq "deadsnakes" /etc/apt/sources.list.d/ 2>/dev/null; then
        add-apt-repository -y ppa:deadsnakes/ppa
        apt-get update -qq
    fi
    apt-get install -y --no-install-recommends \
        python3.12 \
        python3.12-venv \
        python3.12-dev
fi

echo "    -> python version: $(python3.12 --version)"

echo "    -> MariaDB + nginx"
apt-get install -y --no-install-recommends \
    mariadb-server \
    mariadb-client \
    nginx
