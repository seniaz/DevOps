#!/usr/bin/env bash

set -euo pipefail

if [[ $EUID -ne 0 ]]; then
    echo "ERROR: install.sh must be run as root" >&2
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"

N="${STUDENT_NUMBER:-14}"
V2=$(( (N % 2) + 1 ))
V3=$(( (N % 3) + 1 ))
V5=$(( (N % 5) + 1 ))

case "$V5" in
    1) APP_PORT=8080 ;;
    2) APP_PORT=5200 ;;
    3) APP_PORT=3000 ;;
    4) APP_PORT=8000 ;;
    5) APP_PORT=5000 ;;
    *) echo "ERROR: unexpected V5=$V5" >&2; exit 1 ;;
esac

DB_PASSWORD="${DB_PASSWORD:-$(openssl rand -hex 16)}"

export REPO_DIR
export STUDENT_NUMBER="$N"
export V2 V3 V5 APP_PORT DB_PASSWORD

echo "===================================================================="
echo " mywebapp setup"
echo "   N         = $N"
echo "   V2 V3 V5  = $V2 $V3 $V5"
echo "   port      = $APP_PORT"
echo "   DB type   = MariaDB"
echo "   variant   = Simple Inventory (V3=3)"
echo "===================================================================="

run_step() {
    local script="$1"
    echo
    echo "[*] $(basename "$script")"
    bash "$script"
}

run_step "$SCRIPT_DIR/scripts/01-packages.sh"
run_step "$SCRIPT_DIR/scripts/02-users.sh"
run_step "$SCRIPT_DIR/scripts/03-database.sh"
run_step "$SCRIPT_DIR/scripts/04-app.sh"
run_step "$SCRIPT_DIR/scripts/05-systemd.sh"
run_step "$SCRIPT_DIR/scripts/06-nginx.sh"
run_step "$SCRIPT_DIR/scripts/07-finalize.sh"

echo
echo "===================================================================="
echo " Done. Quick checks:"
echo "   curl http://127.0.0.1/                       # root (HTML)"
echo "   curl -H 'Accept: application/json' http://127.0.0.1/items"
echo "   sudo -u operator sudo systemctl status mywebapp.service"
echo "===================================================================="
