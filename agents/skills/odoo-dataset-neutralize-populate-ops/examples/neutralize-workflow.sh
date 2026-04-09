#!/usr/bin/env bash
# Example: Full neutralization workflow from production copy
set -euo pipefail

SOURCE_DB="odoo"
NEUTRAL_DB="odoo_dev_neutral"

echo "=== Step 1: Backup production ==="
# pg_dump -h localhost -U tbwa "${SOURCE_DB}" | gzip > "/tmp/${SOURCE_DB}_$(date +%Y%m%d).sql.gz"

echo "=== Step 2: Create development copy ==="
# createdb -h localhost -U tbwa "${NEUTRAL_DB}"
# gunzip -c "/tmp/${SOURCE_DB}_$(date +%Y%m%d).sql.gz" | psql -h localhost -U tbwa -d "${NEUTRAL_DB}"

echo "=== Step 3: Neutralize ==="
# ~/.pyenv/versions/odoo-18-dev/bin/python vendor/odoo/odoo-bin neutralize \
#   --database="${NEUTRAL_DB}" \
#   --db_host=localhost --db_port=5432 --db_user=tbwa --db_password=False \
#   --addons-path=vendor/odoo/addons,addons/ipai

echo "=== Step 4: Verify neutralization ==="
# psql -h localhost -U tbwa -d "${NEUTRAL_DB}" -c "SELECT id, smtp_host FROM ir_mail_server"
# psql -h localhost -U tbwa -d "${NEUTRAL_DB}" -c "SELECT login, password FROM res_users LIMIT 5"
# psql -h localhost -U tbwa -d "${NEUTRAL_DB}" -c "SELECT name, active FROM ir_cron LIMIT 10"

echo "=== Step 5: Optionally populate with test data ==="
# ~/.pyenv/versions/odoo-18-dev/bin/python vendor/odoo/odoo-bin populate \
#   --database="${NEUTRAL_DB}" --size small
