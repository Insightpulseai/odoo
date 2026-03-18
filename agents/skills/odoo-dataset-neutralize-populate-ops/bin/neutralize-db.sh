#!/usr/bin/env bash
# odoo-dataset-neutralize-populate-ops: Neutralize a database copy
# Usage: neutralize-db.sh <db-name>
set -euo pipefail

DB_NAME="${1:?Usage: neutralize-db.sh <db-name>}"

# Safety: refuse to neutralize canonical production database
if [ "${DB_NAME}" = "odoo" ] || [ "${DB_NAME}" = "odoo_staging" ]; then
  echo "ERROR: Refusing to neutralize ${DB_NAME} — work on a copy instead"
  echo "Steps: pg_dump ${DB_NAME} | psql -d ${DB_NAME}_neutralized"
  exit 1
fi

ODOO_BIN="${ODOO_BIN:-vendor/odoo/odoo-bin}"
PYTHON="${PYTHON:-$HOME/.pyenv/versions/odoo-19-dev/bin/python}"
ADDONS_PATH="${ADDONS_PATH:-vendor/odoo/addons,addons/ipai}"

echo "Neutralizing database ${DB_NAME}"
"${PYTHON}" "${ODOO_BIN}" neutralize \
  --database="${DB_NAME}" \
  --db_host=localhost --db_port=5432 --db_user=tbwa --db_password=False \
  --addons-path="${ADDONS_PATH}"

echo "Database ${DB_NAME} neutralized"
echo "Verify: check ir_mail_server, res_users passwords, ir_cron"
