#!/usr/bin/env bash
# ==============================================================================
# INSIGHTPULSE ODOO 18 CE PRODUCTION HOTFIX SCRIPT
# ==============================================================================
# Fixes:
#   1. OwlError: Removes 'pay_invoices_online' field from database views
#   2. OAuth HTTPS Loop: Forces HTTPS base URL in system parameters
#
# Usage: ./scripts/hotfix_production.sh [DB_NAME]
# ==============================================================================

set -euo pipefail

# === Configuration ===
DB_NAME="${1:-prod}"
CONTAINER_NAME=$(docker ps --format "{{.Names}}" | grep odoo | head -n 1)

if [[ -z "$CONTAINER_NAME" ]]; then
    echo "❌ ERROR: No running Odoo container found"
    exit 1
fi

echo "=================================================="
echo "INSIGHTPULSE ODOO PRODUCTION HOTFIX"
echo "=================================================="
echo "Container: $CONTAINER_NAME"
echo "Database:  $DB_NAME"
echo ""

# === 1. Fix OwlError: Remove 'pay_invoices_online' field ===
echo ">>> [1/4] Fixing OwlError (pay_invoices_online field)..."

docker exec -i "$CONTAINER_NAME" python3 <<'PYTHON_EOF'
import sys
import odoo
from odoo import api, SUPERUSER_ID

# Initialize Odoo environment
DB_NAME = sys.argv[1] if len(sys.argv) > 1 else 'prod'
config = odoo.tools.config
config['db_name'] = DB_NAME

try:
    odoo.service.server.load_server_wide_modules()
    registry = odoo.registry(DB_NAME)
except Exception as e:
    print(f"❌ Failed to initialize Odoo: {e}")
    sys.exit(1)

with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})

    # Find views containing the problematic field
    views = env['ir.ui.view'].search([
        ('arch_db', 'ilike', 'pay_invoices_online')
    ])

    if not views:
        print("✓ No views found with 'pay_invoices_online' field")
    else:
        print(f"Found {len(views)} view(s) to patch:")
        for view in views:
            print(f"  - {view.name} (ID: {view.id}, XML ID: {view.xml_id or 'N/A'})")

            # Remove the field from view architecture
            new_arch = view.arch_db
            new_arch = new_arch.replace('<field name="pay_invoices_online"/>', '')
            new_arch = new_arch.replace('<field name="pay_invoices_online" />', '')
            new_arch = new_arch.replace('<field name="pay_invoices_online"></field>', '')

            if new_arch != view.arch_db:
                view.write({'arch_db': new_arch})
                print(f"  ✓ Patched: {view.name}")

        cr.commit()
        print("✓ Database views patched successfully")
PYTHON_EOF

# === 2. Fix OAuth: Force HTTPS System Parameters ===
echo ""
echo ">>> [2/4] Fixing OAuth HTTPS loop..."

docker exec -i "$CONTAINER_NAME" psql -U odoo -d "$DB_NAME" <<'SQL_EOF'
-- Update web.base.url to use HTTPS
UPDATE ir_config_parameter
SET value = 'https://erp.insightpulseai.com'
WHERE key = 'web.base.url';

-- Freeze base URL to prevent OAuth overrides
DELETE FROM ir_config_parameter WHERE key = 'web.base.url.freeze';
INSERT INTO ir_config_parameter (key, value)
VALUES ('web.base.url.freeze', 'True');

-- Verify changes
SELECT key, value FROM ir_config_parameter
WHERE key IN ('web.base.url', 'web.base.url.freeze');
SQL_EOF

echo "✓ HTTPS system parameters enforced"

# === 3. Regenerate Assets (Clear JS Cache) ===
echo ""
echo ">>> [3/4] Regenerating assets (clearing JS cache)..."

docker exec "$CONTAINER_NAME" odoo -d "$DB_NAME" --update=web --stop-after-init

echo "✓ Assets regenerated"

# === 4. Restart Odoo Service ===
echo ""
echo ">>> [4/4] Restarting Odoo service..."

docker restart "$CONTAINER_NAME"

# Wait for service to come back up
echo -n "Waiting for Odoo to restart"
for i in {1..30}; do
    if docker exec "$CONTAINER_NAME" pgrep -f "odoo-bin" > /dev/null 2>&1; then
        echo " ✓"
        break
    fi
    echo -n "."
    sleep 1
done

echo ""
echo "=================================================="
echo "✅ HOTFIX COMPLETED - RUNNING VALIDATION"
echo "=================================================="
echo ""

# === VALIDATION: Success Criteria ===
VALIDATION_PASSED=true

# Criterion 1: Verify pay_invoices_online removed from database
echo ">>> [VALIDATION 1/5] Checking database views for pay_invoices_online..."
VIEW_COUNT=$(docker exec -i "$CONTAINER_NAME" psql -U odoo -d "$DB_NAME" -t -c \
  "SELECT COUNT(*) FROM ir_ui_view WHERE arch_db ILIKE '%pay_invoices_online%';")
VIEW_COUNT=$(echo $VIEW_COUNT | xargs) # trim whitespace

if [[ "$VIEW_COUNT" == "0" ]]; then
    echo "✓ PASS: No views contain 'pay_invoices_online' field"
else
    echo "❌ FAIL: Found $VIEW_COUNT view(s) still containing 'pay_invoices_online'"
    VALIDATION_PASSED=false
fi

# Criterion 2: Verify web.base.url is HTTPS
echo ""
echo ">>> [VALIDATION 2/5] Checking web.base.url system parameter..."
BASE_URL=$(docker exec -i "$CONTAINER_NAME" psql -U odoo -d "$DB_NAME" -t -c \
  "SELECT value FROM ir_config_parameter WHERE key='web.base.url';")
BASE_URL=$(echo $BASE_URL | xargs)

if [[ "$BASE_URL" == "https://erp.insightpulseai.com" ]]; then
    echo "✓ PASS: web.base.url = https://erp.insightpulseai.com"
else
    echo "❌ FAIL: web.base.url = $BASE_URL (expected https://erp.insightpulseai.com)"
    VALIDATION_PASSED=false
fi

# Criterion 3: Verify web.base.url.freeze is set
echo ""
echo ">>> [VALIDATION 3/5] Checking web.base.url.freeze parameter..."
FREEZE_VALUE=$(docker exec -i "$CONTAINER_NAME" psql -U odoo -d "$DB_NAME" -t -c \
  "SELECT value FROM ir_config_parameter WHERE key='web.base.url.freeze';")
FREEZE_VALUE=$(echo $FREEZE_VALUE | xargs)

if [[ "$FREEZE_VALUE" == "True" ]]; then
    echo "✓ PASS: web.base.url.freeze = True"
else
    echo "❌ FAIL: web.base.url.freeze = $FREEZE_VALUE (expected True)"
    VALIDATION_PASSED=false
fi

# Criterion 4: Verify Odoo is running and responding
echo ""
echo ">>> [VALIDATION 4/5] Checking Odoo service health..."
if docker exec "$CONTAINER_NAME" pgrep -f "odoo-bin" > /dev/null 2>&1; then
    echo "✓ PASS: Odoo process is running"
else
    echo "❌ FAIL: Odoo process not running"
    VALIDATION_PASSED=false
fi

# Criterion 5: Check for OwlError in recent logs
echo ""
echo ">>> [VALIDATION 5/5] Scanning recent logs for OwlError..."
ERROR_COUNT=$(docker logs "$CONTAINER_NAME" --tail 100 2>&1 | grep -c "OwlError" || true)

if [[ "$ERROR_COUNT" == "0" ]]; then
    echo "✓ PASS: No OwlError in recent logs"
else
    echo "⚠️  WARNING: Found $ERROR_COUNT OwlError(s) in recent logs (may be pre-fix errors)"
fi

# === Final Result ===
echo ""
echo "=================================================="
if [[ "$VALIDATION_PASSED" == true ]]; then
    echo "✅ ALL VALIDATIONS PASSED"
else
    echo "❌ SOME VALIDATIONS FAILED - REVIEW OUTPUT ABOVE"
fi
echo "=================================================="
echo ""

# === User Action Items ===
echo "Next Steps:"
echo "  1. Clear browser cache (Ctrl+Shift+R / Cmd+Shift+R)"
echo "  2. Open Chrome Incognito: https://erp.insightpulseai.com"
echo "  3. Press F12 → Console tab → Verify no red errors"
echo "  4. Test OAuth login (should stay on https://)"
echo "  5. Check browser source code: <link href='/web/assets/...css'/>"
echo ""
echo "Manual Verification Commands:"
echo "  # Check nginx headers"
echo "  docker exec nginx nginx -T | grep X-Forwarded-Proto"
echo ""
echo "  # Test HTTPS endpoint"
echo "  curl -I https://erp.insightpulseai.com"
echo ""
echo "  # View recent Odoo logs"
echo "  docker logs $CONTAINER_NAME --tail 50"
echo ""

if [[ "$VALIDATION_PASSED" == false ]]; then
    echo "⚠️  ATTENTION: Validation failures detected. Review before proceeding."
    exit 1
fi
