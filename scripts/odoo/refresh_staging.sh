#!/usr/bin/env bash
# ============================================================================
# Staging Refresh — OdooSH Equivalent
# ============================================================================
# Dumps prod DB, sanitizes PII, restores to staging.
# Usage: DB_HOST=... DB_USER=... DB_PASSWORD=... ./refresh_staging.sh
# ============================================================================
set -euo pipefail

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
DB_HOST="${DB_HOST:?ERROR: DB_HOST required}"
DB_USER="${DB_USER:?ERROR: DB_USER required}"
DB_PORT="${DB_PORT:-5432}"
PGPASSWORD="${DB_PASSWORD:?ERROR: DB_PASSWORD required}"
export PGPASSWORD

PROD_DB="odoo"
STAGING_DB="odoo_staging"
TIMESTAMP="$(date +%Y%m%d-%H%M)"
DUMP_FILE="/tmp/odoo_prod_dump_${TIMESTAMP}.sql"
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SANITIZE_SQL="$REPO_ROOT/scripts/odoo/sanitize_staging.sql"

# Forbidden name guard
if [[ "$STAGING_DB" == "odoo_prod" ]]; then
    echo "ERROR: odoo_prod is a forbidden database name."
    exit 1
fi

echo "============================================"
echo " Staging Refresh"
echo " Source: $PROD_DB → Target: $STAGING_DB"
echo " Host:  $DB_HOST:$DB_PORT"
echo " Time:  $TIMESTAMP"
echo "============================================"

# ---------------------------------------------------------------------------
# Phase 1: Dump production
# ---------------------------------------------------------------------------
echo ""
echo ">>> Phase 1: Dumping $PROD_DB..."
pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" \
    -d "$PROD_DB" \
    --no-owner --no-acl --clean --if-exists \
    -f "$DUMP_FILE"

DUMP_SIZE=$(du -h "$DUMP_FILE" | cut -f1)
echo "    Dump complete: $DUMP_FILE ($DUMP_SIZE)"

# ---------------------------------------------------------------------------
# Phase 2: Drop and recreate staging DB
# ---------------------------------------------------------------------------
echo ""
echo ">>> Phase 2: Recreating $STAGING_DB..."

# Terminate existing connections
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c \
    "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='$STAGING_DB' AND pid <> pg_backend_pid();" \
    2>/dev/null || true

# Drop and recreate
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c \
    "DROP DATABASE IF EXISTS $STAGING_DB;"
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c \
    "CREATE DATABASE $STAGING_DB;"

echo "    $STAGING_DB recreated"

# ---------------------------------------------------------------------------
# Phase 3: Restore dump to staging
# ---------------------------------------------------------------------------
echo ""
echo ">>> Phase 3: Restoring to $STAGING_DB..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$STAGING_DB" \
    -f "$DUMP_FILE" \
    --quiet 2>&1 | tail -5

echo "    Restore complete"

# ---------------------------------------------------------------------------
# Phase 4: Neutralize environment
# ---------------------------------------------------------------------------
echo ""
echo ">>> Phase 4: Neutralizing staging environment..."

NEUTRALIZE_SCRIPT="$REPO_ROOT/scripts/odoo/neutralize_environment.sh"

if [[ -x "$NEUTRALIZE_SCRIPT" ]]; then
    DB_HOST="$DB_HOST" DB_USER="$DB_USER" DB_PASSWORD="$PGPASSWORD" DB_PORT="$DB_PORT" \
        bash "$NEUTRALIZE_SCRIPT" --mode=staging --database="$STAGING_DB"
    echo "    Neutralization complete (via neutralize_environment.sh)"
elif [[ -f "$SANITIZE_SQL" ]]; then
    # Fallback to legacy SQL-only sanitization
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$STAGING_DB" \
        -f "$SANITIZE_SQL" \
        2>&1 | grep -E 'UPDATE|NOTICE|ERROR'
    echo "    Sanitization complete (via sanitize_staging.sql fallback)"
else
    echo "    ERROR: No neutralization script or SQL found"
    exit 1
fi

# ---------------------------------------------------------------------------
# Phase 5: Cleanup
# ---------------------------------------------------------------------------
echo ""
echo ">>> Phase 5: Cleanup..."
rm -f "$DUMP_FILE"
echo "    Dump file removed"

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo ""
echo "============================================"
echo " STAGING REFRESH COMPLETE"
echo " Source: $PROD_DB"
echo " Target: $STAGING_DB"
echo " PII:    Sanitized"
echo " Mail:   Suppressed (all ir_mail_server deactivated)"
echo "============================================"
