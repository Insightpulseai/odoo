#!/bin/bash
set -euo pipefail

# Fix Production Asset System
# Droplet: 178.128.112.214
# Container: odoo-prod

echo "🔧 Fixing production asset system at erp.insightpulseai.net..."
echo ""

DROPLET="root@178.128.112.214"

echo "Step 1: Clear corrupted assets from database"
ssh "$DROPLET" <<'REMOTE'
cd /opt/odoo-ce/repo

# Create fix script
cat > /tmp/fix_assets.py <<'PYTHON'
import odoo
import odoo.sql_db

db_name = "odoo"
with odoo.sql_db.db_connect(db_name).cursor() as cr:
    env = odoo.api.Environment(cr, 1, {})

    print("🗑️  Clearing all asset attachments...")
    # Delete ALL web assets to force complete regeneration
    cr.execute("""
        DELETE FROM ir_attachment
        WHERE res_model = 'ir.ui.view'
          AND (name LIKE 'web.assets%' OR name LIKE 'web_editor.assets%')
    """)
    deleted = cr.rowcount
    print(f"Deleted {deleted} asset attachments")

    print("🗑️  Clearing orphaned attachments...")
    cr.execute("""
        DELETE FROM ir_attachment
        WHERE res_model = 'ir.ui.view'
          AND res_id NOT IN (SELECT id FROM ir_ui_view)
    """)
    orphaned = cr.rowcount
    print(f"Deleted {orphaned} orphaned attachments")

    print("🗑️  Clearing QWeb cache...")
    env["ir.qweb"].clear_caches()

    print("🗑️  Clearing registry cache...")
    env.registry.clear_cache()

    cr.commit()
    print("✅ Database cleanup complete")
PYTHON

# Run fix script
docker exec odoo-prod python3 /tmp/fix_assets.py
REMOTE

echo ""
echo "Step 2: Wipe filestore to force regeneration"
ssh "$DROPLET" <<'REMOTE'
docker exec odoo-prod rm -rf /var/lib/odoo/filestore/odoo/web_editor 2>/dev/null || true
docker exec odoo-prod rm -rf /var/lib/odoo/sessions/* 2>/dev/null || true
echo "✅ Filestore cleared"
REMOTE

echo ""
echo "Step 3: Restart Odoo to regenerate assets"
ssh "$DROPLET" "docker restart odoo-prod"

echo "✅ Container restarted"
echo ""
echo "⏳ Waiting 30 seconds for Odoo to start..."
sleep 30

echo ""
echo "Step 4: Force asset regeneration via HTTP request"
echo "Accessing login page to trigger asset generation..."
curl -sf "https://erp.insightpulseai.net/web/login" > /dev/null && echo "✅ Login page accessible" || echo "⚠️  Login page still loading..."

echo ""
echo "Step 5: Verify asset availability"
STATUS=$(curl -sS -o /dev/null -w "%{http_code}" "https://erp.insightpulseai.net/web/assets/1/f72ec00/web.assets_frontend_minimal.min.js" 2>&1 || echo "000")

if [ "$STATUS" = "200" ]; then
    echo "✅ JavaScript assets now return HTTP 200"
    echo ""
    echo "✅ Fix complete! Test at: https://erp.insightpulseai.net/web/login"
elif [ "$STATUS" = "000" ]; then
    echo "⚠️  Cannot connect - Odoo may still be starting"
    echo "   Wait 30 more seconds and try: https://erp.insightpulseai.net/web/login"
else
    echo "❌ JavaScript assets return HTTP $STATUS (expected 200)"
    echo ""
    echo "🔍 Check Odoo logs:"
    echo "   ssh $DROPLET 'docker logs odoo-prod --tail 100'"
    exit 1
fi
