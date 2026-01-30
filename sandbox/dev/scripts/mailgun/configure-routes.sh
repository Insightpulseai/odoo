#!/usr/bin/env bash
set -euo pipefail

# ═══════════════════════════════════════════════════════════════════════════════
# Configure Mailgun Inbound Routes (Production Only)
# ═══════════════════════════════════════════════════════════════════════════════

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Load environment
if [ -f "$PROJECT_ROOT/.env" ]; then
    set -a
    source "$PROJECT_ROOT/.env"
    set +a
fi

# Configuration
MAILGUN_API_KEY="${MAILGUN_API_KEY:-}"
MAILGUN_DOMAIN="${MAILGUN_DOMAIN:-mg.insightpulseai.net}"
WEBHOOK_BASE_URL="${WEB_BASE_URL:-https://erp.insightpulseai.net}"

echo "════════════════════════════════════════════════════════════════"
echo "Configure Mailgun Inbound Routes"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Configuration:"
echo "  Mailgun Domain: $MAILGUN_DOMAIN"
echo "  Webhook Base URL: $WEBHOOK_BASE_URL"
echo "  API Key: ${MAILGUN_API_KEY:0:15}... (redacted)"
echo ""

# Check API key
if [ -z "$MAILGUN_API_KEY" ]; then
    echo "❌ Error: MAILGUN_API_KEY not set"
    echo "   Set in .env or export MAILGUN_API_KEY=your_key"
    exit 1
fi

echo "🔧 Creating catchall route..."

# Create catchall route (all @insightpulseai.net)
ROUTE_RESPONSE=$(curl -s -u "api:${MAILGUN_API_KEY}" \
    https://api.mailgun.net/v3/routes \
    -F priority=1 \
    -F description='Odoo catchall - all @insightpulseai.net' \
    -F expression='match_recipient(".*@insightpulseai.net")' \
    -F action="forward(\"${WEBHOOK_BASE_URL}/mailgun/inbound\")" \
    -F action='stop()')

if echo "$ROUTE_RESPONSE" | grep -q '"route"'; then
    ROUTE_ID=$(echo "$ROUTE_RESPONSE" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
    echo "✅ Catchall route created: $ROUTE_ID"
else
    echo "⚠️  Route creation response: $ROUTE_RESPONSE"
fi

echo ""
echo "🔧 Configuring event webhooks..."

# Configure event webhook
WEBHOOK_RESPONSE=$(curl -s -u "api:${MAILGUN_API_KEY}" \
    https://api.mailgun.net/v3/domains/${MAILGUN_DOMAIN}/webhooks \
    -F id=tracking \
    -F url="${WEBHOOK_BASE_URL}/mailgun/events")

if echo "$WEBHOOK_RESPONSE" | grep -q '"webhook"'; then
    echo "✅ Event webhook configured"
else
    echo "⚠️  Webhook response: $WEBHOOK_RESPONSE"
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✅ Mailgun routes configured!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Verification:"
echo "  1. Check routes: https://app.mailgun.com/mg/routes"
echo "  2. Check webhooks: https://app.mailgun.com/mg/sending/domains/$MAILGUN_DOMAIN/webhooks"
echo "  3. Test inbound: Send email to support@insightpulseai.net"
echo ""
