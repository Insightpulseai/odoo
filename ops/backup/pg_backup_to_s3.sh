#!/usr/bin/env bash
# pg_backup_to_s3.sh — Backup PostgreSQL to DO Spaces (S3-compatible)
# Usage: ./ops/backup/pg_backup_to_s3.sh
# Requires: PG_DSN, S3_ENDPOINT, S3_BUCKET, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
set -euo pipefail

: "${PG_DSN:?PG_DSN is required (e.g. postgres://user:pass@host:5432/db)}"
: "${S3_ENDPOINT:?S3_ENDPOINT required (e.g. https://nyc3.digitaloceanspaces.com)}"
: "${S3_BUCKET:?S3_BUCKET required}"
: "${S3_PREFIX:=pg-backups}"
: "${AWS_ACCESS_KEY_ID:?AWS_ACCESS_KEY_ID required}"
: "${AWS_SECRET_ACCESS_KEY:?AWS_SECRET_ACCESS_KEY required}"

TS="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="/tmp/pg_${TS}.dump.gz"

echo "[backup] dumping postgres -> ${OUT}"
pg_dump "${PG_DSN}" | gzip -9 > "${OUT}"

echo "[backup] uploading to s3://${S3_BUCKET}/${S3_PREFIX}/"
aws --endpoint-url "${S3_ENDPOINT}" s3 cp \
  "${OUT}" "s3://${S3_BUCKET}/${S3_PREFIX}/pg_${TS}.dump.gz" \
  --only-show-errors

# Clean up local temp file
rm -f "${OUT}"

echo "[backup] done: s3://${S3_BUCKET}/${S3_PREFIX}/pg_${TS}.dump.gz"
