#!/usr/bin/env bash
# odoo-db-ops: Backup an Odoo database
# Usage: db-backup.sh <db-name> [--output <path>]
set -euo pipefail

DB_NAME="${1:?Usage: db-backup.sh <db-name> [--output <path>]}"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
OUTPUT="${3:-/tmp/${DB_NAME}_${TIMESTAMP}.sql.gz}"

echo "Backing up database ${DB_NAME} to ${OUTPUT}"
pg_dump -h localhost -U tbwa "${DB_NAME}" | gzip > "${OUTPUT}"

SIZE=$(ls -lh "${OUTPUT}" | awk '{print $5}')
echo "Backup complete: ${OUTPUT} (${SIZE})"
