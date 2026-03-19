#!/usr/bin/env bash
# =============================================================================
# Supabase PostgreSQL Backup — Azure VM
# =============================================================================
# Creates timestamped pg_dump backups and rotates old ones.
# Designed to run via cron on the Azure VM.
#
# Usage:
#   ./backup.sh                          # Full backup
#   ./backup.sh --schema-only            # Schema only
#   BACKUP_RETAIN_DAYS=14 ./backup.sh    # Override retention
#
# Cron example (daily at 02:00 UTC):
#   0 2 * * * /opt/supabase/scripts/backup.sh >> /var/log/supabase-backup.log 2>&1
#
# SECRETS POLICY: Reads POSTGRES_PASSWORD from .env.supabase. Never logged.
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SUPABASE_DIR="${SCRIPT_DIR}/.."
COMPOSE_FILE="${SUPABASE_DIR}/docker-compose.supabase.yml"
ENV_FILE="${SUPABASE_DIR}/.env.supabase"
BACKUP_DIR="${SUPABASE_DIR}/backups"
RETAIN_DAYS="${BACKUP_RETAIN_DAYS:-7}"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
SCHEMA_ONLY=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --schema-only) SCHEMA_ONLY=true; shift ;;
    *) echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

mkdir -p "$BACKUP_DIR"

echo "[$(date -Iseconds)] Starting Supabase PostgreSQL backup..."

# Determine backup filename
if [[ "$SCHEMA_ONLY" == "true" ]]; then
  BACKUP_FILE="${BACKUP_DIR}/supabase-schema-${TIMESTAMP}.sql.gz"
  DUMP_FLAGS="--schema-only"
else
  BACKUP_FILE="${BACKUP_DIR}/supabase-full-${TIMESTAMP}.sql.gz"
  DUMP_FLAGS="--no-owner --no-acl"
fi

# Run pg_dump inside the container
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" \
  exec -T db pg_dump -U postgres -d postgres $DUMP_FLAGS \
  | gzip > "$BACKUP_FILE"

BACKUP_SIZE=$(du -sh "$BACKUP_FILE" | cut -f1)
echo "[$(date -Iseconds)] Backup created: ${BACKUP_FILE} (${BACKUP_SIZE})"

# Verify backup is not empty
if [[ ! -s "$BACKUP_FILE" ]]; then
  echo "[$(date -Iseconds)] ERROR: Backup file is empty!" >&2
  rm -f "$BACKUP_FILE"
  exit 1
fi

# Quick integrity check: verify gzip can read it
if ! gzip -t "$BACKUP_FILE" 2>/dev/null; then
  echo "[$(date -Iseconds)] ERROR: Backup file is corrupt!" >&2
  exit 1
fi

echo "[$(date -Iseconds)] Backup integrity check passed."

# Rotate old backups
DELETED=0
find "$BACKUP_DIR" -name "supabase-*.sql.gz" -mtime "+${RETAIN_DAYS}" -type f | while read -r old; do
  rm -f "$old"
  DELETED=$((DELETED + 1))
done
echo "[$(date -Iseconds)] Rotated backups older than ${RETAIN_DAYS} days."

# Print summary
echo "[$(date -Iseconds)] Backup complete."
echo "  File:      ${BACKUP_FILE}"
echo "  Size:      ${BACKUP_SIZE}"
echo "  Retention: ${RETAIN_DAYS} days"

# Count existing backups
BACKUP_COUNT=$(find "$BACKUP_DIR" -name "supabase-*.sql.gz" -type f | wc -l)
echo "  Total backups on disk: ${BACKUP_COUNT}"
