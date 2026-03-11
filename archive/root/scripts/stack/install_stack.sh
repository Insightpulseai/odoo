#!/usr/bin/env bash
# install_stack.sh - Install Odoo 19 CE + OCA stack
# Usage: ./scripts/stack/install_stack.sh [--tier N] [--module MODULE]
#
# Installs modules in tier order (0-11) for proper dependency resolution.
# Use --tier to install specific tier, --module for single module.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
LOCKFILE="$REPO_ROOT/oca19.lock.json"
STACK_MANIFEST="$REPO_ROOT/stack/odoo19_stack.yaml"

# Configuration
ODOO_BIN="${ODOO_BIN:-odoo}"
DB_NAME="${ODOO_DB:-odoo_core}"
ODOO_CONFIG="${ODOO_CONFIG:-/etc/odoo/odoo.conf}"
ADDONS_PATH="$REPO_ROOT/addons/oca,$REPO_ROOT/addons/ipai,$REPO_ROOT/addons"
DOCKER_MODE="${DOCKER_MODE:-true}"
CONTAINER_NAME="${ODOO_CONTAINER:-odoo-core}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "${BLUE}[STEP]${NC} $1"; }

# Parse arguments
TIER_FILTER=""
MODULE_FILTER=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --tier)
            TIER_FILTER="$2"
            shift 2
            ;;
        --module)
            MODULE_FILTER="$2"
            shift 2
            ;;
        --docker-off)
            DOCKER_MODE="false"
            shift
            ;;
        *)
            log_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Odoo command wrapper
run_odoo() {
    local modules="$1"
    local action="${2:-install}"

    if [[ "$DOCKER_MODE" == "true" ]]; then
        log_info "Running in Docker container: $CONTAINER_NAME"
        if [[ "$action" == "install" ]]; then
            docker compose exec "$CONTAINER_NAME" odoo \
                -d "$DB_NAME" \
                -i "$modules" \
                --stop-after-init \
                --no-http \
                --log-level=warn
        else
            docker compose exec "$CONTAINER_NAME" odoo \
                -d "$DB_NAME" \
                -u "$modules" \
                --stop-after-init \
                --no-http \
                --log-level=warn
        fi
    else
        log_info "Running native Odoo"
        if [[ "$action" == "install" ]]; then
            $ODOO_BIN -c "$ODOO_CONFIG" \
                -d "$DB_NAME" \
                -i "$modules" \
                --stop-after-init \
                --no-http \
                --log-level=warn
        else
            $ODOO_BIN -c "$ODOO_CONFIG" \
                -d "$DB_NAME" \
                -u "$modules" \
                --stop-after-init \
                --no-http \
                --log-level=warn
        fi
    fi
}

# Module definitions by tier
declare -A TIER_MODULES=(
    [0]="date_range,base_exception,base_technical_user,base_user_role,base_tier_validation,base_tier_validation_formula"
    [1]="web_responsive,web_refresher,web_dialog_size,web_advanced_search,web_m2x_options"
    [2]="queue_job,queue_job_cron"
    [4]="report_xlsx,report_xlsx_helper,bi_sql_editor,mis_builder,account_financial_report,account_lock_date,account_fiscal_year"
    [5]="spreadsheet_oca"
    [6]="dms,document_page,document_page_approval"
    [7]="base_rest,graphql_base"
    [8]="mail_activity_board,mail_tracking,mail_debrand"
    [9]="account_reconcile_oca,purchase_request,sale_order_type,project_timeline,project_task_dependency,contract,hr_timesheet_sheet"
    [10]="connector,storage_backend"
    [11]="ai_oca_bridge"
)

TIER_NAMES=(
    [0]="Foundation"
    [1]="Platform UX"
    [2]="Background Processing"
    [4]="Reporting & BI"
    [5]="Spreadsheet"
    [6]="Documents"
    [7]="API Layer"
    [8]="Communication"
    [9]="Workflow Extensions"
    [10]="Integration"
    [11]="AI/ML (Experimental)"
)

# Single module installation
if [[ -n "$MODULE_FILTER" ]]; then
    log_step "Installing single module: $MODULE_FILTER"
    run_odoo "$MODULE_FILTER" "install"
    log_info "Module $MODULE_FILTER installed successfully"
    exit 0
fi

# Tier-filtered installation
if [[ -n "$TIER_FILTER" ]]; then
    if [[ -z "${TIER_MODULES[$TIER_FILTER]:-}" ]]; then
        log_error "Invalid tier: $TIER_FILTER"
        exit 1
    fi
    log_step "Installing Tier $TIER_FILTER: ${TIER_NAMES[$TIER_FILTER]}"
    modules="${TIER_MODULES[$TIER_FILTER]}"
    run_odoo "$modules" "install"
    log_info "Tier $TIER_FILTER installed successfully"
    exit 0
fi

# Full stack installation (all tiers in order)
log_info "Installing full Odoo 19 CE + OCA stack"
log_info "Database: $DB_NAME"
log_info "Docker mode: $DOCKER_MODE"
echo ""

FAILED_TIERS=()
INSTALLED_MODULES=0

for tier in 0 1 2 4 5 6 7 8 9 10 11; do
    if [[ -z "${TIER_MODULES[$tier]:-}" ]]; then
        continue
    fi

    tier_name="${TIER_NAMES[$tier]:-Tier $tier}"
    modules="${TIER_MODULES[$tier]}"
    module_count=$(echo "$modules" | tr ',' '\n' | wc -l)

    log_step "Installing Tier $tier: $tier_name ($module_count modules)"
    echo "  Modules: $modules"

    if run_odoo "$modules" "install" 2>/dev/null; then
        log_info "  Tier $tier completed successfully"
        INSTALLED_MODULES=$((INSTALLED_MODULES + module_count))
    else
        log_warn "  Tier $tier failed - some modules may not be available for 19.0"
        FAILED_TIERS+=("$tier")
    fi
    echo ""
done

# Install IPAI modules
log_step "Installing IPAI platform modules"
IPAI_MODULES="ipai_dev_studio_base,ipai_workspace_core,ipai_platform_approvals,ipai_platform_audit"

if run_odoo "$IPAI_MODULES" "install" 2>/dev/null; then
    log_info "  IPAI modules installed successfully"
else
    log_warn "  Some IPAI modules failed - check dependencies"
fi

# Summary
echo ""
log_info "===== Installation Summary ====="
log_info "Total modules installed: ~$INSTALLED_MODULES"

if [[ ${#FAILED_TIERS[@]} -gt 0 ]]; then
    log_warn "Failed tiers: ${FAILED_TIERS[*]}"
    log_warn "These modules may not have 19.0 support yet"
else
    log_info "All tiers installed successfully"
fi

log_info "Run ./scripts/stack/verify_stack.sh to validate installation"
