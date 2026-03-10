#!/bin/bash
# Install EE parity modules from environment variables
# Usage: ./scripts/dev/install-ee-parity-modules.sh [--dry-run]
#
# Environment variables:
#   ODOO_EE_PARITY_OCA_MODULES - Comma-separated list of OCA modules
#   ODOO_EE_PARITY_IPAI_MODULES - Comma-separated list of IPAI modules
#   ODOO_DB_NAME - Database name (default: odoo_core)
#   ODOO_CONTAINER - Container name (default: odoo-core)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Load environment if .env exists
if [[ -f "${REPO_ROOT}/.env" ]]; then
    set -a
    source "${REPO_ROOT}/.env"
    set +a
fi

# Defaults
ODOO_DB_NAME="${ODOO_DB_NAME:-odoo_core}"
ODOO_CONTAINER="${ODOO_CONTAINER:-odoo-core}"
DRY_RUN="${1:-}"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_module() { echo -e "${CYAN}  →${NC} $1"; }

# Build module list from env vars
build_module_list() {
    local oca_modules="${ODOO_EE_PARITY_OCA_MODULES:-}"
    local ipai_modules="${ODOO_EE_PARITY_IPAI_MODULES:-}"

    # Combine and normalize
    local combined=""
    if [[ -n "$oca_modules" ]]; then
        combined="$oca_modules"
    fi
    if [[ -n "$ipai_modules" ]]; then
        if [[ -n "$combined" ]]; then
            combined="${combined},${ipai_modules}"
        else
            combined="$ipai_modules"
        fi
    fi

    # Convert to space-separated, trim whitespace
    echo "$combined" | tr ',' '\n' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | grep -v '^$' | sort -u | tr '\n' ' '
}

install_module() {
    local module="$1"

    if [[ "$DRY_RUN" == "--dry-run" ]]; then
        log_module "[DRY-RUN] Would install: $module"
        return 0
    fi

    log_module "Installing: $module"

    # Try docker compose first
    if command -v docker &>/dev/null && docker ps -q --filter "name=${ODOO_CONTAINER}" 2>/dev/null | grep -q .; then
        docker exec -T "${ODOO_CONTAINER}" odoo -d "${ODOO_DB_NAME}" -u "$module" --stop-after-init 2>&1 || {
            log_warn "Failed to install $module (may not be available yet)"
            return 1
        }
    else
        log_error "Docker container ${ODOO_CONTAINER} not running"
        return 1
    fi
}

main() {
    log_info "EE Parity Module Installer"
    log_info "Database: ${ODOO_DB_NAME}"
    log_info "Container: ${ODOO_CONTAINER}"
    echo ""

    local modules
    modules=$(build_module_list)

    if [[ -z "$modules" ]]; then
        log_error "No modules defined in ODOO_EE_PARITY_OCA_MODULES or ODOO_EE_PARITY_IPAI_MODULES"
        log_info "Set these in .env or export them before running"
        exit 1
    fi

    local count
    count=$(echo "$modules" | wc -w)
    log_info "Modules to install: $count"
    echo ""

    local failed=0
    for module in $modules; do
        install_module "$module" || ((failed++))
    done

    echo ""
    if [[ $failed -gt 0 ]]; then
        log_warn "Completed with $failed failures"
        exit 1
    else
        log_info "All modules installed successfully"
    fi
}

main "$@"
