#!/usr/bin/env bash
# odoo-shell-ops: Execute an inline Python expression in Odoo shell
# Usage: shell-query.sh <db-name> "<python-expression>"
set -euo pipefail

DB_NAME="${1:?Usage: shell-query.sh <db-name> \"<python-expression>\"}"
EXPRESSION="${2:?Usage: shell-query.sh <db-name> \"<python-expression>\"}"

ODOO_BIN="${ODOO_BIN:-vendor/odoo/odoo-bin}"
PYTHON="${PYTHON:-$HOME/.pyenv/versions/odoo-19-dev/bin/python}"
ADDONS_PATH="${ADDONS_PATH:-vendor/odoo/addons,addons/ipai}"

echo "${EXPRESSION}" | "${PYTHON}" "${ODOO_BIN}" shell \
  --database="${DB_NAME}" \
  --db_host=localhost --db_port=5432 --db_user=tbwa --db_password=False \
  --addons-path="${ADDONS_PATH}" \
  --no-http
