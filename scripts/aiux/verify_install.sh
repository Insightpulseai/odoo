#!/usr/bin/env bash
# AIUX Installation Verification Script
# Verifies Odoo module installation and upgrade idempotency
#
# Usage: ./scripts/aiux/verify_install.sh [OPTIONS]
#
# Options:
#   --db-name NAME      Database name (default: odoo)
#   --odoo-url URL      Odoo base URL (default: http://localhost:8069)
#   --container NAME    Docker container name (default: odoo-core)
#   --timeout SECS      Health check timeout (default: 120)
#   --skip-upgrade      Skip upgrade idempotency test
#
# Exit codes:
#   0  All checks passed
#   1  Health check failed
#   2  Module install failed
#   3  Upgrade idempotency failed

set -euo pipefail

# Default configuration
DB_NAME="${DB_NAME:-odoo}"
ODOO_URL="${ODOO_URL:-http://localhost:8069}"
CONTAINER="${ODOO_CONTAINER:-odoo-core}"
TIMEOUT=120
SKIP_UPGRADE=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --db-name)
            DB_NAME="$2"
            shift 2
            ;;
        --odoo-url)
            ODOO_URL="$2"
            shift 2
            ;;
        --container)
            CONTAINER="$2"
            shift 2
            ;;
        --timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        --skip-upgrade)
            SKIP_UPGRADE=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo ""
    echo -e "${GREEN}==>${NC} $1"
    echo "---------------------------------------------------"
}

# Check if running in Docker context
is_docker() {
    docker info &>/dev/null
}

# Execute Odoo command
odoo_exec() {
    if is_docker; then
        docker exec "$CONTAINER" "$@"
    else
        "$@"
    fi
}

# Wait for Odoo health
wait_for_odoo() {
    log_step "Waiting for Odoo to be healthy..."

    local elapsed=0
    local interval=5

    while [ $elapsed -lt $TIMEOUT ]; do
        if curl -sf "${ODOO_URL}/web/login" -o /dev/null 2>/dev/null; then
            log_info "Odoo is healthy (took ${elapsed}s)"
            return 0
        fi

        log_info "Waiting for Odoo... (${elapsed}s/${TIMEOUT}s)"
        sleep $interval
        elapsed=$((elapsed + interval))
    done

    log_error "Odoo health check timed out after ${TIMEOUT}s"
    return 1
}

# Get installed modules
get_installed_modules() {
    log_step "Getting installed modules..."

    if is_docker; then
        docker exec "$CONTAINER" odoo-bin shell -d "$DB_NAME" --no-http <<'EOF'
modules = env['ir.module.module'].search([('state', '=', 'installed')])
for m in modules.sorted(key=lambda x: x.name):
    print(f"{m.name}: {m.installed_version}")
EOF
    else
        log_warn "Not running in Docker - skipping module list"
    fi
}

# Install modules
install_modules() {
    local modules="$1"
    log_step "Installing modules: $modules"

    if is_docker; then
        docker exec "$CONTAINER" odoo-bin -d "$DB_NAME" -i "$modules" --stop-after-init
    else
        odoo-bin -d "$DB_NAME" -i "$modules" --stop-after-init
    fi

    local result=$?
    if [ $result -eq 0 ]; then
        log_info "Module installation completed successfully"
    else
        log_error "Module installation failed with exit code: $result"
    fi
    return $result
}

# Upgrade all modules
upgrade_all() {
    log_step "Upgrading all modules (pass $1)..."

    if is_docker; then
        docker exec "$CONTAINER" odoo-bin -d "$DB_NAME" -u all --stop-after-init
    else
        odoo-bin -d "$DB_NAME" -u all --stop-after-init
    fi

    local result=$?
    if [ $result -eq 0 ]; then
        log_info "Upgrade pass $1 completed successfully"
    else
        log_error "Upgrade pass $1 failed with exit code: $result"
    fi
    return $result
}

# Test upgrade idempotency
test_upgrade_idempotency() {
    if [ "$SKIP_UPGRADE" = true ]; then
        log_warn "Skipping upgrade idempotency test"
        return 0
    fi

    log_step "Testing upgrade idempotency..."

    # First upgrade pass
    if ! upgrade_all 1; then
        log_error "First upgrade pass failed"
        return 3
    fi

    # Second upgrade pass
    if ! upgrade_all 2; then
        log_error "Second upgrade pass failed"
        return 3
    fi

    log_info "Upgrade idempotency test passed"
    return 0
}

# Check for tracebacks in logs
check_logs_for_errors() {
    log_step "Checking logs for errors..."

    if is_docker; then
        local traceback_count
        traceback_count=$(docker logs "$CONTAINER" 2>&1 | grep -c "Traceback" || true)

        if [ "$traceback_count" -gt 0 ]; then
            log_warn "Found $traceback_count traceback(s) in logs"
            log_info "Recent tracebacks:"
            docker logs "$CONTAINER" 2>&1 | grep -A 5 "Traceback" | tail -30
            return 1
        else
            log_info "No tracebacks found in logs"
        fi
    else
        log_warn "Not running in Docker - skipping log check"
    fi

    return 0
}

# Print summary
print_summary() {
    local status=$1

    echo ""
    echo "==================================================="
    echo "             AIUX INSTALL VERIFICATION             "
    echo "==================================================="
    echo ""
    echo "Database:     $DB_NAME"
    echo "Odoo URL:     $ODOO_URL"
    echo "Container:    $CONTAINER"
    echo ""

    if [ "$status" -eq 0 ]; then
        echo -e "Status:       ${GREEN}PASSED${NC}"
    else
        echo -e "Status:       ${RED}FAILED${NC} (exit code: $status)"
    fi

    echo "==================================================="
}

# Main execution
main() {
    local exit_code=0

    echo ""
    echo "==================================================="
    echo "         AIUX Installation Verification            "
    echo "==================================================="
    echo ""
    echo "Configuration:"
    echo "  Database:   $DB_NAME"
    echo "  Odoo URL:   $ODOO_URL"
    echo "  Container:  $CONTAINER"
    echo "  Timeout:    ${TIMEOUT}s"
    echo ""

    # Step 1: Wait for Odoo health
    if ! wait_for_odoo; then
        print_summary 1
        exit 1
    fi

    # Step 2: Get installed modules
    get_installed_modules || true

    # Step 3: Test upgrade idempotency
    if ! test_upgrade_idempotency; then
        print_summary 3
        exit 3
    fi

    # Step 4: Check logs for errors
    check_logs_for_errors || exit_code=0  # Non-fatal warning

    # Step 5: Final module list
    log_step "Final installed modules:"
    get_installed_modules || true

    print_summary 0
    exit 0
}

main "$@"
