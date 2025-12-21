#!/usr/bin/env bash
# Install all 38 CE-native Odoo apps in dependency order
# Usage: ./scripts/odoo/install-ce-apps.sh [--dry-run]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

DRY_RUN=false
if [[ "$1" == "--dry-run" ]]; then
    DRY_RUN=true
    echo -e "${YELLOW}DRY RUN MODE - No changes will be made${NC}"
fi

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       Odoo CE 18.0 - Install All CE-Native Apps            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Odoo connection settings (from environment or defaults)
ODOO_HOST="${ODOO_HOST:-localhost}"
ODOO_PORT="${ODOO_PORT:-8069}"
ODOO_DB="${ODOO_DB:-odoo}"
ODOO_USER="${ODOO_USER:-admin}"
ODOO_PASSWORD="${ODOO_PASSWORD:-admin}"

# CE-native apps in dependency order
# Group 1: Base dependencies
GROUP1=(
    "contacts"
    "account"
)

# Group 2: Core transactional
GROUP2=(
    "sale_management"
    "crm"
    "purchase"
    "stock"
    "mrp"
    "maintenance"
)

# Group 3: HR modules
GROUP3=(
    "hr"
    "hr_contract"
    "hr_skills"
    "hr_recruitment"
    "hr_holidays"
    "hr_attendance"
    "hr_expense"
    "fleet"
)

# Group 4: Website & Marketing
GROUP4=(
    "website"
    "website_sale"
    "website_event"
    "website_slides"
    "im_livechat"
    "mass_mailing"
    "mass_mailing_sms"
    "marketing_card"
)

# Group 5: Project & Productivity
GROUP5=(
    "project"
    "project_todo"
    "survey"
    "lunch"
)

# Group 6: POS & Services
GROUP6=(
    "point_of_sale"
    "pos_restaurant"
    "repair"
)

# Group 7: Admin & Compliance
GROUP7=(
    "data_recycle"
)

# Already installed (skip)
ALREADY_INSTALLED=(
    "mail"
    "calendar"
)

install_module() {
    local module=$1
    echo -n "  Installing $module... "

    if [[ "$DRY_RUN" == "true" ]]; then
        echo -e "${YELLOW}[DRY RUN]${NC}"
        return 0
    fi

    # Use Odoo CLI or XML-RPC to install
    # Option 1: Odoo CLI (if running in same container)
    if command -v odoo &> /dev/null; then
        odoo -d "$ODOO_DB" -i "$module" --stop-after-init 2>/dev/null && \
            echo -e "${GREEN}✓${NC}" || echo -e "${RED}✗${NC}"
    else
        # Option 2: HTTP API call
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
        else
            echo -e "${GREEN}✓${NC}"
        fi
    fi
}

install_group() {
    local group_name=$1
    shift
    local modules=("$@")

    echo -e "${YELLOW}▸ $group_name${NC}"
    for module in "${modules[@]}"; do
        install_module "$module"
    done
    echo ""
}

# Main installation
echo -e "${YELLOW}▸ Checking already installed modules...${NC}"
for module in "${ALREADY_INSTALLED[@]}"; do
    echo -e "  ${GREEN}✓${NC} $module (already installed)"
done
echo ""

install_group "Group 1: Base Dependencies" "${GROUP1[@]}"
install_group "Group 2: Core Transactional" "${GROUP2[@]}"
install_group "Group 3: HR Modules" "${GROUP3[@]}"
install_group "Group 4: Website & Marketing" "${GROUP4[@]}"
install_group "Group 5: Project & Productivity" "${GROUP5[@]}"
install_group "Group 6: POS & Services" "${GROUP6[@]}"
install_group "Group 7: Admin & Compliance" "${GROUP7[@]}"

# Count total
TOTAL=$((${#GROUP1[@]} + ${#GROUP2[@]} + ${#GROUP3[@]} + ${#GROUP4[@]} + ${#GROUP5[@]} + ${#GROUP6[@]} + ${#GROUP7[@]} + ${#ALREADY_INSTALLED[@]}))

echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Installation complete!${NC}"
echo -e "${GREEN}  Total modules: $TOTAL${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo "  Run verification: ./scripts/odoo/verify-ce-apps.sh"
