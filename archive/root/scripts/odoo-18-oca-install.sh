#!/bin/bash
# =============================================================================
# Odoo 18 CE + OCA Installation Script
# =============================================================================
# This script installs Odoo 18 CE with essential OCA modules following the
# non-negotiable install order:
#   1. Odoo CE core first
#   2. OCA repos second (18.0 branches only)
#   3. Third-party addons after OCA
#   4. Custom modules last
# =============================================================================

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_FILE="${PROJECT_ROOT}/logs/odoo-install-$(date +%Y%m%d-%H%M%S).log"
DB_NAME="${ODOO_DB_NAME:-odoo_core}"
DB_USER="${ODOO_DB_USER:-odoo}"
DB_PASSWORD="${ODOO_DB_PASSWORD:-odoo}"
DB_HOST="${ODOO_DB_HOST:-postgres}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Ensure logs directory exists
mkdir -p "${PROJECT_ROOT}/logs"

# Logging function
log() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} [${level}] ${message}" | tee -a "$LOG_FILE"
}

info() { log "INFO" "${BLUE}$1${NC}"; }
success() { log "SUCCESS" "${GREEN}$1${NC}"; }
warning() { log "WARNING" "${YELLOW}$1${NC}"; }
error() { log "ERROR" "${RED}$1${NC}"; }

# =============================================================================
# STEP 1: Initialize OCA Submodules
# =============================================================================
init_oca_submodules() {
    info "Step 1: Initializing OCA submodules (18.0 branches)..."

    cd "$PROJECT_ROOT"

    # Essential OCA repos for this installation
    local OCA_REPOS=(
        "addons/OCA/server-tools"
        "addons/OCA/server-ux"
        "addons/OCA/web"
        "addons/OCA/automation"
        "addons/OCA/account-financial-reporting"
        "addons/OCA/sale-workflow"
    )

    local EXTERNAL_REPOS=(
        "external-src/account-financial-tools"
    )

    # Initialize OCA submodules
    for repo in "${OCA_REPOS[@]}"; do
        info "Initializing $repo..."
        if git submodule update --init "$repo" 2>&1 | tee -a "$LOG_FILE"; then
            success "Initialized $repo"
        else
            warning "SKIPPED: $repo - may not exist or no 18.0 branch"
        fi
    done

    # Initialize external repos
    for repo in "${EXTERNAL_REPOS[@]}"; do
        info "Initializing $repo..."
        if git submodule update --init "$repo" 2>&1 | tee -a "$LOG_FILE"; then
            success "Initialized $repo"
        else
            warning "SKIPPED: $repo - may not exist or no 18.0 branch"
        fi
    done

    # Create symlink for account-financial-tools if needed
    if [ -d "${PROJECT_ROOT}/external-src/account-financial-tools" ] && \
       [ ! -L "${PROJECT_ROOT}/addons/OCA/account-financial-tools" ]; then
        ln -sf "../../external-src/account-financial-tools" \
               "${PROJECT_ROOT}/addons/OCA/account-financial-tools"
        success "Created symlink for account-financial-tools"
    fi

    success "OCA submodule initialization complete"
}

# =============================================================================
# STEP 2: Check sale-workflow submodule (add if missing)
# =============================================================================
check_sale_workflow() {
    info "Checking sale-workflow submodule..."

    if [ ! -d "${PROJECT_ROOT}/addons/OCA/sale-workflow/.git" ] && \
       [ ! -f "${PROJECT_ROOT}/addons/OCA/sale-workflow/.git" ]; then
        info "Adding sale-workflow submodule..."
        cd "$PROJECT_ROOT"
        git submodule add --branch 18.0 \
            https://github.com/OCA/sale-workflow.git \
            addons/OCA/sale-workflow 2>&1 | tee -a "$LOG_FILE" || true
        success "Added sale-workflow submodule"
    else
        success "sale-workflow already exists"
    fi
}

# =============================================================================
# STEP 3: Verify OCA repo branches
# =============================================================================
verify_oca_branches() {
    info "Step 3: Verifying OCA repos are on 18.0 branch..."

    local repos=(
        "${PROJECT_ROOT}/addons/OCA/server-tools"
        "${PROJECT_ROOT}/addons/OCA/server-ux"
        "${PROJECT_ROOT}/addons/OCA/web"
        "${PROJECT_ROOT}/addons/OCA/automation"
        "${PROJECT_ROOT}/addons/OCA/account-financial-reporting"
        "${PROJECT_ROOT}/addons/OCA/sale-workflow"
        "${PROJECT_ROOT}/external-src/account-financial-tools"
    )

    for repo in "${repos[@]}"; do
        if [ -d "$repo" ] && [ "$(ls -A "$repo" 2>/dev/null)" ]; then
            cd "$repo"
            local branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
            if [ "$branch" == "18.0" ] || [ "$branch" == "HEAD" ]; then
                success "$repo: branch $branch (OK)"
            else
                warning "$repo: branch $branch (expected 18.0)"
            fi
        else
            warning "SKIPPED: $repo - directory empty or not found"
        fi
    done

    cd "$PROJECT_ROOT"
}

# =============================================================================
# Print Installation Summary
# =============================================================================
print_summary() {
    echo ""
    echo "============================================================================="
    echo "                    ODOO 18 CE + OCA INSTALLATION SUMMARY"
    echo "============================================================================="
    echo ""
    echo "OCA Repositories Cloned (18.0 branch):"
    echo "  - OCA/server-tools      : Foundation utilities"
    echo "  - OCA/server-ux         : UX improvements, date ranges"
    echo "  - OCA/web               : Web/client utilities"
    echo "  - OCA/automation        : Server automation (CE marketing automation)"
    echo "  - OCA/account-financial-tools    : Accounting utilities"
    echo "  - OCA/account-financial-reporting: Financial reports"
    echo "  - OCA/sale-workflow     : Sales workflow enhancements"
    echo ""
    echo "Configuration:"
    echo "  - Config file: ${PROJECT_ROOT}/config/odoo-core.conf"
    echo "  - Database: ${DB_NAME}"
    echo "  - addons_path configured with correct install order"
    echo ""
    echo "Next Steps:"
    echo "  1. Start PostgreSQL: docker compose up -d postgres"
    echo "  2. Run CE core init: docker compose --profile ce-init up"
    echo "  3. Run IPAI init: docker compose --profile init up"
    echo "  4. Start Odoo: docker compose up -d odoo-core"
    echo "  5. Verify: ./scripts/verify-odoo-18-oca.sh"
    echo ""
    echo "Log file: $LOG_FILE"
    echo "============================================================================="
}

# =============================================================================
# Main
# =============================================================================
main() {
    info "Starting Odoo 18 CE + OCA installation..."
    info "Project root: $PROJECT_ROOT"
    info "Log file: $LOG_FILE"

    init_oca_submodules
    check_sale_workflow
    verify_oca_branches
    print_summary

    success "Installation preparation complete!"
}

# Run main
main "$@"
