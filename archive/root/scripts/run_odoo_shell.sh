#!/usr/bin/env bash
# run_odoo_shell.sh - Execute Python script in Odoo shell
# Works with Docker container or bare-metal Odoo installation
#
# Usage:
#   ./scripts/run_odoo_shell.sh scripts/configure_smtp.py
#   ODOO_DB=odoo_core ./scripts/run_odoo_shell.sh scripts/verify_smtp.py

set -euo pipefail

DB="${ODOO_DB:-odoo}"
SCRIPT="${1:?Usage: scripts/run_odoo_shell.sh <script.py>}"

# Check if script exists
if [ ! -f "$SCRIPT" ]; then
  echo "ERROR: Script not found: $SCRIPT"
  exit 1
fi

# Try Docker first (production pattern)
if command -v docker >/dev/null 2>&1 && docker ps --format '{{.Names}}' | grep -qx 'odoo-ce'; then
  echo "Running via Docker container 'odoo-ce' with database '$DB'"
  docker exec -i odoo-ce odoo shell -d "$DB" < "$SCRIPT"
  exit 0
fi

# Fallback to bare-metal Odoo
ODOO_BIN="${ODOO_BIN:-./odoo/odoo-bin}"
ODOO_CONF="${ODOO_CONF:-./config/odoo.conf}"

if [ -x "$ODOO_BIN" ]; then
  echo "Running via bare-metal Odoo with database '$DB'"
  "$ODOO_BIN" shell -d "$DB" -c "$ODOO_CONF" < "$SCRIPT"
  exit 0
fi

echo "ERROR: Docker container 'odoo-ce' not found and no ODOO_BIN at $ODOO_BIN"
echo ""
echo "Options:"
echo "  1. Start Docker: docker compose up -d"
echo "  2. Set ODOO_BIN: export ODOO_BIN=/path/to/odoo-bin"
exit 1
