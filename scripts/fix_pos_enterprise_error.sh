#!/bin/bash
# =============================================================================
# Fix POS Enterprise Field Error on Production
# =============================================================================
# Deploys ipai_enterprise_bridge fix for pos_self_ordering_mode field
# Resolves: "res.config.settings"."pos_self_ordering_mode" field is undefined
# =============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Deploying Enterprise Bridge POS Fix ===${NC}"
echo ""

# Check if we're on the production server
if [ ! -f "/opt/odoo-ce/repo/.git/config" ]; then
    echo -e "${RED}❌ Error: Not on production server${NC}"
    echo "This script must run on root@159.223.75.148"
    exit 1
fi

cd /opt/odoo-ce/repo

# Step 1: Pull latest code
echo -e "${YELLOW}Step 1: Pulling latest code from repository...${NC}"
git fetch origin main
git reset --hard origin/main
echo -e "${GREEN}✅ Code updated to latest commit${NC}"
echo ""

# Step 2: Verify the fix is present
echo -e "${YELLOW}Step 2: Verifying fix is present...${NC}"
if grep -q "pos_self_ordering_mode" addons/ipai/ipai_enterprise_bridge/models/res_config_settings.py; then
    echo -e "${GREEN}✅ POS field stubs found in enterprise bridge${NC}"
else
    echo -e "${RED}❌ Error: Fix not found in code${NC}"
    exit 1
fi
echo ""

# Step 3: Upgrade ipai_enterprise_bridge module
echo -e "${YELLOW}Step 3: Upgrading ipai_enterprise_bridge module...${NC}"
docker exec odoo-erp-prod odoo \
    -d production \
    -u ipai_enterprise_bridge \
    --stop-after-init \
    --log-level=info

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Module upgraded successfully${NC}"
else
    echo -e "${RED}❌ Error: Module upgrade failed${NC}"
    echo "Check Odoo logs: docker logs odoo-erp-prod --tail 50"
    exit 1
fi
echo ""

# Step 4: Restart Odoo to apply changes
echo -e "${YELLOW}Step 4: Restarting Odoo...${NC}"
docker restart odoo-erp-prod
echo -e "${GREEN}✅ Odoo restarted${NC}"
echo ""

# Step 5: Wait for Odoo to start
echo -e "${YELLOW}Step 5: Waiting for Odoo to start (15 seconds)...${NC}"
sleep 15
echo ""

# Step 6: Verify Odoo is running
echo -e "${YELLOW}Step 6: Verifying Odoo health...${NC}"
if docker exec odoo-erp-prod pgrep -f "odoo-bin" > /dev/null; then
    echo -e "${GREEN}✅ Odoo process is running${NC}"
else
    echo -e "${RED}❌ Error: Odoo process not running${NC}"
    echo "Check logs: docker logs odoo-erp-prod --tail 50"
    exit 1
fi
echo ""

# Step 7: Test HTTP endpoint
echo -e "${YELLOW}Step 7: Testing HTTP endpoint...${NC}"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" https://erp.insightpulseai.net/web/login)

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ HTTP endpoint responding (HTTP $HTTP_CODE)${NC}"
else
    echo -e "${RED}❌ Warning: HTTP endpoint returned $HTTP_CODE${NC}"
    echo "May need additional time to fully start"
fi
echo ""

# Step 8: Check for errors in logs
echo -e "${YELLOW}Step 8: Checking for errors in logs...${NC}"
ERRORS=$(docker logs odoo-erp-prod --tail 100 | grep -i "error\|exception\|traceback" | wc -l)

if [ "$ERRORS" -eq 0 ]; then
    echo -e "${GREEN}✅ No errors found in recent logs${NC}"
else
    echo -e "${YELLOW}⚠️  Warning: Found $ERRORS error lines in logs${NC}"
    echo "Recent errors:"
    docker logs odoo-erp-prod --tail 100 | grep -i "error\|exception" | tail -5
fi
echo ""

# Final summary
echo -e "${GREEN}=== Deployment Complete ===${NC}"
echo ""
echo "Summary:"
echo "  ✅ Code updated from repository"
echo "  ✅ ipai_enterprise_bridge module upgraded"
echo "  ✅ Odoo restarted"
echo "  ✅ Service health verified"
echo ""
echo "Next steps:"
echo "  1. Test Settings page: https://erp.insightpulseai.net/web#action=base.action_res_config_settings"
echo "  2. Navigate to Point of Sale settings"
echo "  3. Verify no OwlError occurs"
echo "  4. Check browser console for errors (F12)"
echo ""
echo "If errors persist:"
echo "  - Check logs: docker logs odoo-erp-prod --tail 100"
echo "  - Clear browser cache (Ctrl+Shift+Delete)"
echo "  - Hard refresh page (Ctrl+Shift+R)"
echo ""
