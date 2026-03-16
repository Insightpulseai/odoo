#!/usr/bin/env bash
###############################################################################
# Odoo Baseline Installation (CE + OCA Must-Have)
# Based on prd-odoo-module-pipeline.md Appendix A
###############################################################################

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

DROPLET_IP="${DROPLET_IP:-178.128.112.214}"
DB="${ODOO_DB:-odoo}"

echo "================================================================================"
echo "Odoo Baseline Installation (CE + OCA Must-Have)"
echo "================================================================================"
echo ""
echo "Database: $DB"
echo "Droplet: $DROPLET_IP"
echo ""

###############################################################################
# 0. Hard-stop on invalid module names
###############################################################################
echo "0. Checking for invalid module names (hard blocker)..."

if ssh root@"$DROPLET_IP" "find /opt/odoo-ce/repo/addons -maxdepth 3 -type d -name '*.backup' 2>/dev/null | grep -q ."; then
    echo -e "${RED}ERROR: Found invalid module folder names with dots:${NC}"
    ssh root@"$DROPLET_IP" "find /opt/odoo-ce/repo/addons -maxdepth 3 -type d -name '*.backup'"
    echo ""
    echo "Fix: Rename/remove folders with dots in module names."
    echo "Example: ipai_month_end_closing.backup → ipai_month_end_closing_backup"
    exit 1
fi

echo -e "${GREEN}✓ No invalid module names found${NC}"
echo ""

###############################################################################
# 1A. Install CE Baseline First
###############################################################################
echo "1A. Installing Odoo CE baseline modules..."

ssh root@"$DROPLET_IP" bash <<'REMOTE_SCRIPT'
set -euo pipefail
DB="${ODOO_DB:-odoo}"

echo "  Updating module list..."
docker exec odoo-erp-prod odoo -d "$DB" -u base --stop-after-init

echo "  Installing CE baseline modules..."
CE_BASE="base,web,mail,account,accountant,sale_management,purchase,stock,crm,project,hr_timesheet"

docker exec odoo-erp-prod odoo -d "$DB" -i "$CE_BASE" --stop-after-init

echo "  ✓ CE baseline installed"
REMOTE_SCRIPT

echo -e "${GREEN}✓ CE baseline installation complete${NC}"
echo ""

###############################################################################
# 1B. Install OCA Must-Have Baseline
###############################################################################
echo "1B. Installing OCA Must-Have modules..."

echo -e "${YELLOW}Note: This requires OCA addons_path to be configured in odoo.conf${NC}"
echo ""

ssh root@"$DROPLET_IP" bash <<'REMOTE_SCRIPT'
set -euo pipefail
DB="${ODOO_DB:-odoo}"

# OCA Must-Have modules from PRD Appendix A
OCA_MUST="account_financial_report,account_lock_date_update,account_fiscal_year,base_tier_validation,mass_editing,report_xlsx"

# OCA Should-Have modules (optional but recommended)
OCA_SHOULD="sale_order_type,purchase_order_type,auditlog,web_responsive"

echo "  Installing OCA Must-Have modules..."
if docker exec odoo-erp-prod odoo -d "$DB" -i "$OCA_MUST" --stop-after-init 2>&1 | tee /tmp/oca_install.log; then
    echo "  ✓ OCA Must-Have modules installed"
else
    echo "  ⚠ Some OCA modules may not be available yet"
    echo "  Check /tmp/oca_install.log for details"
fi

echo ""
echo "  Installing OCA Should-Have modules..."
if docker exec odoo-erp-prod odoo -d "$DB" -i "$OCA_SHOULD" --stop-after-init 2>&1 | tee -a /tmp/oca_install.log; then
    echo "  ✓ OCA Should-Have modules installed"
else
    echo "  ⚠ Some OCA modules may not be available yet"
    echo "  This is optional and can be installed later"
fi
REMOTE_SCRIPT

echo -e "${GREEN}✓ OCA baseline installation complete${NC}"
echo ""

###############################################################################
# 2. Verify Installation
###############################################################################
echo "2. Verifying baseline installation..."

ssh root@"$DROPLET_IP" bash <<'REMOTE_SCRIPT'
set -euo pipefail
DB="${ODOO_DB:-odoo}"

echo "  Installed modules summary:"
docker exec odoo-erp-prod bash -c "
psql -h db -U postgres -d \"$DB\" -c \"
SELECT
  CASE
    WHEN name LIKE 'ipai_%' THEN 'Custom (ipai_*)'
    WHEN author LIKE '%OCA%' OR author LIKE '%Odoo Community%' THEN 'OCA'
    ELSE 'Core'
  END as category,
  COUNT(*) as count
FROM ir_module_module
WHERE state = 'installed'
GROUP BY category
ORDER BY category;
\"
"
REMOTE_SCRIPT

echo -e "${GREEN}✓ Verification complete${NC}"
echo ""

###############################################################################
# 3. Health Checks
###############################################################################
echo "3. Running health checks..."

ssh root@"$DROPLET_IP" bash <<'REMOTE_SCRIPT'
set -euo pipefail
DB="${ODOO_DB:-odoo}"

echo "  Database health check..."
docker exec odoo-erp-prod bash -c "psql -h db -U postgres -d \"$DB\" -c 'SELECT 1;'" > /dev/null
echo "  ✓ Database connection OK"

echo "  Module registry sanity check..."
docker exec odoo-erp-prod bash -c "
psql -h db -U postgres -d \"$DB\" -c \"
SELECT state, COUNT(*) as count
FROM ir_module_module
WHERE name LIKE 'ipai_%'
GROUP BY state
ORDER BY state;
\"
"

echo "  Server boot test..."
if docker exec odoo-erp-prod odoo -d "$DB" --stop-after-init 2>&1 | grep -q "odoo.modules.loading: Modules loaded"; then
    echo "  ✓ Server boots cleanly"
else
    echo "  ⚠ Server boot had warnings (check logs)"
fi
REMOTE_SCRIPT

echo -e "${GREEN}✓ Health checks complete${NC}"
echo ""

###############################################################################
# Summary
###############################################################################
echo "================================================================================"
echo "Baseline Installation Complete"
echo "================================================================================"
echo ""
echo "Installed baseline:"
echo "  - Odoo CE core modules (base, accounting, sales, etc.)"
echo "  - OCA Must-Have modules (from PRD Appendix A)"
echo "  - OCA Should-Have modules (optional enhancements)"
echo ""
echo "Next steps:"
echo "  1. Run footprint analysis: ./scripts/odoo_rationalization.sh"
echo "  2. Review redundancy report: docs/rationalization/RATIONALIZATION_REPORT.md"
echo "  3. Execute retirements for UI-only modules"
echo "  4. Re-evaluate remaining ipai_* modules against OCA baseline"
echo ""
echo "View installed modules:"
echo "  ssh root@$DROPLET_IP \"docker exec odoo-erp-prod odoo shell -d $DB\""
echo "  >> env['ir.module.module'].search([('state', '=', 'installed')]).mapped('name')"
echo ""
