#!/usr/bin/env bash
# =============================================================================
# Supabase PostgreSQL Restore — Azure VM
# =============================================================================
# Restores a pg_dump backup into the Supabase PostgreSQL container.
# WARNING: This drops and recreates the target database.
#
# Usage:
#   ./restore.sh backups/supabase-full-20260310-020000.sql.gz
#   ./restore.sh --dry-run backups/supabase-full-20260310-020000.sql.gz
#   ./restore.sh --test backups/supabase-full-20260310-020000.sql.gz
#
# --test: Restore to a temporary database (supabase_restore_test), validate,
#         then drop it. Does NOT touch the main database.
#
# SECRETS POLICY: Reads credentials from .env.supabase. Never logged.
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SUPABASE_DIR="${SCRIPT_DIR}/.."
COMPOSE_FILE="${SUPABASE_DIR}/docker-compose.supabase.yml"
ENV_FILE="${SUPABASE_DIR}/.env.supabase"
DRY_RUN=false
TEST_MODE=false
BACKUP_FILE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=true; shift ;;
    --test)    TEST_MODE=true; shift ;;
    -*)        echo "Unknown flag: $1" >&2; exit 1 ;;
    *)         BACKUP_FILE="$1"; shift ;;
  esac
done

if [[ -z "$BACKUP_FILE" ]]; then
  echo "Usage: $0 [--dry-run|--test] <backup-file.sql.gz>" >&2
  exit 1
fi

if [[ ! -f "$BACKUP_FILE" ]]; then
  echo "ERROR: Backup file not found: ${BACKUP_FILE}" >&2
  exit 1
fi

# Verify backup integrity
echo "[$(date -Iseconds)] Verifying backup integrity..."
if ! gzip -t "$BACKUP_FILE" 2>/dev/null; then
  echo "ERROR: Backup file is corrupt: ${BACKUP_FILE}" >&2
  exit 1
fi
echo "[$(date -Iseconds)] Backup integrity OK."

BACKUP_SIZE=$(du -sh "$BACKUP_FILE" | cut -f1)
echo "[$(date -Iseconds)] Restoring from: ${BACKUP_FILE} (${BACKUP_SIZE})"

if [[ "$TEST_MODE" == "true" ]]; then
  TARGET_DB="supabase_restore_test"
  echo "[$(date -Iseconds)] TEST MODE: restoring to temporary database '${TARGET_DB}'"
else
  TARGET_DB="postgres"
  echo "[$(date -Iseconds)] PRODUCTION MODE: restoring to database '${TARGET_DB}'"
fi

if [[ "$DRY_RUN" == "true" ]]; then
  echo "[$(date -Iseconds)] DRY RUN: Would restore ${BACKUP_FILE} to database '${TARGET_DB}'"
  echo "[$(date -Iseconds)] DRY RUN: No changes made."
  exit 0
fi

docker_exec() {
  docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T db "$@"
}

if [[ "$TEST_MODE" == "true" ]]; then
  # Create temporary test database
  echo "[$(date -Iseconds)] Creating temporary test database..."
  docker_exec psql -U postgres -c "DROP DATABASE IF EXISTS ${TARGET_DB};"
  docker_exec psql -U postgres -c "CREATE DATABASE ${TARGET_DB};"

  # Restore into test database
  echo "[$(date -Iseconds)] Restoring into test database..."
  gunzip -c "$BACKUP_FILE" | docker_exec psql -U postgres -d "$TARGET_DB" --quiet

  # Validate: count tables
  TABLE_COUNT=$(docker_exec psql -U postgres -d "$TARGET_DB" -t -A \
    -c "SELECT count(*) FROM information_schema.tables WHERE table_schema NOT IN ('information_schema', 'pg_catalog');")
  echo "[$(date -Iseconds)] Test restore: ${TABLE_COUNT} tables found."

  # Validate: check key schemas exist
  for schema in public auth storage _realtime _analytics; do
    EXISTS=$(docker_exec psql -U postgres -d "$TARGET_DB" -t -A \
      -c "SELECT 1 FROM information_schema.schemata WHERE schema_name='${schema}';" || echo "0")
    if [[ "$EXISTS" == "1" ]]; then
      echo "[$(date -Iseconds)]   Schema '${schema}': OK"
    else
      echo "[$(date -Iseconds)]   Schema '${schema}': MISSING"
    fi
  done

  # Clean up test database
  echo "[$(date -Iseconds)] Dropping test database..."
  docker_exec psql -U postgres -c "DROP DATABASE IF EXISTS ${TARGET_DB};"
  echo "[$(date -Iseconds)] Restore test PASSED."

else
  # Production restore — stop dependent services first
  echo "[$(date -Iseconds)] Stopping Supabase services (keeping db)..."
  docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" \
    stop kong auth rest realtime storage studio meta functions analytics vector imgproxy

  echo "[$(date -Iseconds)] Restoring database..."
  gunzip -c "$BACKUP_FILE" | docker_exec psql -U postgres -d "$TARGET_DB" --quiet

  echo "[$(date -Iseconds)] Restarting all services..."
  docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d

  echo "[$(date -Iseconds)] Waiting 30s for services to stabilize..."
  sleep 30

  # Quick health check
  echo "[$(date -Iseconds)] Running post-restore health check..."
  "${SCRIPT_DIR}/health.sh" || echo "[$(date -Iseconds)] WARNING: Some health checks failed after restore."

  echo "[$(date -Iseconds)] Restore complete."
fi
