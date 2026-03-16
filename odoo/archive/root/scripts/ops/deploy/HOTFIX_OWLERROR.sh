#!/bin/bash
# HOTFIX: Remove pay_invoices_online field references causing OWL error
# Error: "res.config.settings"."pay_invoices_online" field is undefined
# Location: erp.insightpulseai.com
# Date: 2025-12-28

set -e

echo "🔧 Odoo OwlError Hotfix - pay_invoices_online field"
echo "=================================================="
echo ""

# Check if running with required credentials
if [ -z "$ODOO_PASSWORD" ]; then
    echo "❌ Error: ODOO_PASSWORD environment variable not set"
    echo ""
    echo "Usage:"
    echo "  export ODOO_PASSWORD='your_admin_password'"
    echo "  ./HOTFIX_OWLERROR.sh"
    exit 1
fi

# Configuration
ODOO_URL="${ODOO_URL:-https://erp.insightpulseai.com}"
ODOO_DB="${ODOO_DB:-production}"
ODOO_USERNAME="${ODOO_USERNAME:-admin}"
PRODUCTION_SERVER="${PRODUCTION_SERVER:-159.223.75.148}"

echo "📋 Configuration:"
echo "  URL: $ODOO_URL"
echo "  DB: $ODOO_DB"
echo "  User: $ODOO_USERNAME"
echo ""

# Ask for confirmation
read -p "⚠️  This will modify production database. Continue? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "Aborted."
    exit 0
fi

echo ""
echo "Step 1: Running diagnostic (dry-run mode)..."
echo "--------------------------------------------"

python3 scripts/fix-pay-invoices-online-error.py --dry-run --remove-field

echo ""
read -p "Do diagnostics look correct? Continue with fix? (yes/no): " confirm2
if [ "$confirm2" != "yes" ]; then
    echo "Aborted."
    exit 0
fi

echo ""
echo "Step 2: Applying fix (removing field references)..."
echo "----------------------------------------------------"

python3 scripts/fix-pay-invoices-online-error.py --remove-field

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Fix applied successfully"
    echo ""
    echo "Step 3: Restarting Odoo service..."
    echo "-----------------------------------"

    ssh root@$PRODUCTION_SERVER "docker compose -f /opt/odoo/docker-compose.yml restart odoo-ce"

    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Odoo restarted successfully"
        echo ""
        echo "📝 Next steps:"
        echo "  1. Clear browser cache (Cmd+Shift+R)"
        echo "  2. Visit: $ODOO_URL"
        echo "  3. Navigate to Settings and verify no errors"
        echo ""
        echo "If error persists, check:"
        echo "  - Browser console for any remaining errors"
        echo "  - scripts/FIX_OWLERROR_GUIDE.md for troubleshooting"
    else
        echo ""
        echo "❌ Error restarting Odoo"
        echo "Manual restart required:"
        echo "  ssh root@$PRODUCTION_SERVER"
        echo "  docker compose -f /opt/odoo/docker-compose.yml restart odoo-ce"
    fi
else
    echo ""
    echo "❌ Fix failed. Check error output above."
    echo "Fallback: Use SQL method from scripts/FIX_OWLERROR_GUIDE.md"
    exit 1
fi

echo ""
echo "✅ Hotfix complete"
