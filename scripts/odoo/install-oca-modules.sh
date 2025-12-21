#!/usr/bin/env bash
# Install OCA modules to replace Odoo Enterprise functionality
# Usage: ./scripts/odoo/install-oca-modules.sh [category]
# Categories: accounting, mrp, hr, timesheets, subscriptions, helpdesk, planning, quality, all

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

CATEGORY="${1:-all}"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       OCA Modules Installation                             ║${NC}"
echo -e "${BLUE}║       Category: ${YELLOW}$CATEGORY${BLUE}                                    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check Python environment
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo -e "${YELLOW}Warning: Not in a virtual environment${NC}"
    echo "Consider activating your Odoo venv first"
fi

install_accounting() {
    echo -e "${YELLOW}▸ Installing Accounting modules (replaces: accountant)${NC}"
    pip install --no-deps \
        odoo-addon-account-financial-report \
        odoo-addon-mis-builder \
        odoo-addon-mis-builder-budget \
        odoo-addon-account-asset-management \
        odoo-addon-account-reconcile-oca
    echo ""
}

install_mrp() {
    echo -e "${YELLOW}▸ Installing MRP II modules (replaces: mrp_workorder)${NC}"
    pip install --no-deps \
        odoo-addon-mrp-multi-level \
        odoo-addon-mrp-multi-level-estimate \
        odoo-addon-mrp-production-request \
        odoo-addon-mrp-workorder-sequence
    echo ""
}

install_hr() {
    echo -e "${YELLOW}▸ Installing HR Appraisal modules (replaces: hr_appraisal)${NC}"
    pip install --no-deps \
        odoo-addon-hr-appraisal
    echo ""
}

install_timesheets() {
    echo -e "${YELLOW}▸ Installing Timesheet modules (replaces: timesheet_grid)${NC}"
    pip install --no-deps \
        odoo-addon-hr-timesheet-sheet \
        odoo-addon-hr-timesheet-task-required \
        odoo-addon-project-timesheet-time-control
    echo ""
}

install_subscriptions() {
    echo -e "${YELLOW}▸ Installing Subscription modules (replaces: sale_subscription)${NC}"
    pip install --no-deps \
        odoo-addon-sale-subscription
    echo ""
}

install_helpdesk() {
    echo -e "${YELLOW}▸ Installing Helpdesk modules (replaces: helpdesk)${NC}"
    pip install --no-deps \
        odoo-addon-helpdesk-mgmt \
        odoo-addon-helpdesk-mgmt-timesheet \
        odoo-addon-helpdesk-mgmt-project
    echo ""
}

install_planning() {
    echo -e "${YELLOW}▸ Installing Planning modules (replaces: planning)${NC}"
    pip install --no-deps \
        odoo-addon-project-timeline \
        odoo-addon-project-stage-closed \
        odoo-addon-project-task-dependency
    echo ""
}

install_quality() {
    echo -e "${YELLOW}▸ Installing Quality Control modules (replaces: quality_control)${NC}"
    pip install --no-deps \
        odoo-addon-quality-control \
        odoo-addon-quality-control-stock
    echo ""
}

install_utilities() {
    echo -e "${YELLOW}▸ Installing Utility modules${NC}"
    pip install --no-deps \
        odoo-addon-web-responsive \
        odoo-addon-web-environment-ribbon \
        odoo-addon-partner-firstname
    echo ""
}

case "$CATEGORY" in
    accounting)
        install_accounting
        ;;
    mrp)
        install_mrp
        ;;
    hr)
        install_hr
        ;;
    timesheets)
        install_timesheets
        ;;
    subscriptions)
        install_subscriptions
        ;;
    helpdesk)
        install_helpdesk
        ;;
    planning)
        install_planning
        ;;
    quality)
        install_quality
        ;;
    utilities)
        install_utilities
        ;;
    all)
        install_accounting
        install_mrp
        install_hr
        install_timesheets
        install_subscriptions
        install_helpdesk
        install_planning
        install_quality
        install_utilities
        ;;
    *)
        echo -e "${RED}Unknown category: $CATEGORY${NC}"
        echo "Valid categories: accounting, mrp, hr, timesheets, subscriptions, helpdesk, planning, quality, utilities, all"
        exit 1
        ;;
esac

echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  OCA modules installed!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo "  Next steps:"
echo "  1. Restart Odoo: docker compose restart odoo"
echo "  2. Update module list in Odoo: Settings → Apps → Update Apps List"
echo "  3. Install OCA modules from Odoo UI"
echo ""
echo "  Run verification: ./scripts/odoo/verify-oca-modules.sh"
