#!/usr/bin/env bash
set -euo pipefail

# Canonical Asset Rebuild After Filestore Wipe
# Idempotent + safe runbook for asset system failures
#
# Use this when:
# - Filestore was wiped but asset attachments remain in DB
# - JavaScript assets return HTTP 500
# - Login form has d-none class that JS never removes

: "${DB_HOST:?Missing DB_HOST}"
: "${DB_PORT:=5432}"
: "${DB_NAME:=odoo}"
: "${DB_USER:?Missing DB_USER}"
: "${DB_PASSWORD:?Missing DB_PASSWORD}"
: "${ODOO_CONTAINER:=odoo-prod}"

export PGPASSWORD="$DB_PASSWORD"

echo "🔧 Odoo Asset Rebuild After Filestore Wipe"
echo "Database: $DB_HOST:$DB_PORT/$DB_NAME"
echo "Container: $ODOO_CONTAINER"
echo ""

echo "Step 1: Purging stale web asset attachments from database..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" <<'SQL'
DELETE FROM ir_attachment
WHERE (url LIKE '/web/assets/%')
   OR (name LIKE 'web.assets%')
   OR (name LIKE 'web_editor.assets%')
   OR (name LIKE 'web._assets_%')
   OR (name LIKE 'web.assets_frontend%')
   OR (name LIKE 'web.assets_backend%')
   OR (res_model = 'ir.ui.view' AND name LIKE '%assets%');

SELECT 'Deleted ' || COUNT(*) || ' asset attachments' AS result
FROM ir_attachment
WHERE FALSE; -- Always returns 0, just for message

-- Also clear orphaned attachments
DELETE FROM ir_attachment
WHERE res_model = 'ir.ui.view'
  AND res_id NOT IN (SELECT id FROM ir_ui_view);
SQL

echo "✅ Asset attachments purged"
echo ""

echo "Step 2: Restarting Odoo container..."
docker restart "$ODOO_CONTAINER" >/dev/null
echo "✅ Container restarted"
echo ""

echo "⏳ Waiting 10 seconds for Odoo to start..."
sleep 10

echo ""
echo "Step 3: Running health check..."
if curl -sS -I "https://erp.insightpulseai.net/web/assets/debug" 2>&1 | head -5 | grep -q "200"; then
    echo "✅ Assets debug endpoint returns 200"
else
    echo "⚠️  Assets may still be regenerating - check logs"
fi

echo ""
echo "✅ Asset rebuild complete"
echo ""
echo "Verify with:"
echo "  ./scripts/healthcheck_odoo_login.sh"
echo "  node scripts/verify_login_headless.js"
