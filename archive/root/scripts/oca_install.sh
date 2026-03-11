#!/usr/bin/env bash
# =============================================================================
# OCA Module Installer for Odoo 19.0 CE — InsightPulse AI
# =============================================================================
# Usage:
#   ./scripts/oca_install.sh wave1           # Activate already-present modules
#   ./scripts/oca_install.sh wave2-clone     # Clone OCA repos (LOCAL dev)
#   ./scripts/oca_install.sh wave2-install   # Install Wave 2 modules
#   ./scripts/oca_install.sh wave3-clone     # Clone finance OCA repos (LOCAL dev)
#   ./scripts/oca_install.sh wave3-install   # Install Wave 3 modules
#   ./scripts/oca_install.sh wave4-clone     # Clone nice-to-have repos (LOCAL dev)
#   ./scripts/oca_install.sh wave4-install   # Install Wave 4 modules
#   ./scripts/oca_install.sh status          # Show all OCA module status
#
# Strategy: Direct clone to oca/ dir (NOT git submodules — see commit 5e55c77e)
# Symlink individual modules to addons-oca/ for clean addons_path management.
#
# Environment variables:
#   ODOO_BIN     — path to odoo-bin (default: ./odoo-bin)
#   ODOO_DB      — database name (default: odoo_dev)
#   ODOO_CONF    — odoo config file (default: /etc/odoo/odoo.conf)
#   FORCE=1      — skip confirmation for finance installs
# =============================================================================
set -euo pipefail

# --- Configuration -----------------------------------------------------------
ODOO_BIN="${ODOO_BIN:-./odoo-bin}"
ODOO_DB="${ODOO_DB:-odoo_dev}"
ODOO_CONF="${ODOO_CONF:-/etc/odoo/odoo.conf}"
OCA_DIR="oca"
ADDONS_DIR="addons-oca"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# Colors
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'
log()  { echo -e "${GREEN}[+]${NC} $*"; }
warn() { echo -e "${YELLOW}[!]${NC} $*"; }
err()  { echo -e "${RED}[x]${NC} $*" >&2; }
info() { echo -e "${BLUE}[i]${NC} $*"; }

# --- Functions ---------------------------------------------------------------

clone_oca_repo() {
    local name="$1"
    local path="${OCA_DIR}/${name}"
    local url="https://github.com/OCA/${name}.git"

    if [ -d "$path" ]; then
        warn "Already exists: $path — pulling latest 19.0"
        (cd "$path" && git pull origin 19.0 2>/dev/null || true)
    else
        log "Cloning: OCA/${name} (19.0) -> ${path}"
        mkdir -p "$OCA_DIR"
        git clone --branch 19.0 --depth 1 "$url" "$path"
    fi
}

symlink_module() {
    local source="$1"
    local modname
    modname="$(basename "$1")"
    local target="${ADDONS_DIR}/${modname}"

    mkdir -p "$ADDONS_DIR"
    if [ -L "$target" ] || [ -d "$target" ]; then
        warn "Already linked: $target"
    else
        if [ ! -d "$source" ]; then
            err "Source not found: $source — skipping"
            return 1
        fi
        ln -sf "../${source}" "$target"
        log "Linked: $target -> $source"
    fi
}

install_modules() {
    local modules="$1"
    info "Installing modules on DB=${ODOO_DB}: ${modules}"
    if [ -f "$ODOO_CONF" ]; then
        $ODOO_BIN -c "$ODOO_CONF" -d "$ODOO_DB" -i "$modules" --stop-after-init
    else
        $ODOO_BIN -d "$ODOO_DB" -i "$modules" --stop-after-init
    fi
    log "Install complete: ${modules}"
}

# --- Wave 1: Activate Already-Present Modules --------------------------------
wave1() {
    echo ""
    echo "=========================================="
    echo "  WAVE 1: Activate Already-Present Modules"
    echo "=========================================="
    echo ""
    warn "These modules are already on the instance — just need activation."
    echo ""

    install_modules "account_statement_import_file_reconcile_oca"
    echo ""
    log "Wave 1 complete!"
    info "Optional: also install quality_control_oca,quality_control_stock_oca if needed"
}

# --- Wave 2: Clone OCA Repos (LOCAL) -----------------------------------------
wave2_clone() {
    echo ""
    echo "=========================================="
    echo "  WAVE 2: Clone OCA Repos + Symlinks"
    echo "=========================================="
    echo ""
    cd "$REPO_ROOT"

    # Clone repos (direct clone, NOT submodules)
    clone_oca_repo "reporting-engine"
    clone_oca_repo "web"
    clone_oca_repo "server-ux"
    clone_oca_repo "server-auth"

    # Symlink individual modules
    symlink_module "oca/reporting-engine/report_xlsx"
    symlink_module "oca/reporting-engine/report_xlsx_helper"

    symlink_module "oca/web/web_responsive"
    symlink_module "oca/web/web_dialog_size"
    symlink_module "oca/web/web_environment_ribbon"
    symlink_module "oca/web/web_refresher"
    symlink_module "oca/web/web_search_with_and"

    symlink_module "oca/server-ux/date_range"
    symlink_module "oca/server-ux/base_substate"

    symlink_module "oca/server-auth/auth_session_timeout"

    echo ""
    log "Wave 2 clone complete!"
    info "Next steps:"
    info "  1. Add addons-oca to your addons_path in odoo.conf"
    info "  2. Run: $0 wave2-install"
}

# --- Wave 2: Install Modules -------------------------------------------------
wave2_install() {
    echo ""
    echo "=========================================="
    echo "  WAVE 2: Install UX + Reporting Modules"
    echo "=========================================="
    echo ""

    MODULES="report_xlsx,report_xlsx_helper"
    MODULES="${MODULES},web_responsive,web_dialog_size,web_environment_ribbon,web_refresher,web_search_with_and"
    MODULES="${MODULES},date_range,base_substate"
    MODULES="${MODULES},auth_session_timeout"

    install_modules "$MODULES"

    echo ""
    log "Wave 2 install complete!"
    info "Verify: open Odoo on mobile -> responsive layout"
    info "Verify: export any list view -> XLSX option should appear"
    info "Verify: session timeout after configured idle period"
}

# --- Wave 3: Clone Finance Repos (LOCAL) --------------------------------------
wave3_clone() {
    echo ""
    echo "=========================================="
    echo "  WAVE 3: Clone Finance OCA Repos"
    echo "=========================================="
    echo ""
    cd "$REPO_ROOT"

    clone_oca_repo "account-financial-tools"
    clone_oca_repo "account-financial-reporting"
    clone_oca_repo "bank-payment"

    # Finance tools (from account-financial-tools)
    symlink_module "oca/account-financial-tools/account_move_name_sequence"
    symlink_module "oca/account-financial-tools/account_journal_restrict_mode"
    symlink_module "oca/account-financial-tools/account_usability"
    symlink_module "oca/account-financial-tools/account_move_post_date_user"
    symlink_module "oca/account-financial-tools/account_move_print"

    # Tax balance (from account-financial-reporting, NOT account-financial-tools)
    symlink_module "oca/account-financial-reporting/account_tax_balance"

    # Bank payment
    symlink_module "oca/bank-payment/account_payment_mode"
    symlink_module "oca/bank-payment/account_payment_order"
    symlink_module "oca/bank-payment/account_payment_purchase"
    symlink_module "oca/bank-payment/account_payment_sale"

    echo ""
    log "Wave 3 clone complete!"
    warn "These affect accounting! Test on staging (ODOO_DB=odoo_stage) first!"
    info "  1. Run: ODOO_DB=odoo_stage $0 wave3-install"
    info "  2. Have Finance team (BOM/RIM) verify"
    info "  3. Then: ODOO_DB=odoo_prod $0 wave3-install"
}

# --- Wave 3: Install Finance Modules -----------------------------------------
wave3_install() {
    echo ""
    echo "=========================================="
    echo "  WAVE 3: Install Finance Modules"
    echo "=========================================="
    echo ""
    warn "Installing on DB=${ODOO_DB}"

    if [ "${FORCE:-0}" != "1" ]; then
        err "Finance modules require explicit confirmation."
        err "Run with FORCE=1 to proceed:"
        err "  FORCE=1 ODOO_DB=odoo_stage $0 wave3-install"
        exit 1
    fi

    # Tier 1: no inter-OCA deps
    info "Installing Tier 1: base finance tools..."
    install_modules "account_move_name_sequence,account_journal_restrict_mode,account_usability,account_payment_mode,account_move_post_date_user,account_move_print"

    # Tier 2: depends on Tier 1 + Wave 2 (date_range must be installed)
    info "Installing Tier 2: payment orders + tax balance..."
    install_modules "account_tax_balance,account_payment_order"

    # Tier 3: depends on Tier 2
    info "Installing Tier 3: payment order extensions..."
    install_modules "account_payment_purchase,account_payment_sale"

    echo ""
    log "Wave 3 install complete!"
    info "Verify with Finance team:"
    info "  - Create a payment order batch"
    info "  - Check tax balance report"
    info "  - Verify journal entry sequences unchanged"
    info "  - Check account_move_post_date_user captures posting user"
}

# --- Wave 4: Clone Nice-to-Have Repos (LOCAL) ---------------------------------
wave4_clone() {
    echo ""
    echo "=========================================="
    echo "  WAVE 4: Clone Nice-to-Have OCA Repos"
    echo "=========================================="
    echo ""
    cd "$REPO_ROOT"

    clone_oca_repo "hr"
    clone_oca_repo "knowledge"
    clone_oca_repo "timesheet"

    symlink_module "oca/hr/hr_employee_firstname"
    symlink_module "oca/knowledge/document_url"
    symlink_module "oca/timesheet/hr_timesheet_task_stage"

    echo ""
    log "Wave 4 clone complete!"
    info "Run: $0 wave4-install"
}

# --- Wave 4: Install Nice-to-Have Modules -------------------------------------
wave4_install() {
    echo ""
    echo "=========================================="
    echo "  WAVE 4: Install Nice-to-Have Modules"
    echo "=========================================="
    echo ""

    install_modules "hr_employee_firstname,document_url,hr_timesheet_task_stage"

    echo ""
    log "Wave 4 install complete!"
}

# --- Status -------------------------------------------------------------------
status() {
    echo ""
    echo "=========================================="
    echo "  OCA Module Status"
    echo "=========================================="
    echo ""

    info "Cloned OCA repos in ${OCA_DIR}/..."
    if [ -d "$OCA_DIR" ]; then
        for repo in "$OCA_DIR"/*/; do
            if [ -d "$repo/.git" ]; then
                branch=$(cd "$repo" && git branch --show-current 2>/dev/null || echo "unknown")
                echo -e "  ${GREEN}+${NC} $(basename "$repo") (branch: $branch)"
            fi
        done
    else
        warn "No ${OCA_DIR}/ directory"
    fi

    echo ""
    info "Symlinked modules in ${ADDONS_DIR}/..."
    if [ -d "$ADDONS_DIR" ]; then
        for link in "$ADDONS_DIR"/*; do
            if [ -L "$link" ]; then
                target=$(readlink "$link")
                if [ -d "$link" ]; then
                    echo -e "  ${GREEN}+${NC} $(basename "$link") -> $target"
                else
                    echo -e "  ${RED}x${NC} $(basename "$link") -> $target (BROKEN)"
                fi
            fi
        done
    else
        warn "No ${ADDONS_DIR}/ directory"
    fi

    echo ""
    info "To check installed OCA modules in database:"
    echo "  $ODOO_BIN shell -d $ODOO_DB --stop-after-init <<< \\"
    echo "    \"for m in env['ir.module.module'].search([('state','=','installed'),('author','ilike','OCA')]).sorted('name'): print(f'{m.name:<45} {m.installed_version}')\""
}

# --- Main --------------------------------------------------------------------
case "${1:-help}" in
    wave1)         wave1 ;;
    wave2-clone)   wave2_clone ;;
    wave2-install) wave2_install ;;
    wave3-clone)   wave3_clone ;;
    wave3-install) wave3_install ;;
    wave4-clone)   wave4_clone ;;
    wave4-install) wave4_install ;;
    status)        status ;;
    *)
        echo "OCA Module Installer — Odoo 19.0 CE (InsightPulse AI)"
        echo ""
        echo "Usage: $0 {wave1|wave2-clone|wave2-install|wave3-clone|wave3-install|wave4-clone|wave4-install|status}"
        echo ""
        echo "  wave1          Activate already-present modules (no git needed)"
        echo "  wave2-clone    Clone OCA repos + create symlinks (run on LOCAL dev)"
        echo "  wave2-install  Install Wave 2 modules (UX + reporting)"
        echo "  wave3-clone    Clone finance OCA repos + symlinks (run on LOCAL dev)"
        echo "  wave3-install  Install Wave 3 modules (finance tools — FORCE=1 required)"
        echo "  wave4-clone    Clone nice-to-have OCA repos + symlinks (run on LOCAL dev)"
        echo "  wave4-install  Install Wave 4 modules (nice-to-haves)"
        echo "  status         Show cloned repos + symlink status"
        echo ""
        echo "Environment:"
        echo "  ODOO_DB=odoo_dev    Target database (default: odoo_dev)"
        echo "  ODOO_CONF=...       Odoo config file (default: /etc/odoo/odoo.conf)"
        echo "  FORCE=1             Skip confirmation for finance installs"
        ;;
esac
