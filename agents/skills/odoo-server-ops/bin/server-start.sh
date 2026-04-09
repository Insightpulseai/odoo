#!/usr/bin/env bash
# odoo-server-ops: Start Odoo server (local dev)
# Usage: server-start.sh [--database <db>] [--port <port>] [--dev]
set -euo pipefail

DB="${2:-odoo_dev}"
PORT="${4:-8069}"
DEV_MODE=""

# Parse flags
while [[ $# -gt 0 ]]; do
  case "$1" in
    --database) DB="$2"; shift 2 ;;
    --port) PORT="$2"; shift 2 ;;
    --dev) DEV_MODE="--dev=xml,reload,qweb"; shift ;;
    *) shift ;;
  esac
done

ODOO_BIN="${ODOO_BIN:-vendor/odoo/odoo-bin}"
PYTHON="${PYTHON:-$HOME/.pyenv/versions/odoo-18-dev/bin/python}"
ADDONS_PATH="${ADDONS_PATH:-vendor/odoo/addons,addons/ipai}"

echo "Starting Odoo CE 19 on port ${PORT} with database ${DB}"
exec "${PYTHON}" "${ODOO_BIN}" \
  --database="${DB}" \
  --db_host=localhost --db_port=5432 --db_user=tbwa --db_password=False \
  --http-port="${PORT}" \
  --addons-path="${ADDONS_PATH}" \
  --data-dir=/tmp/odoo-data \
  ${DEV_MODE}
