#!/usr/bin/env bash
# Verify all 9 OCA replacement modules are installed
# Usage: ./scripts/odoo/verify-oca-modules.sh

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       OCA Modules Verification                             ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# OCA modules that replace Enterprise functionality
declare -A OCA_MODULES=(
    # Accounting (replaces: accountant)
    ["account_financial_report"]="Accounting - Financial Reports"
    ["mis_builder"]="Accounting - MIS Builder"

    # MRP II (replaces: mrp_workorder)
    ["mrp_multi_level"]="MRP II - Multi Level"
    ["mrp_production_request"]="MRP II - Production Request"

    # HR (replaces: hr_appraisal)
    ["hr_appraisal"]="HR - Appraisal"

    # Timesheets (replaces: timesheet_grid)
    ["hr_timesheet_sheet"]="Timesheets - Sheet"
    ["project_timesheet_time_control"]="Timesheets - Time Control"

    # Subscriptions (replaces: sale_subscription)
    ["sale_subscription"]="Subscriptions"

    # Helpdesk (replaces: helpdesk)
    ["helpdesk_mgmt"]="Helpdesk Management"

    # Planning (replaces: planning)
    ["project_timeline"]="Planning - Timeline"
    ["project_task_dependency"]="Planning - Dependencies"

    # Quality (replaces: quality_control)
    ["quality_control"]="Quality Control"
)

INSTALLED=0
MISSING=0

echo -e "${YELLOW}▸ Checking OCA modules...${NC}"
echo ""

for module in "${!OCA_MODULES[@]}"; do
    description="${OCA_MODULES[$module]}"

    # Check if module is installed via pip
    if pip show "odoo-addon-${module//_/-}" &>/dev/null; then
        echo -e "  ${GREEN}✓${NC} $description ($module)"
        INSTALLED=$((INSTALLED + 1))
    else
        echo -e "  ${RED}✗${NC} $description ($module)"
        MISSING=$((MISSING + 1))
    fi
done

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "  Installed: ${GREEN}$INSTALLED${NC} / ${#OCA_MODULES[@]}"
echo -e "  Missing:   ${RED}$MISSING${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Enterprise replacement summary
echo ""
echo -e "${YELLOW}Enterprise Replacement Status:${NC}"
echo "  accountant      → account_financial_report, mis_builder"
echo "  mrp_workorder   → mrp_multi_level, mrp_production_request"
echo "  hr_appraisal    → hr_appraisal (OCA)"
echo "  timesheet_grid  → hr_timesheet_sheet, project_timesheet_time_control"
echo "  sale_subscription → sale_subscription (OCA)"
echo "  helpdesk        → helpdesk_mgmt"
echo "  planning        → project_timeline, project_task_dependency"
echo "  quality_control → quality_control (OCA)"
echo "  social          → n8n workflows (not OCA)"

if [[ $MISSING -eq 0 ]]; then
    echo ""
    echo -e "${GREEN}✓ All OCA modules verified!${NC}"
    exit 0
else
    echo ""
    echo -e "${YELLOW}! Some OCA modules missing. Run:${NC}"
    echo "  ./scripts/odoo/install-oca-modules.sh all"
    exit 1
fi
