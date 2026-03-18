#!/usr/bin/env bash
# Install all Odoo CE core modules in dependency order
# Usage: ./scripts/odoo/install-ce-apps.sh [--dry-run] [--docker CONTAINER_NAME]
#
# Examples:
#   ./scripts/odoo/install-ce-apps.sh --dry-run
#   ./scripts/odoo/install-ce-apps.sh --docker odoo-core
#   ODOO_DB=odoo_marketing ./scripts/odoo/install-ce-apps.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

DRY_RUN=false
DOCKER_MODE=false
DOCKER_CONTAINER=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            echo -e "${YELLOW}DRY RUN MODE - No changes will be made${NC}"
            shift
            ;;
        --docker)
            DOCKER_MODE=true
            DOCKER_CONTAINER="${2:-odoo-core}"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--dry-run] [--docker CONTAINER_NAME]"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       Odoo CE 18.0 - Install All CE Core Modules                  ║${NC}"
echo -e "${BLUE}║       Complete canonical set by functional area                   ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Odoo connection settings (from environment or defaults)
ODOO_HOST="${ODOO_HOST:-localhost}"
ODOO_PORT="${ODOO_PORT:-8069}"
ODOO_DB="${ODOO_DB:-odoo}"
ODOO_USER="${ODOO_USER:-admin}"
ODOO_PASSWORD="${ODOO_PASSWORD:-admin}"

if [[ "$DOCKER_MODE" == "true" ]]; then
    echo -e "${CYAN}Docker Mode: Using container '${DOCKER_CONTAINER}'${NC}"
    echo -e "${CYAN}Database: ${ODOO_DB}${NC}"
else
    echo -e "${CYAN}Host: ${ODOO_HOST}:${ODOO_PORT}${NC}"
    echo -e "${CYAN}Database: ${ODOO_DB}${NC}"
fi
echo ""

# ============================================================================
# CE Core Modules - Organized by Functional Area with Dependencies
# ============================================================================

# Group 0: Base / System (Already installed with Odoo, but included for completeness)
GROUP0_NAME="Base / System"
GROUP0=(
    "base"
    "web"
    "base_setup"
    "base_import"
    "bus"
    "mail"
    "digest"
    "iap"
    "web_tour"
    "web_editor"
    "web_unsplash"
    "portal"
    "resource"
    "calendar"
)

# Group 1: Contacts / CRM / Sales
GROUP1_NAME="Contacts / CRM / Sales"
GROUP1=(
    "contacts"
    "sales_team"
    "crm"
    "sale"
    "sale_management"
    "sale_crm"
)

# Group 2: Accounting / Invoicing / Payments
GROUP2_NAME="Accounting / Invoicing / Payments"
GROUP2=(
    "analytic"
    "account"
    "account_payment"
    "account_check_printing"
    "account_bank_statement_import"
    "account_bank_statement_import_csv"
    "account_bank_statement_import_ofx"
    "account_bank_statement_import_qif"
    "account_batch_payment"
    "account_asset"
    "account_budget"
    "account_tax_python"
)

# Group 3: Purchase
GROUP3_NAME="Purchase"
GROUP3=(
    "purchase"
    "purchase_requisition"
)

# Group 4: Inventory / Warehouse
GROUP4_NAME="Inventory / Warehouse"
GROUP4=(
    "stock"
    "stock_account"
    "stock_landed_costs"
    "stock_picking_batch"
)

# Group 5: Cross-module dependencies (require stock + purchase/sale)
GROUP5_NAME="Cross-Module Integrations"
GROUP5=(
    "sale_stock"
    "sale_purchase"
    "purchase_stock"
)

# Group 6: Manufacturing
GROUP6_NAME="Manufacturing"
GROUP6=(
    "mrp"
    "maintenance"
)

# Group 7: Project / Services / Timesheet
GROUP7_NAME="Project / Services"
GROUP7=(
    "project"
    "project_todo"
    "hr_timesheet"
    "sale_timesheet"
)

# Group 8: HR
GROUP8_NAME="Human Resources"
GROUP8=(
    "hr"
    "hr_contract"
    "hr_holidays"
    "hr_attendance"
    "hr_expense"
    "hr_recruitment"
    "hr_skills"
)

# Group 9: Website / eCommerce
GROUP9_NAME="Website / eCommerce"
GROUP9=(
    "website"
    "website_sale"
    "website_crm"
    "website_blog"
    "website_forum"
    "website_slides"
    "website_event"
)

# Group 10: Marketing
GROUP10_NAME="Marketing"
GROUP10=(
    "mass_mailing"
    "mass_mailing_sms"
    "marketing_card"
    "im_livechat"
)

# Group 11: POS
GROUP11_NAME="Point of Sale"
GROUP11=(
    "point_of_sale"
    "pos_restaurant"
)

# Group 12: Utilities / Misc
GROUP12_NAME="Utilities / Misc"
GROUP12=(
    "survey"
    "lunch"
    "fleet"
    "repair"
    "data_recycle"
)

# Track success/failure
SUCCESS_COUNT=0
FAIL_COUNT=0
SKIP_COUNT=0
FAILED_MODULES=()

install_module() {
    local module=$1
    printf "  %-40s " "$module"

    if [[ "$DRY_RUN" == "true" ]]; then
        echo -e "${YELLOW}[DRY RUN]${NC}"
        ((SUCCESS_COUNT++))
        return 0
    fi

    if [[ "$DOCKER_MODE" == "true" ]]; then
        # Docker mode: exec into container
        result=$(docker exec "$DOCKER_CONTAINER" \
            odoo -d "$ODOO_DB" -i "$module" --stop-after-init 2>&1) || true

        if echo "$result" | grep -q "odoo.modules.loading: Module .* loaded"; then
            echo -e "${GREEN}✓${NC}"
            ((SUCCESS_COUNT++))
            return 0
        elif echo "$result" | grep -q "already"; then
            echo -e "${CYAN}[already installed]${NC}"
            ((SKIP_COUNT++))
            return 0
        else
            echo -e "${RED}✗${NC}"
            ((FAIL_COUNT++))
            FAILED_MODULES+=("$module")
            return 1
        fi
    elif command -v odoo &> /dev/null; then
        # Local odoo binary
        if odoo -d "$ODOO_DB" -i "$module" --stop-after-init 2>/dev/null; then
            echo -e "${GREEN}✓${NC}"
            ((SUCCESS_COUNT++))
        else
            echo -e "${RED}✗${NC}"
            ((FAIL_COUNT++))
            FAILED_MODULES+=("$module")
        fi
    elif command -v odoo-bin &> /dev/null; then
        # Local odoo-bin
        if odoo-bin -d "$ODOO_DB" -i "$module" --stop-after-init 2>/dev/null; then
            echo -e "${GREEN}✓${NC}"
            ((SUCCESS_COUNT++))
        else
            echo -e "${RED}✗${NC}"
            ((FAIL_COUNT++))
            FAILED_MODULES+=("$module")
        fi
    else
        # Fallback: HTTP API call
        response=$(curl -s -X POST "http://${ODOO_HOST}:${ODOO_PORT}/web/dataset/call_kw" \
            -H "Content-Type: application/json" \
            -d "{
                \"jsonrpc\": \"2.0\",
                \"method\": \"call\",
                \"params\": {
                    \"model\": \"ir.module.module\",
                    \"method\": \"button_immediate_install\",
                    \"args\": [[\"$module\"]],
                    \"kwargs\": {}
                },
                \"id\": 1
            }" 2>/dev/null || echo "{}")

        if echo "$response" | grep -q '"error"'; then
            echo -e "${RED}✗${NC}"
            ((FAIL_COUNT++))
            FAILED_MODULES+=("$module")
        else
            echo -e "${GREEN}✓${NC}"
            ((SUCCESS_COUNT++))
        fi
    fi
}

install_group() {
    local group_name=$1
    shift
    local modules=("$@")

    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}▸ $group_name (${#modules[@]} modules)${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    for module in "${modules[@]}"; do
        install_module "$module" || true  # Continue on failure
    done
    echo ""
}

# Calculate total modules
TOTAL_MODULES=$((${#GROUP0[@]} + ${#GROUP1[@]} + ${#GROUP2[@]} + ${#GROUP3[@]} + \
    ${#GROUP4[@]} + ${#GROUP5[@]} + ${#GROUP6[@]} + ${#GROUP7[@]} + ${#GROUP8[@]} + \
    ${#GROUP9[@]} + ${#GROUP10[@]} + ${#GROUP11[@]} + ${#GROUP12[@]}))

echo -e "${CYAN}Total CE core modules to install: ${TOTAL_MODULES}${NC}"
echo ""

# Install in dependency order
install_group "$GROUP0_NAME" "${GROUP0[@]}"
install_group "$GROUP1_NAME" "${GROUP1[@]}"
install_group "$GROUP2_NAME" "${GROUP2[@]}"
install_group "$GROUP3_NAME" "${GROUP3[@]}"
install_group "$GROUP4_NAME" "${GROUP4[@]}"
install_group "$GROUP5_NAME" "${GROUP5[@]}"
install_group "$GROUP6_NAME" "${GROUP6[@]}"
install_group "$GROUP7_NAME" "${GROUP7[@]}"
install_group "$GROUP8_NAME" "${GROUP8[@]}"
install_group "$GROUP9_NAME" "${GROUP9[@]}"
install_group "$GROUP10_NAME" "${GROUP10[@]}"
install_group "$GROUP11_NAME" "${GROUP11[@]}"
install_group "$GROUP12_NAME" "${GROUP12[@]}"

# Summary
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}                         INSTALLATION SUMMARY                       ${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "  ${GREEN}✓ Successful:${NC}  $SUCCESS_COUNT"
echo -e "  ${CYAN}⊘ Skipped:${NC}     $SKIP_COUNT"
echo -e "  ${RED}✗ Failed:${NC}      $FAIL_COUNT"
echo -e "  ─────────────────────"
echo -e "  Total:         $TOTAL_MODULES"
echo ""

if [[ ${#FAILED_MODULES[@]} -gt 0 ]]; then
    echo -e "${RED}Failed modules:${NC}"
    for mod in "${FAILED_MODULES[@]}"; do
        echo -e "  - $mod"
    done
    echo ""
    echo -e "${YELLOW}Note: Some modules may not be available in Odoo 18 CE.${NC}"
    echo -e "${YELLOW}Run with --dry-run first to see the full list.${NC}"
fi

echo ""
echo -e "  ${CYAN}Next steps:${NC}"
echo -e "  - Verify installation: ./scripts/odoo/verify-ce-apps.sh"
echo -e "  - Restart Odoo if needed: docker restart ${DOCKER_CONTAINER:-odoo-core}"
echo ""
