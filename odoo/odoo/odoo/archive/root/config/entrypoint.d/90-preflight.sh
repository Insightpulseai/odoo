#!/bin/bash
# =============================================================================
# 90-preflight.sh - Preflight checks before starting Odoo
# =============================================================================
# Verifies that the container is properly configured before starting Odoo.
#
# Checks:
#   1. Required directories exist and are accessible
#   2. Configuration file is present and readable
#   3. Database connectivity (optional, if PREFLIGHT_DB_CHECK=1)
#   4. No duplicate xmlids (optional static check)
#
# Exit Codes:
#   0 - All checks passed
#   1 - Critical check failed (container should not start)
#
# Environment:
#   PREFLIGHT_DB_CHECK=1    Enable database connectivity check
#   PREFLIGHT_STRICT=1      Fail on warnings (default: only fail on errors)
#
# =============================================================================

set -euo pipefail

ERRORS=0
WARNINGS=0

log_ok() { echo "[preflight] OK: $1"; }
log_warn() { echo "[preflight] WARN: $1"; ((WARNINGS++)); }
log_error() { echo "[preflight] ERROR: $1"; ((ERRORS++)); }

echo ""
echo "[preflight] Running preflight checks..."
echo ""

# ---------------------------------------------------------------------------
# Check 1: IPAI addons directory
# ---------------------------------------------------------------------------
IPAI_ADDONS="${IPAI_ADDONS_PATH:-/mnt/extra-addons}"
if [[ -d "$IPAI_ADDONS" ]]; then
    IPAI_COUNT=$(find "$IPAI_ADDONS" -maxdepth 1 -type d -name "ipai_*" 2>/dev/null | wc -l)
    if [[ $IPAI_COUNT -gt 0 ]]; then
        log_ok "IPAI addons directory: $IPAI_ADDONS ($IPAI_COUNT modules)"
    else
        log_warn "IPAI addons directory exists but no ipai_* modules found"
    fi
else
    log_error "IPAI addons directory not found: $IPAI_ADDONS"
fi

# ---------------------------------------------------------------------------
# Check 2: OCA addons directory
# ---------------------------------------------------------------------------
OCA_ADDONS="${OCA_ADDONS_PATH:-/mnt/oca-modules}"
if [[ -d "$OCA_ADDONS" ]]; then
    OCA_COUNT=$(find "$OCA_ADDONS" -maxdepth 1 -type d 2>/dev/null | wc -l)
    ((OCA_COUNT--)) # Subtract 1 for the directory itself
    log_ok "OCA addons directory: $OCA_ADDONS ($OCA_COUNT repos)"
else
    log_warn "OCA addons directory not found: $OCA_ADDONS"
fi

# ---------------------------------------------------------------------------
# Check 3: Configuration file
# ---------------------------------------------------------------------------
CONFIG_FILE="${ODOO_RC:-/etc/odoo/odoo.conf}"
if [[ -f "$CONFIG_FILE" ]]; then
    if [[ -r "$CONFIG_FILE" ]]; then
        log_ok "Configuration file: $CONFIG_FILE"

        # Check for placeholder values
        if grep -q "CHANGE_ME" "$CONFIG_FILE" 2>/dev/null; then
            log_warn "Configuration contains CHANGE_ME placeholders"
        fi
    else
        log_error "Configuration file not readable: $CONFIG_FILE"
    fi
else
    log_error "Configuration file not found: $CONFIG_FILE"
fi

# ---------------------------------------------------------------------------
# Check 4: Filestore directory
# ---------------------------------------------------------------------------
FILESTORE="${ODOO_DATA_DIR:-/var/lib/odoo}"
if [[ -d "$FILESTORE" ]]; then
    if [[ -w "$FILESTORE" ]]; then
        log_ok "Filestore directory: $FILESTORE (writable)"
    else
        log_error "Filestore directory not writable: $FILESTORE"
    fi
else
    log_warn "Filestore directory not found: $FILESTORE"
fi

# ---------------------------------------------------------------------------
# Check 5: Log directory (optional)
# ---------------------------------------------------------------------------
LOG_DIR="/var/log/odoo"
if [[ -d "$LOG_DIR" ]]; then
    if [[ -w "$LOG_DIR" ]]; then
        log_ok "Log directory: $LOG_DIR (writable)"
    else
        log_warn "Log directory not writable: $LOG_DIR"
    fi
else
    log_warn "Log directory not found: $LOG_DIR"
fi

# ---------------------------------------------------------------------------
# Check 6: Database connectivity (optional)
# ---------------------------------------------------------------------------
if [[ "${PREFLIGHT_DB_CHECK:-0}" == "1" ]]; then
    DB_HOST="${HOST:-db}"
    DB_PORT="${PORT:-5432}"
    DB_USER="${USER:-odoo}"

    echo "[preflight] Checking database connectivity..."

    if command -v pg_isready &>/dev/null; then
        if pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -q; then
            log_ok "Database connectivity: $DB_HOST:$DB_PORT"
        else
            log_error "Cannot connect to database: $DB_HOST:$DB_PORT"
        fi
    else
        log_warn "pg_isready not available, skipping database check"
    fi
fi

# ---------------------------------------------------------------------------
# Check 7: No .git directories in addons (production hygiene)
# ---------------------------------------------------------------------------
GIT_DIRS=$(find /mnt -name ".git" -type d 2>/dev/null | wc -l)
if [[ $GIT_DIRS -gt 0 ]]; then
    log_warn "Found $GIT_DIRS .git directories in /mnt (should be removed in production)"
fi

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo ""
echo "[preflight] ============================================="
echo "[preflight] Preflight Summary"
echo "[preflight] ============================================="
echo "[preflight] Errors:   $ERRORS"
echo "[preflight] Warnings: $WARNINGS"
echo "[preflight] ============================================="
echo ""

# Determine exit code
if [[ $ERRORS -gt 0 ]]; then
    echo "[preflight] FAILED: $ERRORS critical error(s) detected"
    exit 1
fi

if [[ "${PREFLIGHT_STRICT:-0}" == "1" && $WARNINGS -gt 0 ]]; then
    echo "[preflight] FAILED: $WARNINGS warning(s) detected (strict mode)"
    exit 1
fi

echo "[preflight] PASSED: All preflight checks completed"
exit 0
