#!/usr/bin/env bash
# odoo-shell-ops: Execute a Python script in Odoo shell context
# Usage: shell-exec.sh <db-name> <script.py>
set -euo pipefail

DB_NAME="${1:?Usage: shell-exec.sh <db-name> <script.py>}"
SCRIPT="${2:?Usage: shell-exec.sh <db-name> <script.py>}"

ODOO_BIN="${ODOO_BIN:-vendor/odoo/odoo-bin}"
PYTHON="${PYTHON:-$HOME/.pyenv/versions/odoo-19-dev/bin/python}"
ADDONS_PATH="${ADDONS_PATH:-vendor/odoo/addons,addons/ipai}"

echo "Executing ${SCRIPT} in Odoo shell (database: ${DB_NAME})"
"${PYTHON}" "${ODOO_BIN}" shell \
  --database="${DB_NAME}" \
  --db_host=localhost --db_port=5432 --db_user=tbwa --db_password=False \
  --addons-path="${ADDONS_PATH}" \
  --no-http \
  < "${SCRIPT}"
