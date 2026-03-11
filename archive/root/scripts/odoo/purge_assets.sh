#!/usr/bin/env bash
# ==============================================================================
# ODOO ASSET PURGE & REBUILD SCRIPT
# ==============================================================================
# Purges compiled CSS/JS assets and restarts Odoo to force recompilation.
# Use this when you see "Style compilation failed" banner or broken CSS.
#
# Usage:
#   ./scripts/odoo/purge_assets.sh [CONTAINER_NAME] [DB_NAME]
#
# Default: odoo-erp-prod, odoo
# ==============================================================================

set -euo pipefail

CONTAINER_NAME="${1:-odoo-erp-prod}"
DB_NAME="${2:-odoo}"

echo "============================================================"
echo "ODOO ASSET PURGE & REBUILD"
echo "============================================================"
echo "Container: $CONTAINER_NAME"
echo "Database:  $DB_NAME"
echo ""

# === Check if container exists ===
if ! docker ps --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
    echo "❌ ERROR: Container '$CONTAINER_NAME' not found"
    exit 1
fi

# === 1. Count existing assets ===
echo ">>> [1/4] Counting existing compiled assets..."
BEFORE_COUNT=$(docker exec -i "$CONTAINER_NAME" psql -U odoo -d "$DB_NAME" -t -c \
    "SELECT COUNT(*) FROM ir_attachment WHERE name ILIKE '%assets_%' OR name ILIKE 'web.assets_%';" 2>/dev/null || echo "0")
BEFORE_COUNT=$(echo "$BEFORE_COUNT" | xargs)
echo "Found $BEFORE_COUNT compiled asset attachment(s)"
echo ""

# === 2. Purge asset attachments ===
echo ">>> [2/4] Purging compiled assets..."
docker exec -i "$CONTAINER_NAME" psql -U odoo -d "$DB_NAME" -c "
DELETE FROM ir_attachment
WHERE name ILIKE '%assets_%'
   OR name ILIKE 'web.assets_%';
" 2>/dev/null

echo "✓ Asset attachments purged"
echo ""

# === 3. Clear QWEB cache ===
echo ">>> [3/4] Clearing QWEB template cache..."
docker exec -i "$CONTAINER_NAME" psql -U odoo -d "$DB_NAME" -c "
DELETE FROM ir_qweb_field_html_history WHERE 1=1;
" 2>/dev/null || true  # Table may not exist in all versions

echo "✓ QWEB cache cleared"
echo ""

# === 4. Restart container ===
echo ">>> [4/4] Restarting Odoo container..."
docker restart "$CONTAINER_NAME"

# Wait for container to come back
echo -n "Waiting for Odoo to restart"
for i in {1..30}; do
    if docker exec "$CONTAINER_NAME" pgrep -f "odoo-bin\|odoo" > /dev/null 2>&1; then
        echo " ✓"
        break
    fi
    echo -n "."
    sleep 1
done

echo ""
echo "============================================================"
echo "✅ ASSET PURGE COMPLETE"
echo "============================================================"
echo ""
echo "Deleted approximately $BEFORE_COUNT asset attachments."
echo "Assets will be recompiled on first page load."
echo ""
echo "Next steps:"
echo "  1. Hard refresh browser: Ctrl+Shift+R (Win) / Cmd+Shift+R (Mac)"
echo "  2. Check for errors: docker logs --tail 50 $CONTAINER_NAME"
echo "  3. If still failing, check: ./scripts/odoo/diagnose_scss_error.sh"
echo ""
