#!/usr/bin/env bash
# pg_restore_from_s3.sh — Restore PostgreSQL from DO Spaces backup
# Usage: S3_KEY=pg-backups/pg_20260207T010000Z.dump.gz ./ops/backup/pg_restore_from_s3.sh
# Requires: PG_DSN, S3_ENDPOINT, S3_BUCKET, S3_KEY, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
set -euo pipefail

: "${PG_DSN:?PG_DSN is required (target DB connection string)}"
: "${S3_ENDPOINT:?S3_ENDPOINT required}"
: "${S3_BUCKET:?S3_BUCKET required}"
: "${S3_KEY:?S3_KEY required (object key in bucket)}"
: "${AWS_ACCESS_KEY_ID:?AWS_ACCESS_KEY_ID required}"
: "${AWS_SECRET_ACCESS_KEY:?AWS_SECRET_ACCESS_KEY required}"

IN="/tmp/restore.dump.gz"

echo "[restore] downloading s3://${S3_BUCKET}/${S3_KEY} -> ${IN}"
aws --endpoint-url "${S3_ENDPOINT}" s3 cp \
  "s3://${S3_BUCKET}/${S3_KEY}" "${IN}" \
  --only-show-errors

echo "[restore] restoring into target database"
gunzip -c "${IN}" | psql "${PG_DSN}"

# Clean up local temp file
rm -f "${IN}"

echo "[restore] complete"
