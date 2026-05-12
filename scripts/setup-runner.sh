#!/usr/bin/env bash
set -euo pipefail

echo "=== Self-Hosted Runner Setup ==="

apt-get update
apt-get install -y curl jq git ssh

if ! id runner &>/dev/null; then
    useradd -m -s /bin/bash runner
fi

RUNNER_DIR="/home/runner/actions-runner"
mkdir -p "$RUNNER_DIR"
cd "$RUNNER_DIR"

RUNNER_VERSION=$(curl -s https://api.github.com/repos/actions/runner/releases/latest \
    | jq -r '.tag_name' | sed 's/v//')
curl -o actions-runner-linux-x64.tar.gz -L \
    "https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz"
tar xzf actions-runner-linux-x64.tar.gz
rm actions-runner-linux-x64.tar.gz
chown -R runner:runner "$RUNNER_DIR"

sudo -u runner ssh-keygen -t ed25519 -f /home/runner/.ssh/deploy_key -N "" -C "runner-deploy"

echo ""
echo "=== Done ==="
echo "1. Register: sudo -u runner bash -c 'cd $RUNNER_DIR && ./config.sh --url https://github.com/REPO --token TOKEN'"
echo "2. Service:  cd $RUNNER_DIR && sudo ./svc.sh install runner && sudo ./svc.sh start"
echo "3. Copy key: cat /home/runner/.ssh/deploy_key.pub -> target /home/ansible/.ssh/authorized_keys"
echo "4. Secrets:  SSH_PRIVATE_KEY, TARGET_HOST, TARGET_USER, DB_PASSWORD"
