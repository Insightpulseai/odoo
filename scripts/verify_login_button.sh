#!/bin/bash
# Verify login button fix on production Odoo

set -e

PRODUCTION_URL="https://erp.insightpulseai.net"
LOGIN_URL="${PRODUCTION_URL}/web/login"

echo "==========================================="
echo "Login Button Verification"
echo "==========================================="
echo ""

echo "1. Testing production login page accessibility..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$LOGIN_URL")
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Login page accessible (HTTP $HTTP_CODE)"
else
    echo "❌ Login page returned HTTP $HTTP_CODE"
    exit 1
fi
echo ""

echo "2. Checking if theme CSS is loaded..."
THEME_CSS=$(curl -s "$LOGIN_URL" | grep -c "ipai_web_theme_tbwa" || echo "0")
if [ "$THEME_CSS" -gt "0" ]; then
    echo "✅ TBWA theme CSS detected"
else
    echo "⚠️  TBWA theme CSS not found (may need module restart)"
fi
echo ""

echo "3. Checking for login button elements..."
LOGIN_BUTTON=$(curl -s "$LOGIN_URL" | grep -c 'type="submit"' || echo "0")
if [ "$LOGIN_BUTTON" -gt "0" ]; then
    echo "✅ Login button element found"
else
    echo "❌ Login button element not found"
fi
echo ""

echo "==========================================="
echo "Manual Verification Steps:"
echo "==========================================="
echo ""
echo "1. Open: $LOGIN_URL"
echo "2. Check login button:"
echo "   - Button should be black (#000000)"
echo "   - Text should be white"
echo "   - Hover should darken to #1a1a1a"
echo "   - Cursor should be pointer"
echo "   - Button should be clickable"
echo ""
echo "3. Test login flow:"
echo "   - Enter credentials"
echo "   - Click login button"
echo "   - Should authenticate successfully"
echo ""

echo "To restart Odoo with new theme (if needed):"
echo "ssh root@178.128.112.214 'docker restart odoo-prod'"
echo ""
