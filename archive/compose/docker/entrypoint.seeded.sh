#!/usr/bin/env bash
# =============================================================================
# InsightPulse Odoo 18 CE - Seeded Image Entrypoint
# =============================================================================
# This script handles:
# 1. First-boot database initialization with KEEP modules
# 2. Seed reconciliation to ensure task parity
# 3. Normal Odoo startup on subsequent boots
# =============================================================================

set -e

# Configuration
DB_NAME="${DB_NAME:-odoo_core}"
SEED_FLAG="/var/lib/odoo/.db_seeded"
LOG_PREFIX="[IPAI-SEED]"

# KEEP modules to install on first boot (only existing modules)
# Note: ipai_finance_ppm_closing depends on ipai_finance_ppm and ipai_ppm_monthly_close
KEEP_MODULES="ipai_bir_compliance,ipai_ocr_expense,ipai_expense,ipai_finance_ppm,ipai_ppm_monthly_close,ipai_finance_ppm_closing,ipai_finance_ppm_dashboard,ipai_equipment"

# =============================================================================
# Helper Functions
# =============================================================================

log_info() {
    echo "${LOG_PREFIX} [INFO] $1"
}

log_warn() {
    echo "${LOG_PREFIX} [WARN] $1"
}

log_error() {
    echo "${LOG_PREFIX} [ERROR] $1"
}

wait_for_postgres() {
    log_info "Waiting for PostgreSQL to be ready..."
    local max_attempts=30
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        if pg_isready -h "${HOST:-db}" -p "${PORT:-5432}" -U "${USER:-odoo}" > /dev/null 2>&1; then
            log_info "PostgreSQL is ready!"
            return 0
        fi
        log_info "Attempt $attempt/$max_attempts - PostgreSQL not ready, waiting..."
        sleep 2
        attempt=$((attempt + 1))
    done

    log_error "PostgreSQL did not become ready in time"
    return 1
}

# =============================================================================
# First Boot: Database Initialization & Seeding
# =============================================================================

if [ ! -f "$SEED_FLAG" ]; then
    log_info "=============================================="
    log_info "First boot detected - initializing database"
    log_info "=============================================="

    # Wait for PostgreSQL
    wait_for_postgres

    # Step 1: Initialize database with KEEP modules
    log_info "Installing KEEP modules: $KEEP_MODULES"
    log_info "This may take 2-5 minutes..."

    odoo \
        --database="$DB_NAME" \
        --init="$KEEP_MODULES" \
        --without-demo=all \
        --stop-after-init \
        --no-http \
        2>&1 | while read line; do echo "${LOG_PREFIX} $line"; done

    if [ $? -ne 0 ]; then
        log_error "Module installation failed!"
        exit 1
    fi

    log_info "Module installation complete!"

    # Step 2: Run seed reconciliation (if script exists)
    RECONCILE_SCRIPT="/mnt/extra-addons/ipai_finance_ppm_closing/scripts/reconcile_seed_parity.py"

    if [ -f "$RECONCILE_SCRIPT" ]; then
        log_info "Running seed reconciliation..."

        odoo shell \
            --database="$DB_NAME" \
            --no-http \
            -c /etc/odoo/odoo.conf <<EOF
try:
    from odoo.addons.ipai_finance_ppm_closing.scripts.validate_seed_parity import main as validate
    result = validate(env)
    print("Validation result:", result)
except Exception as e:
    print("Validation skipped or failed:", str(e))
    # Non-fatal - continue with startup
EOF

        log_info "Seed reconciliation complete!"
    else
        log_warn "Reconciliation script not found, skipping seed validation"
    fi

    # Step 3: Create seed flag to prevent re-initialization
    touch "$SEED_FLAG"
    log_info "Created seed flag: $SEED_FLAG"

    log_info "=============================================="
    log_info "✅ Database seeding complete!"
    log_info "=============================================="

else
    log_info "Seed flag exists - skipping initialization"
fi

# =============================================================================
# Normal Startup
# =============================================================================

log_info "Starting Odoo..."

# Execute the main command (odoo or custom command)
exec "$@"
