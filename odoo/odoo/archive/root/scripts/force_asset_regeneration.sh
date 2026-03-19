#!/bin/bash
# Force Odoo to regenerate all assets (CSS/JS)

set -e

PROD_SERVER="root@178.128.112.214"

echo "==========================================="
echo "Force Asset Regeneration"
echo "==========================================="
echo ""

echo "1. Clearing Odoo assets cache..."
ssh "$PROD_SERVER" "docker exec odoo-prod bash -c 'rm -rf /var/lib/odoo/.local/share/Odoo/filestore/*/assets/*'"
echo "✅ Assets cache cleared"
echo ""

echo "2. Clearing web assets..."
ssh "$PROD_SERVER" "docker exec odoo-prod bash -c 'rm -rf /var/lib/odoo/addons/18.0/web/static/lib/*'"
echo "✅ Web assets cleared"
echo ""

echo "3. Restarting Odoo..."
ssh "$PROD_SERVER" "docker restart odoo-prod"
echo "✅ Odoo restarted"
echo ""

echo "4. Waiting for Odoo to come back online..."
sleep 15

for i in {1..12}; do
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "https://erp.insightpulseai.com/web/health" || echo "000")
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
echo "Asset Regeneration Complete"
echo "==========================================="
echo ""
echo "Next steps:"
echo "1. Open: https://erp.insightpulseai.com/web/login"
echo "2. Hard refresh your browser (Cmd+Shift+R on Mac, Ctrl+Shift+R on Windows)"
echo "3. Login and verify changes"
echo ""
echo "What to verify:"
echo "✅ Header shows only TBWA logo and user menu"
echo "✅ No navigation menu items visible"
echo "✅ Login button is black with white text"
echo ""
