#!/usr/bin/env bash
# odoo-db-ops: Create and initialize an Odoo database
# Usage: db-create.sh <db-name> [--demo]
set -euo pipefail

DB_NAME="${1:?Usage: db-create.sh <db-name> [--demo]}"
DEMO_FLAG="--without-demo all"

if [ "${2:-}" = "--demo" ]; then
  DEMO_FLAG=""
  echo "Creating database ${DB_NAME} WITH demo data"
else
  echo "Creating database ${DB_NAME} WITHOUT demo data"
fi

ODOO_BIN="${ODOO_BIN:-vendor/odoo/odoo-bin}"
PYTHON="${PYTHON:-$HOME/.pyenv/versions/odoo-19-dev/bin/python}"
ADDONS_PATH="${ADDONS_PATH:-vendor/odoo/addons,addons/ipai}"

"${PYTHON}" "${ODOO_BIN}" \
  --database="${DB_NAME}" \
  --db_host=localhost --db_port=5432 --db_user=tbwa --db_password=False \
  --addons-path="${ADDONS_PATH}" \
  --init=base \
  ${DEMO_FLAG} \
  --stop-after-init

echo "Database ${DB_NAME} created and initialized"
