#!/usr/bin/env bash
# Example: Full backup and restore cycle
set -euo pipefail

SOURCE_DB="odoo_dev"
RESTORE_DB="odoo_dev_restore_test"
BACKUP_FILE="/tmp/${SOURCE_DB}_$(date +%Y%m%d).sql.gz"

echo "=== Backup ${SOURCE_DB} ==="
pg_dump -h localhost -U tbwa "${SOURCE_DB}" | gzip > "${BACKUP_FILE}"
echo "Backup: ${BACKUP_FILE} ($(ls -lh "${BACKUP_FILE}" | awk '{print $5}'))"

echo "=== Create target database ==="
createdb -h localhost -U tbwa "${RESTORE_DB}" 2>/dev/null || echo "DB already exists"

echo "=== Restore ==="
gunzip -c "${BACKUP_FILE}" | psql -h localhost -U tbwa -d "${RESTORE_DB}" -q

echo "=== Verify restore ==="
psql -h localhost -U tbwa -d "${RESTORE_DB}" -c \
  "SELECT count(*) AS module_count FROM ir_module_module WHERE state='installed'"

echo "=== Cleanup ==="
# dropdb -h localhost -U tbwa "${RESTORE_DB}"
# rm "${BACKUP_FILE}"
