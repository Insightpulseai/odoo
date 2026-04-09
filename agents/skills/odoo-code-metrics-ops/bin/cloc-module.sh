#!/usr/bin/env bash
# odoo-code-metrics-ops: Count lines of code for Odoo modules
# Usage: cloc-module.sh <db-name> [--module <name>]
set -euo pipefail

DB_NAME="${1:?Usage: cloc-module.sh <db-name> [--module <name>]}"
shift

ODOO_BIN="${ODOO_BIN:-vendor/odoo/odoo-bin}"
PYTHON="${PYTHON:-$HOME/.pyenv/versions/odoo-18-dev/bin/python}"
ADDONS_PATH="${ADDONS_PATH:-vendor/odoo/addons,addons/ipai}"

MODULE_FLAG=""
if [ "${1:-}" = "--module" ]; then
  MODULE_FLAG="-c ${2}"
  shift 2
fi

echo "Running cloc for database ${DB_NAME}"
"${PYTHON}" "${ODOO_BIN}" cloc \
  --database="${DB_NAME}" \
  --db_host=localhost --db_port=5432 --db_user=tbwa --db_password=False \
  --addons-path="${ADDONS_PATH}" \
  ${MODULE_FLAG}
