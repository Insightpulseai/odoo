#!/bin/bash
set -euo pipefail

: "${ODOO_DB:=odoo_core}"
: "${BASE_URL:=https://erp.insightpulseai.net}"
: "${COMPOSE_FILE:=docker-compose.prod.yml}"

echo "=== IPAI Ship Pack v1.1.0: Final Deployment (Odoo CE) ==="
echo "Target DB: $ODOO_DB"

# 1. Rebuild Image (Critical for odoo-ce structure changes)
echo ""
echo "[1/4] Rebuilding Docker image..."
docker-compose -f "$COMPOSE_FILE" build odoo

# 2. Fix Permissions (Crucial for 500 fixes)
echo ""
echo "[2/4] Ensuring correct volume permissions..."
# Start container if not running to fix perms
docker-compose -f "$COMPOSE_FILE" up -d odoo
docker-compose -f "$COMPOSE_FILE" exec -u root odoo chown -R odoo:odoo /var/lib/odoo

# 3. Force upgrade of web + ship pack modules (Fast fix pattern)
echo ""
echo "[3/4] Force upgrading web + IPAI modules..."
docker-compose -f "$COMPOSE_FILE" exec odoo odoo -c /etc/odoo/odoo.conf -d "$ODOO_DB" -u web,ipai_theme_aiux,ipai_aiux_chat,ipai_ask_ai,ipai_document_ai,ipai_expense_ocr --stop-after-init

# 4. Restart and Verify
echo ""
echo "[4/4] Restarting and Verifying..."
docker-compose -f "$COMPOSE_FILE" restart odoo || true

echo "Waiting 15s for startup..."
sleep 15

if curl -fsS "$BASE_URL/web" >/dev/null 2>&1; then
    echo "✅ /web endpoint reachable"
    curl -fsSI "$BASE_URL/web/assets/" | head -n 1
else
    echo "⚠️  Could not reach $BASE_URL automatically. Please verify manually."
fi

echo ""
echo "✅ Ship v1.1.0 sequence initiated."
