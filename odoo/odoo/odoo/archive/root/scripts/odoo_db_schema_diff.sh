#!/usr/bin/env bash
set -euo pipefail
: "${ODOO_PGHOST:?Set ODOO_PGHOST}"
: "${ODOO_PGPORT:?Set ODOO_PGPORT}"
: "${ODOO_PGUSER:?Set ODOO_PGUSER}"
: "${ODOO_PGPASSWORD:?Set ODOO_PGPASSWORD}"
: "${ODOO_PGDB:?Set ODOO_PGDB}"

OUT_DIR="${OUT_DIR:-out/schema}"
mkdir -p "${OUT_DIR}"
export PGPASSWORD="${ODOO_PGPASSWORD}"

pg_dump -h "${ODOO_PGHOST}" -p "${ODOO_PGPORT}" -U "${ODOO_PGUSER}" \
  --schema-only --no-owner --no-privileges "${ODOO_PGDB}" \
  > "${OUT_DIR}/odoo.remote.schema.sql"

if [[ -f "runtime/odoo/expected_schema.sql" ]]; then
  cp runtime/odoo/expected_schema.sql "${OUT_DIR}/odoo.repo.schema.sql"
else
  echo "-- TODO: create runtime/odoo/expected_schema.sql from blessed env" > "${OUT_DIR}/odoo.repo.schema.sql"
fi

diff -u "${OUT_DIR}/odoo.repo.schema.sql" "${OUT_DIR}/odoo.remote.schema.sql"
