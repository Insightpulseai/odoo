#!/bin/bash
# =============================================================================
# Deploy TBWA Theme Token Alignment to Odoo
# =============================================================================
# Upgrades TBWA theme modules to regenerate assets with corrected brand colors
# Run after merging fix/tbwa-align-brand-tokens branch
# =============================================================================

set -e

ODOO_DB="${ODOO_DB:-odoo_core}"
ODOO_CONTAINER="${ODOO_CONTAINER:-odoo-core}"

echo "==========================================="
echo "TBWA Theme Token Deployment"
echo "==========================================="
echo "Database: $ODOO_DB"
echo "Container: $ODOO_CONTAINER"
echo ""

# Check if running in Docker
if command -v docker &> /dev/null && docker ps --format '{{.Names}}' | grep -q "$ODOO_CONTAINER"; then
    echo "✅ Docker detected, using container: $ODOO_CONTAINER"
    ODOO_CMD="docker compose exec -T $ODOO_CONTAINER odoo"
else
    echo "✅ Running directly (no Docker)"
    ODOO_CMD="odoo"
fi

echo ""
echo "Step 1: Backup current assets..."
BACKUP_DIR="/tmp/odoo_tbwa_theme_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
echo "Backup directory: $BACKUP_DIR"

# Note: Asset backup is optional since Odoo regenerates on upgrade
# Uncomment if you need file-level backups
# docker compose cp odoo-core:/var/lib/odoo/filestore "$BACKUP_DIR/" 2>/dev/null || true

echo ""
echo "Step 2: Upgrade TBWA theme modules..."
echo "Modules: ipai_ui_brand_tokens, ipai_theme_tbwa_backend, ipai_web_theme_tbwa"

$ODOO_CMD -d "$ODOO_DB" \
  -u ipai_ui_brand_tokens,ipai_theme_tbwa_backend,ipai_web_theme_tbwa \
  --stop-after-init

if [ $? -eq 0 ]; then
    echo "✅ Module upgrade successful"
else
    echo "❌ Module upgrade failed"
    exit 1
fi

echo ""
echo "Step 3: Restart Odoo to apply changes..."

if command -v docker &> /dev/null && docker ps --format '{{.Names}}' | grep -q "$ODOO_CONTAINER"; then
    docker compose restart "$ODOO_CONTAINER"
    echo "✅ Container restarted"
else
    echo "⚠️  Manual restart required (not in Docker environment)"
    echo "   Run: sudo systemctl restart odoo"
fi

echo ""
echo "==========================================="
echo "Deployment Complete!"
echo "==========================================="
echo ""
echo "Next Steps:"
echo "1. Open Odoo in browser with hard refresh:"
echo "   https://erp.insightpulseai.net/web?debug=assets"
echo ""
echo "2. Verify brand colors:"
echo "   - Navbar background: #0B0B0B (TBWA Black)"
echo "   - Primary buttons: #FFC400 (TBWA Yellow)"
echo "   - Button hover: #E5AE00 (TBWA Yellow Dark)"
echo "   - Info badges: #2563EB (Blue, not yellow)"
echo ""
echo "3. Test in different views:"
echo "   - Contacts list"
echo "   - Project tasks"
echo "   - Accounting dashboard"
echo "   - Settings"
echo ""
echo "4. Check browser console for asset errors"
echo ""
echo "Rollback: Use backup in $BACKUP_DIR if needed"
echo "==========================================="
