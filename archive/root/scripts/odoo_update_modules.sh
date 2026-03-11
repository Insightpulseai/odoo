#!/usr/bin/env bash
# odoo_update_modules.sh - Install/upgrade Odoo modules
#
# Usage:
#   ODOO_MODULES=ipai_workos_core,ipai_finance_ppm ./scripts/odoo_update_modules.sh
#
# Environment Variables:
#   ODOO_DB      - Database name (default: odoo)
#   ODOO_MODULES - Comma-separated module list (required)
#   ODOO_CONF    - Config file path (default: ./config/odoo.conf)
#   ODOO_BIN     - Odoo binary path (default: ./odoo/odoo-bin)

set -euo pipefail

DB="${ODOO_DB:-odoo}"
CONF="${ODOO_CONF:-./config/odoo.conf}"
ODOO_BIN="${ODOO_BIN:-./odoo/odoo-bin}"
MODULES="${ODOO_MODULES:?Set ODOO_MODULES='mod1,mod2,...'}"

echo "=" * 60
echo "Odoo Module Update"
echo "=" * 60
echo "Database: $DB"
echo "Modules: $MODULES"
echo ""

# Prefer docker container if present
if command -v docker >/dev/null 2>&1 && docker ps --format '{{.Names}}' | grep -qx 'odoo-ce'; then
  echo "Using Docker container 'odoo-ce'"
  docker exec -i odoo-ce odoo -d "$DB" -u "$MODULES" --stop-after-init
  echo ""
  echo "SUCCESS: Modules updated via Docker"
  exit 0
fi

# Bare-metal/systemd path
if [ -x "$ODOO_BIN" ]; then
  echo "Using odoo-bin at $ODOO_BIN"
  "$ODOO_BIN" -c "$CONF" -d "$DB" -u "$MODULES" --stop-after-init
  echo ""
  echo "SUCCESS: Modules updated via bare-metal"
  exit 0
fi

echo "ERROR: Neither Docker container 'odoo-ce' nor ODOO_BIN at $ODOO_BIN available"
echo ""
echo "Options:"
echo "  1. Start Docker: docker compose up -d"
echo "  2. Set ODOO_BIN: export ODOO_BIN=/path/to/odoo-bin"
exit 1
