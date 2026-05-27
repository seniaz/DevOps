#!/usr/bin/env bash
set -euo pipefail

HOST="${TARGET_HOST:?TARGET_HOST not set}"
USER="${TARGET_USER:-ansible}"
KEY="/opt/deploy_key"
PASS=0
FAIL=0

run_on_target() {
    ssh -i "$KEY" -o StrictHostKeyChecking=no "${USER}@${HOST}" "$@"
}

check() {
    local name="$1"
    shift
    if "$@" > /dev/null 2>&1; then
        echo "  [PASS] $name"
        ((PASS++))
    else
        echo "  [FAIL] $name"
        ((FAIL++))
    fi
}

echo "=== Deployment Verification ==="
echo "Target: ${USER}@${HOST}"
echo ""

echo "-- Service Availability --"
check "Health /alive endpoint" run_on_target "curl -sf http://localhost:5000/health/alive"
check "Health /ready endpoint" run_on_target "curl -sf http://localhost:5000/health/ready"

echo ""
echo "-- Nginx Configuration --"
check "Nginx is running" run_on_target "systemctl is-active nginx"
check "Root endpoint via nginx (port 80)" run_on_target "curl -sf http://localhost:80/"
check "GET /items via nginx" run_on_target "curl -sf -H 'Accept: application/json' http://localhost:80/items"
check "Health endpoints blocked by nginx" run_on_target "! curl -sf http://localhost:80/health/alive"

echo ""
echo "-- Container Status --"
check "mywebapp container is running" run_on_target "sudo docker ps --format '{{.Names}}' | grep -q mywebapp"
check "mywebapp-container systemd service is active" run_on_target "systemctl is-active mywebapp-container.service"

echo ""
echo "-- API Functionality --"
check "POST /items creates item via nginx" run_on_target "curl -sf -X POST http://localhost:80/items -H 'Content-Type: application/json' -d '{\"name\":\"verify-test\",\"quantity\":1}'"
check "GET /items returns created item" run_on_target "curl -sf -H 'Accept: application/json' http://localhost:80/items | grep -q verify-test"

echo ""
echo "================================="
echo "Passed: $PASS"
echo "Failed: $FAIL"
echo "================================="

if [ "$FAIL" -gt 0 ]; then
    echo "VERIFICATION FAILED"
    exit 1
else
    echo "ALL CHECKS PASSED"
fi