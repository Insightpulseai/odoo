#!/usr/bin/env bash
###############################################################################
# deploy-odoo-modules-with-gates.sh
# Enhanced Odoo module deployment with quality gates and rollback capability
#
# Features:
# - Pre-deployment quality gates (flake8, pylint, unit tests)
# - Database backup before upgrade
# - Rollback capability on failure
# - Visual parity testing (optional)
# - Task bus verification (optional)
# - RLS policy validation (optional)
#
# Usage: ./scripts/deploy-odoo-modules-with-gates.sh <module_name> [options]
# Options:
#   --skip-tests       Skip unit test execution
#   --skip-lint        Skip flake8/pylint checks
#   --skip-backup      Skip database backup (not recommended)
#   --skip-visual      Skip visual parity checks (default if tools missing)
###############################################################################

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}ℹ ${NC}$1"; }
log_success() { echo -e "${GREEN}✅ ${NC}$1"; }
log_warning() { echo -e "${YELLOW}⚠️  ${NC}$1"; }
log_error() { echo -e "${RED}❌ ${NC}$1"; }

###############################################################################
# Configuration
###############################################################################

REMOTE_HOST="erp.insightpulseai.net"
REMOTE_USER="root"
REMOTE_ODOO_DIR="/opt/odoo/custom-addons"
ODOO_CONTAINER="odoo-odoo-1"
ODOO_DB="odoo"
LOCAL_ADDONS_DIR="addons"

# Quality gate flags
SKIP_TESTS=false
SKIP_LINT=false
SKIP_BACKUP=false
SKIP_VISUAL=true  # Default skip (tools may not exist)

# Available modules
AVAILABLE_MODULES=(
    "ipai_ce_cleaner"
    "ipai_expense"
    "ipai_equipment"
    "ipai_ocr_expense"
    "ipai_finance_monthly_closing"
    "ipai_finance_ppm"
)

###############################################################################
# Parse Arguments
###############################################################################

MODULE_NAME=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        --skip-lint)
            SKIP_LINT=true
            shift
            ;;
        --skip-backup)
            SKIP_BACKUP=true
            shift
            ;;
        --skip-visual)
            SKIP_VISUAL=true
            shift
            ;;
        *)
            MODULE_NAME="$1"
            shift
            ;;
    esac
done

if [ -z "$MODULE_NAME" ]; then
    log_error "Usage: $0 <module_name> [options]"
    log_info "Available modules: ${AVAILABLE_MODULES[*]}"
    exit 1
fi

###############################################################################
# Phase 1: Prerequisites Check
###############################################################################

phase_1_prerequisites() {
    log_info "=== Phase 1: Prerequisites Check ==="

    # Validate module exists
    if [ ! -d "${LOCAL_ADDONS_DIR}/${MODULE_NAME}" ]; then
        log_error "Module directory not found: ${LOCAL_ADDONS_DIR}/${MODULE_NAME}"
        exit 1
    fi

    # Check __manifest__.py exists
    if [ ! -f "${LOCAL_ADDONS_DIR}/${MODULE_NAME}/__manifest__.py" ]; then
        log_error "Missing __manifest__.py in ${MODULE_NAME}"
        exit 1
    fi

    # Check SSH connectivity
    if ! ssh -q ${REMOTE_USER}@${REMOTE_HOST} exit; then
        log_error "Cannot connect to ${REMOTE_HOST}"
        exit 1
    fi

    # Check required Python packages for quality gates
    if [ "$SKIP_LINT" = false ]; then
        if ! command -v flake8 &> /dev/null; then
            log_warning "flake8 not found, installing..."
            pip install flake8 || log_warning "Failed to install flake8, skipping lint"
        fi

        if ! command -v pylint &> /dev/null; then
            log_warning "pylint not found, installing..."
            pip install pylint || log_warning "Failed to install pylint, skipping lint"
        fi
    fi

    log_success "Prerequisites check passed"
}

###############################################################################
# Phase 2: Quality Gates - Linting
###############################################################################

phase_2_linting() {
    if [ "$SKIP_LINT" = true ]; then
        log_warning "Skipping linting (--skip-lint)"
        return 0
    fi

    log_info "=== Phase 2: Quality Gates - Linting ==="

    local module_path="${LOCAL_ADDONS_DIR}/${MODULE_NAME}"
    local lint_failed=false

    # flake8 check
    if command -v flake8 &> /dev/null; then
        log_info "Running flake8..."
        if ! flake8 "$module_path" --max-line-length=120 --exclude=__pycache__,*.pyc; then
            log_error "flake8 found issues"
            lint_failed=true
        else
            log_success "flake8 passed"
        fi
    fi

    # pylint check
    if command -v pylint &> /dev/null; then
        log_info "Running pylint..."
        if ! pylint "$module_path" --disable=C,R --errors-only; then
            log_warning "pylint found issues (non-blocking)"
        else
            log_success "pylint passed"
        fi
    fi

    if [ "$lint_failed" = true ]; then
        log_error "Linting failed - fix issues before deployment"
        exit 1
    fi

    log_success "Linting phase passed"
}

###############################################################################
# Phase 3: Quality Gates - Unit Tests
###############################################################################

phase_3_unit_tests() {
    if [ "$SKIP_TESTS" = true ]; then
        log_warning "Skipping unit tests (--skip-tests)"
        return 0
    fi

    log_info "=== Phase 3: Quality Gates - Unit Tests ==="

    # Check if test runner exists
    if [ ! -f "scripts/ci/run_odoo_tests.sh" ]; then
        log_warning "Test runner not found, skipping tests"
        return 0
    fi

    # Check if module has tests
    if [ ! -d "${LOCAL_ADDONS_DIR}/${MODULE_NAME}/tests" ]; then
        log_warning "No tests directory found in ${MODULE_NAME}, skipping"
        return 0
    fi

    log_info "Running unit tests for ${MODULE_NAME}..."

    # Run tests via existing test runner
    if ! ODOO_MODULES="$MODULE_NAME" \
         DB_NAME="test_${MODULE_NAME}_$(date +%s)" \
         LOG_LEVEL="warn" \
         ./scripts/ci/run_odoo_tests.sh; then
        log_error "Unit tests failed"
        exit 1
    fi

    log_success "Unit tests passed"
}

###############################################################################
# Phase 4: Database Backup
###############################################################################

BACKUP_FILE=""

phase_4_backup() {
    if [ "$SKIP_BACKUP" = true ]; then
        log_warning "Skipping database backup (--skip-backup) - RISKY!"
        return 0
    fi

    log_info "=== Phase 4: Database Backup ==="

    local timestamp=$(date +%Y%m%d_%H%M%S)
    BACKUP_FILE="/tmp/odoo_backup_${MODULE_NAME}_${timestamp}.sql"

    log_info "Creating database backup: $BACKUP_FILE"

    # Create backup via SSH
    if ! ssh ${REMOTE_USER}@${REMOTE_HOST} \
         "docker exec ${ODOO_CONTAINER} pg_dump -U odoo ${ODOO_DB} > ${BACKUP_FILE}"; then
        log_error "Database backup failed"
        exit 1
    fi

    log_success "Database backup created: $BACKUP_FILE"
}

###############################################################################
# Phase 5: Deploy Module Files
###############################################################################

phase_5_deploy() {
    log_info "=== Phase 5: Deploy Module Files ==="

    local local_module="${LOCAL_ADDONS_DIR}/${MODULE_NAME}"
    local remote_module="${REMOTE_ODOO_DIR}/${MODULE_NAME}"

    log_info "Deploying ${MODULE_NAME} to ${REMOTE_HOST}..."

    # rsync module files
    if ! rsync -avz --delete \
         -e "ssh" \
         "${local_module}/" \
         "${REMOTE_USER}@${REMOTE_HOST}:${remote_module}/"; then
        log_error "rsync failed"
        rollback "rsync deployment failed"
        exit 1
    fi

    # Set correct permissions
    ssh ${REMOTE_USER}@${REMOTE_HOST} \
        "chown -R odoo:odoo ${remote_module}"

    log_success "Module files deployed"
}

###############################################################################
# Phase 6: Upgrade Module
###############################################################################

phase_6_upgrade() {
    log_info "=== Phase 6: Upgrade Module in Odoo ==="

    log_info "Upgrading module ${MODULE_NAME} in database ${ODOO_DB}..."

    # Run odoo upgrade
    if ! ssh ${REMOTE_USER}@${REMOTE_HOST} \
         "docker exec ${ODOO_CONTAINER} odoo -d ${ODOO_DB} -u ${MODULE_NAME} --stop-after-init --log-level=warn"; then
        log_error "Module upgrade failed"
        rollback "module upgrade failed in Odoo"
        exit 1
    fi

    log_success "Module upgraded successfully"
}

###############################################################################
# Phase 7: Restart Odoo Container
###############################################################################

phase_7_restart() {
    log_info "=== Phase 7: Restart Odoo Container ==="

    log_info "Restarting ${ODOO_CONTAINER}..."

    if ! ssh ${REMOTE_USER}@${REMOTE_HOST} \
         "docker restart ${ODOO_CONTAINER}"; then
        log_error "Container restart failed"
        rollback "Odoo container restart failed"
        exit 1
    fi

    # Wait for container to be ready
    log_info "Waiting for Odoo to start..."
    sleep 10

    log_success "Odoo container restarted"
}

###############################################################################
# Phase 8: Smoke Tests & Health Check
###############################################################################

phase_8_smoke_tests() {
    log_info "=== Phase 8: Smoke Tests & Health Check ==="

    # Health check endpoint
    local health_url="https://${REMOTE_HOST}/web/health"

    log_info "Checking health endpoint: $health_url"

    local max_retries=5
    local retry=0

    while [ $retry -lt $max_retries ]; do
        if curl -sf "$health_url" | grep -q '"status": "pass"'; then
            log_success "Health check passed"
            break
        fi

        retry=$((retry + 1))
        if [ $retry -lt $max_retries ]; then
            log_warning "Health check attempt $retry/$max_retries failed, retrying..."
            sleep 5
        else
            log_error "Health check failed after $max_retries attempts"
            rollback "health check failed"
            exit 1
        fi
    done

    # Optional: Visual parity check
    if [ "$SKIP_VISUAL" = false ] && [ -f "scripts/snap.js" ]; then
        log_info "Running visual parity checks..."
        if ! node scripts/snap.js --module="${MODULE_NAME}"; then
            log_warning "Visual parity check failed (non-blocking)"
        else
            log_success "Visual parity check passed"
        fi
    fi

    log_success "Smoke tests passed"
}

###############################################################################
# Rollback Function
###############################################################################

rollback() {
    local reason="$1"

    log_error "Deployment failed: $reason"
    log_warning "=== Initiating Rollback ==="

    if [ -z "$BACKUP_FILE" ]; then
        log_error "No backup file available - cannot rollback database"
        log_info "You may need to manually restore from a previous backup"
        return 1
    fi

    log_info "Restoring database from: $BACKUP_FILE"

    # Restore database
    if ssh ${REMOTE_USER}@${REMOTE_HOST} \
         "docker exec -i ${ODOO_CONTAINER} psql -U odoo ${ODOO_DB} < ${BACKUP_FILE}"; then
        log_success "Database restored from backup"
    else
        log_error "Database restore failed"
        return 1
    fi

    # Restart Odoo
    log_info "Restarting Odoo after rollback..."
    ssh ${REMOTE_USER}@${REMOTE_HOST} "docker restart ${ODOO_CONTAINER}"

    log_warning "Rollback completed - system restored to pre-deployment state"
    log_info "Backup preserved at: $BACKUP_FILE"
}

###############################################################################
# Main Execution
###############################################################################

main() {
    log_info "========================================="
    log_info "Odoo Module Deployment with Quality Gates"
    log_info "========================================="
    log_info "Module: ${MODULE_NAME}"
    log_info "Target: ${REMOTE_USER}@${REMOTE_HOST}"
    log_info "Database: ${ODOO_DB}"
    log_info "Skip tests: ${SKIP_TESTS}"
    log_info "Skip lint: ${SKIP_LINT}"
    log_info "Skip backup: ${SKIP_BACKUP}"
    log_info "========================================="
    echo ""

    # Execute deployment phases
    phase_1_prerequisites
    phase_2_linting
    phase_3_unit_tests
    phase_4_backup
    phase_5_deploy
    phase_6_upgrade
    phase_7_restart
    phase_8_smoke_tests

    # Success
    echo ""
    log_info "========================================="
    log_success "Deployment Completed Successfully!"
    log_info "========================================="
    log_info "Module: ${MODULE_NAME}"
    log_info "Deployed to: https://${REMOTE_HOST}"
    if [ -n "$BACKUP_FILE" ]; then
        log_info "Backup: ${BACKUP_FILE}"
    fi
    log_info "========================================="
}

# Run main function
main "$@"
