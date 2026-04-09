#!/usr/bin/env bash
# odoo-dataset-neutralize-populate-ops: Populate a database with test data
# Usage: populate-db.sh <db-name> [--size <small|medium|large>] [--models <model1,model2>]
set -euo pipefail

DB_NAME="${1:?Usage: populate-db.sh <db-name> [--size <small|medium|large>]}"
shift

# Safety: refuse to populate production databases
if [ "${DB_NAME}" = "odoo" ] || [ "${DB_NAME}" = "odoo_staging" ]; then
  echo "ERROR: Refusing to populate ${DB_NAME} with test data"
  exit 1
fi

ODOO_BIN="${ODOO_BIN:-vendor/odoo/odoo-bin}"
PYTHON="${PYTHON:-$HOME/.pyenv/versions/odoo-18-dev/bin/python}"
ADDONS_PATH="${ADDONS_PATH:-vendor/odoo/addons,addons/ipai}"

echo "Populating database ${DB_NAME} with test data"
"${PYTHON}" "${ODOO_BIN}" populate \
  --database="${DB_NAME}" \
  --db_host=localhost --db_port=5432 --db_user=tbwa --db_password=False \
  --addons-path="${ADDONS_PATH}" \
  "$@"

echo "Database ${DB_NAME} populated"
