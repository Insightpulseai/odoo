#!/usr/bin/env bash
set -euo pipefail

DB_CONTAINER="${DB_CONTAINER:-db}"
DB_USER="${DB_USER:-odoo}"
SOURCE_DB="${SOURCE_DB:-odoo}"
VERIFY_DB="${VERIFY_DB:-odoo_verify}"
BACKUP_DIR="${BACKUP_DIR:-/var/backups/odoo}"
MM_WEBHOOK_URL="${MM_WEBHOOK_URL:-}"
N8N_WEBHOOK_URL="${N8N_WEBHOOK_URL:-}"

timestamp=$(date +%Y%m%d_%H%M%S)
backup_file="${BACKUP_DIR}/backup_${SOURCE_DB}_${timestamp}.sql.gz"
status="success"
message="✅ Backup verification succeeded for ${SOURCE_DB} at ${timestamp}"

echo "[INFO] Ensuring backup directory exists: ${BACKUP_DIR}"
docker compose exec -T "${DB_CONTAINER}" mkdir -p "${BACKUP_DIR}"

echo "[INFO] Creating fresh backup..."
docker compose exec -T "${DB_CONTAINER}" \
  pg_dump -U "${DB_USER}" "${SOURCE_DB}" | gzip > "${backup_file}"

echo "[INFO] Dropping verification DB if exists..."
docker compose exec -T "${DB_CONTAINER}" \
  psql -U "${DB_USER}" -c "DROP DATABASE IF EXISTS \"${VERIFY_DB}\";"

echo "[INFO] Creating verification DB..."
docker compose exec -T "${DB_CONTAINER}" \
  psql -U "${DB_USER}" -c "CREATE DATABASE \"${VERIFY_DB}\" TEMPLATE template0;"

echo "[INFO] Restoring backup into ${VERIFY_DB}..."
gunzip -c "${backup_file}" | docker compose exec -T "${DB_CONTAINER}" \
  psql -U "${DB_USER}" "${VERIFY_DB}"

echo "[INFO] Running basic sanity checks..."
docker compose exec -T "${DB_CONTAINER}" \
  psql -U "${DB_USER}" "${VERIFY_DB}" -c "SELECT count(*) FROM ir_module_module;" >/dev/null

# If we get here, all good
echo "[OK] Backup verification succeeded."

# Mattermost notification
if [[ -n "${MM_WEBHOOK_URL}" ]]; then
  payload=$(cat <<EOF
{"text": "${message}"}
EOF
)
  curl -s -X POST -H 'Content-Type: application/json' \
    -d "${payload}" "${MM_WEBHOOK_URL}" >/dev/null || true
fi

# n8n ingest (new)
if [[ -n "${N8N_WEBHOOK_URL}" ]]; then
  n8n_payload=$(cat <<EOF
{
  "source_db": "${SOURCE_DB}",
  "verify_db": "${VERIFY_DB}",
  "verified_at": "${timestamp}",
  "success": true,
  "backup_file": "${backup_file}",
  "message": "${message}"
}
EOF
)
  curl -s -X POST -H 'Content-Type: application/json' \
    -d "${n8n_payload}" "${N8N_WEBHOOK_URL}" >/dev/null || true
fi
