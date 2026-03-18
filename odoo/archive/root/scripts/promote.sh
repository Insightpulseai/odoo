#!/usr/bin/env bash
# Odoo.sh-Style Database Promotion Script
# Usage: ./scripts/promote.sh --source dev --target stage
#        ./scripts/promote.sh --source stage --target prod

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
die() {
    echo -e "${RED}ERROR: $1${NC}" >&2
    exit 1
}

info() {
    echo -e "${GREEN}INFO: $1${NC}"
}

warn() {
    echo -e "${YELLOW}WARN: $1${NC}"
}

# Parse arguments
SOURCE_ENV=""
TARGET_ENV=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --source)
            SOURCE_ENV="$2"
            shift 2
            ;;
        --target)
            TARGET_ENV="$2"
            shift 2
            ;;
        *)
            die "Unknown option: $1"
            ;;
    esac
done

# Validate inputs
[[ -z "$SOURCE_ENV" ]] && die "Missing --source argument"
[[ -z "$TARGET_ENV" ]] && die "Missing --target argument"
[[ ! "$SOURCE_ENV" =~ ^(dev|stage|prod)$ ]] && die "Invalid source: $SOURCE_ENV (must be dev, stage, or prod)"
[[ ! "$TARGET_ENV" =~ ^(dev|stage|prod)$ ]] && die "Invalid target: $TARGET_ENV (must be dev, stage, or prod)"

# Database names
SOURCE_DB="odoo_${SOURCE_ENV}"
TARGET_DB="odoo_${TARGET_ENV}"
DUMP_FILE="/tmp/${SOURCE_DB}_$(date +%Y%m%d_%H%M%S).dump"

info "Starting promotion: ${SOURCE_ENV} → ${TARGET_ENV}"
info "Source DB: ${SOURCE_DB}"
info "Target DB: ${TARGET_DB}"
info "Dump file: ${DUMP_FILE}"

# Step 1: Backup target database (safety)
info "Step 1/5: Backing up target database ${TARGET_DB}..."
BACKUP_FILE="backups/${TARGET_DB}_pre_promote_$(date +%Y%m%d_%H%M%S).sql"
mkdir -p backups
docker compose exec -T postgres pg_dump -U odoo -d "$TARGET_DB" > "$BACKUP_FILE" || die "Target backup failed"
info "Target backup saved: $BACKUP_FILE"

# Step 2: Dump source database (plain SQL for reliable streaming)
info "Step 2/5: Dumping source database ${SOURCE_DB}..."
docker compose exec -T postgres pg_dump -U odoo -d "$SOURCE_DB" > "$DUMP_FILE" || die "Source dump failed"
info "Source dump complete: $DUMP_FILE"

# Step 3: Drop and recreate target database
info "Step 3/5: Dropping target database ${TARGET_DB}..."
docker compose exec -T postgres psql -U odoo -c "DROP DATABASE IF EXISTS \"$TARGET_DB\";" || die "Drop database failed"
docker compose exec -T postgres psql -U odoo -c "CREATE DATABASE \"$TARGET_DB\" OWNER odoo;" || die "Create database failed"
info "Target database recreated"

# Step 4: Restore source dump to target (plain SQL)
info "Step 4/5: Restoring dump to ${TARGET_DB}..."
cat "$DUMP_FILE" | docker compose exec -T postgres psql -U odoo -d "$TARGET_DB" || die "Restore failed"
info "Restore complete"

# Step 5: Apply environment-specific transformations
info "Step 5/5: Applying ${SOURCE_ENV}->${TARGET_ENV} transformations..."

case "${SOURCE_ENV}->${TARGET_ENV}" in
    "dev->stage")
        info "Applying sanitization for staging..."
        docker compose exec -T postgres psql -U odoo -d "$TARGET_DB" <<'SQL'
-- Disable all cron jobs (staging is CI-only)
UPDATE ir_cron SET active = false;

-- Anonymize test data emails (if any)
UPDATE res_partner SET email = 'test_' || id || '@example.com' WHERE email IS NOT NULL AND email NOT LIKE '%@insightpulseai.%';

-- Clear session data (schema-safe)
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name='ir_sessions') THEN
    EXECUTE 'DELETE FROM ir_sessions';
  END IF;
END $$;
SQL
        info "Sanitization complete: crons disabled, emails anonymized"
        ;;

    "stage->prod")
        info "Applying hardening for production..."
        docker compose exec -T postgres psql -U odoo -d "$TARGET_DB" <<'SQL'
-- Remove demo users (demo data control is config-level via without_demo=all)
UPDATE res_users SET active = false WHERE login ILIKE 'demo%';

-- Enable production crons only (skip demo-related)
UPDATE ir_cron SET active = true WHERE model NOT LIKE '%demo%';

-- Clear all sessions for clean production start (schema-safe)
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name='ir_sessions') THEN
    EXECUTE 'DELETE FROM ir_sessions';
  END IF;
END $$;

-- Reset admin password flag (force password change)
UPDATE res_users SET password_write_date = NOW() WHERE id = 2;
SQL
        info "Hardening complete: demo users deactivated, crons enabled, sessions cleared"
        ;;

    *)
        die "Invalid promotion path: ${SOURCE_ENV}->${TARGET_ENV} (only dev->stage and stage->prod supported)"
        ;;
esac

# Step 6: Verification
info "Verification: Starting ${TARGET_ENV} environment..."
ENV="$TARGET_ENV" ./scripts/up.sh

sleep 10  # Give Odoo time to start

info "Verification: Running smoke tests..."
ENV="$TARGET_ENV" ./scripts/smoke.sh "$TARGET_ENV"

# Cleanup
info "Cleaning up dump file: $DUMP_FILE"
rm -f "$DUMP_FILE"

info "✅ Promotion complete: ${SOURCE_ENV} → ${TARGET_ENV}"
info "Target backup available at: $BACKUP_FILE"
info "To rollback: docker compose exec -T postgres psql -U odoo -d ${TARGET_DB} < $BACKUP_FILE"
