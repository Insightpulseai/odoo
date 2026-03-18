#!/usr/bin/env bash
set -euo pipefail

PGHOST="${PGHOST:-localhost}"
PGPORT="${PGPORT:-5432}"
PGUSER="${PGUSER:-odoo}"
PGDATABASE="${PGDATABASE:-odoo}"
PGPASSWORD="${PGPASSWORD:-odoo}"  # default for CI; override via env in workflow
export PGHOST PGPORT PGUSER PGDATABASE PGPASSWORD

echo "▶ Waiting for PostgreSQL on ${PGHOST}:${PGPORT} as ${PGUSER}/${PGDATABASE}..."

for i in {1..30}; do
  if pg_isready -h "${PGHOST}" -p "${PGPORT}" -U "${PGUSER}" >/dev/null 2>&1; then
    echo "✅ PostgreSQL is ready."
    exit 0
  fi
  echo "[${i}/30] Waiting for PostgreSQL..."
  sleep 5
done

echo "❌ PostgreSQL did not become ready in time."
exit 1
