#!/usr/bin/env bash
set -euo pipefail

missing=0

req_vars=(
  # Odoo DB (prod/stage/dev depending on runner env)
  ODOO_DB_HOST
  ODOO_DB_PORT
  ODOO_DB_USER
  ODOO_DB_PASSWORD
  ODOO_DB_NAME
  # Supabase DB (direct Postgres)
  SUPABASE_DB_HOST
  SUPABASE_DB_PORT
  SUPABASE_DB_USER
  SUPABASE_DB_PASSWORD
  SUPABASE_DB_NAME
  SUPABASE_DB_SSLMODE
)

for v in "${req_vars[@]}"; do
  if [[ -z "${!v:-}" ]]; then
    echo "Missing env: $v" >&2
    missing=1
  fi
done

if [[ "$missing" -ne 0 ]]; then
  echo "Schema drift env check failed. Set required variables in CI secrets or runner env." >&2
  exit 2
fi

echo "Schema drift env check: OK"
