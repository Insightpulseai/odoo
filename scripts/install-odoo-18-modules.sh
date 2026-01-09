#!/bin/bash
# =============================================================================
# Odoo 18 CE + OCA Module Installation Script
# =============================================================================
# Installs core CE apps and OCA modules in proper dependency order:
#   STEP 4: Boot + Install Core Apps (CE)
#   STEP 5: Install OCA Module Set (Curated, Minimal)
# =============================================================================

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_FILE="${PROJECT_ROOT}/logs/module-install-$(date +%Y%m%d-%H%M%S).log"
DB_NAME="${ODOO_DB_NAME:-odoo_core}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Tracking arrays
declare -a INSTALLED_MODULES=()
declare -a SKIPPED_MODULES=()

mkdir -p "${PROJECT_ROOT}/logs"

log() { echo -e "$(date '+%Y-%m-%d %H:%M:%S') [$1] $2" | tee -a "$LOG_FILE"; }
info() { log "INFO" "${BLUE}$1${NC}"; }
success() { log "SUCCESS" "${GREEN}$1${NC}"; }
warning() { log "WARNING" "${YELLOW}$1${NC}"; }
error() { log "ERROR" "${RED}$1${NC}"; }

# =============================================================================
# Install module helper
# =============================================================================
install_module() {
    local module="$1"
    local description="${2:-}"

    info "Installing: $module ${description:+($description)}"

    if docker compose exec -T odoo-core odoo -d "$DB_NAME" -i "$module" --stop-after-init 2>&1 | tee -a "$LOG_FILE"; then
        INSTALLED_MODULES+=("$module")
        success "Installed: $module"
        return 0
    else
        SKIPPED_MODULES+=("$module: install failed")
        warning "SKIPPED: $module - install failed (see log)"
        return 1
    fi
}

# Install multiple modules
install_modules() {
    local modules="$1"
    local description="${2:-}"

    info "Installing modules: $modules ${description:+($description)}"

    if docker compose exec -T odoo-core odoo -d "$DB_NAME" -i "$modules" --stop-after-init 2>&1 | tee -a "$LOG_FILE"; then
        INSTALLED_MODULES+=("$modules")
        success "Installed: $modules"
        return 0
    else
        warning "Some modules in '$modules' may have failed"
        return 1
    fi
}

# =============================================================================
# STEP 4: Install Core CE Apps
# =============================================================================
install_core_ce_apps() {
    echo ""
    echo "============================================================================="
    info "STEP 4: Installing Core CE Apps"
    echo "============================================================================="

    # Minimal core + requested apps
    info "Installing base system modules..."
    install_modules "base,web,mail,contacts" "Base system"

    # Accounting: account (+ invoicing)
    info "Installing accounting modules..."
    install_modules "account" "Accounting core"

    # Sales: sale_management (+ crm)
    info "Installing sales modules..."
    install_modules "sale_management,crm" "Sales + CRM"

    # Marketing: mass_mailing (Email Marketing)
    info "Installing marketing modules..."
    install_modules "mass_mailing" "Email Marketing"

    # Check for marketing_automation (may be Enterprise-only)
    info "Checking for marketing_automation availability..."
    if docker compose exec -T odoo-core python3 -c "
import odoo
from odoo.modules.module import get_module_path
path = get_module_path('marketing_automation')
print('EXISTS' if path else 'NOT_FOUND')
" 2>/dev/null | grep -q "EXISTS"; then
        install_module "marketing_automation" "Marketing Automation"
    else
        warning "marketing_automation NOT FOUND in CE - using OCA/automation instead"
        SKIPPED_MODULES+=("marketing_automation: Enterprise-only, using OCA/automation")
    fi

    success "Core CE apps installation complete"
}

# =============================================================================
# STEP 5: Install OCA Module Set
# =============================================================================
install_oca_modules() {
    echo ""
    echo "============================================================================="
    info "STEP 5: Installing OCA Module Set (Curated, Minimal)"
    echo "============================================================================="

    # A) Base OCA foundations (server-tools / web)
    info "A) Installing OCA Foundation modules..."

    # server-tools essentials
    local server_tools="base_view_inheritance_extension,auditlog,base_exception,base_technical_user"
    install_modules "$server_tools" "server-tools foundation" || true

    # server-ux essentials
    local server_ux="date_range,server_action_mass_edit"
    install_modules "$server_ux" "server-ux foundation" || true

    # web essentials
    local web_modules="web_responsive,web_dialog_size,web_m2x_options,web_no_bubble"
    install_modules "$web_modules" "web UX enhancements" || true

    # B) Accounting OCA (account-financial-tools + account-financial-reporting)
    info "B) Installing Accounting OCA modules..."

    local acct_tools="account_fiscal_year,account_move_name_sequence,account_journal_lock_date"
    install_modules "$acct_tools" "account-financial-tools" || true

    local acct_reporting="account_financial_report"
    install_modules "$acct_reporting" "account-financial-reporting" || true

    # C) Sales OCA (sale-workflow)
    info "C) Installing Sales OCA modules..."

    local sale_workflow="sale_order_type"
    install_modules "$sale_workflow" "sale-workflow" || true

    # sale_order_line_sequence if available
    install_module "sale_order_line_sequence" "sale line sequencing" || true

    # D) Automation OCA (for CE marketing automation needs)
    info "D) Installing Automation OCA modules..."

    # automation_oca - CE alternative to marketing_automation
    if install_module "automation_oca" "OCA automation framework"; then
        success "Installed automation_oca as CE marketing automation alternative"
    else
        warning "automation_oca not available - automated actions via base_automation recommended"
        # Fallback: base_automation is part of core Odoo
        install_module "base_automation" "Odoo automated actions" || true
    fi

    success "OCA module installation complete"
}

# =============================================================================
# Print Installation Report
# =============================================================================
print_report() {
    echo ""
    echo "============================================================================="
    echo "                     INSTALLATION REPORT"
    echo "============================================================================="
    echo ""
    echo "INSTALLED MODULES:"
    for mod in "${INSTALLED_MODULES[@]}"; do
        echo "  ✓ $mod"
    done
    echo ""
    echo "SKIPPED MODULES (with reasons):"
    for mod in "${SKIPPED_MODULES[@]}"; do
        echo "  ⊘ $mod"
    done
    echo ""
    echo "Log file: $LOG_FILE"
    echo "============================================================================="
}

# =============================================================================
# Main
# =============================================================================
main() {
    info "Starting Odoo 18 CE + OCA module installation..."
    info "Database: $DB_NAME"
    info "Log file: $LOG_FILE"

    # Check if docker compose is available
    if ! command -v docker &> /dev/null; then
        error "Docker is not available. Please install Docker first."
        exit 1
    fi

    # Check if odoo-core container is running
    if ! docker compose ps odoo-core 2>/dev/null | grep -q "running"; then
        info "Starting odoo-core container..."
        docker compose up -d odoo-core
        sleep 10
    fi

    install_core_ce_apps
    install_oca_modules
    print_report

    success "Module installation complete!"
}

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
