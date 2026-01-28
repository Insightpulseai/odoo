#!/bin/bash
# Deploy TBWA theme updates to production Odoo

set -e

PROD_SERVER="root@178.128.112.214"
PROD_REPO="/opt/odoo-ce/repo"
MODULE_NAME="ipai_web_theme_tbwa"

echo "==========================================="
echo "TBWA Theme Production Deployment"
echo "==========================================="
echo ""

echo "1. Connecting to production server..."
ssh "$PROD_SERVER" "cd $PROD_REPO && git fetch origin main"
echo "✅ Fetched latest changes"
echo ""

echo "2. Pulling latest code..."
ssh "$PROD_SERVER" "cd $PROD_REPO && git checkout main && git pull origin main"
echo "✅ Code updated"
echo ""

echo "3. Restarting Odoo to apply theme changes..."
ssh "$PROD_SERVER" "docker restart odoo-prod"
echo "✅ Odoo restarted"
echo ""

echo "4. Waiting for Odoo to come back online..."
sleep 10

for i in {1..12}; do
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "https://erp.insightpulseai.net/web/health" || echo "000")
    if [ "$HTTP_CODE" = "200" ]; then
        echo "✅ Odoo is online (attempt $i/12)"
        break
    else
        echo "⏳ Waiting for Odoo... (attempt $i/12)"
        sleep 5
    fi
done
echo ""

echo "==========================================="
echo "Deployment Complete"
echo "==========================================="
echo ""
echo "Theme module: $MODULE_NAME"
echo "Production URL: https://erp.insightpulseai.net/web/login"
echo ""
echo "✅ Login button should now be fixed:"
echo "   - Black button (#000000)"
echo "   - White text"
echo "   - Hover effects working"
echo "   - Fully clickable"
echo ""
echo "Please test the login page to verify."
echo ""
