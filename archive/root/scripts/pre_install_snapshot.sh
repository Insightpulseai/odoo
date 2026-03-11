#!/usr/bin/env bash
set -euo pipefail

DB_NAME="${DB_NAME:-odoo}"
DB_USER="${DB_USER:-odoo}"
DB_HOST="${DB_HOST:-odoo-db}"
DB_PORT="${DB_PORT:-5432}"
BACKUP_DIR="${BACKUP_DIR:-./backups}"

MODULE_NAME="${1:-}"
if [ -z "$MODULE_NAME" ]; then
  echo "Usage: $0 <module_name>"
  exit 1
fi

timestamp="$(date +%Y%m%d%H%M%S)"
mkdir -p "${BACKUP_DIR}"

backup_file="${BACKUP_DIR}/${DB_NAME}_preinstall_${MODULE_NAME}_${timestamp}.sql"

echo "📦 Creating pre-install snapshot for module '${MODULE_NAME}'..."
echo "   DB: ${DB_NAME}@${DB_HOST}:${DB_PORT}"
echo "   File: ${backup_file}"

PGPASSWORD="${DB_PASSWORD:-odoo}" pg_dump \
  -h "${DB_HOST}" \
  -p "${DB_PORT}" \
  -U "${DB_USER}" \
  -F p \
  -d "${DB_NAME}" \
  > "${backup_file}"

echo "✅ Snapshot created: ${backup_file}"
