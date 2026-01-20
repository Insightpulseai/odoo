#!/usr/bin/env bash
# Mailgun Webhook Setup Script for InsightPulse AI
# Domain: mg.insightpulseai.net
#
# Usage:
#   export MAILGUN_API_KEY=key-xxxxx
#   ./scripts/mailgun/setup_webhooks.sh
#
# Prerequisites:
#   - MAILGUN_API_KEY environment variable set
#   - curl and jq installed

set -euo pipefail

MAILGUN_API_KEY="${MAILGUN_API_KEY:?Missing MAILGUN_API_KEY environment variable}"
MAILGUN_DOMAIN="${MAILGUN_DOMAIN:-mg.insightpulseai.net}"
WEBHOOK_URL="${WEBHOOK_URL:-https://n8n.insightpulseai.net/webhook/mailgun-events}"
TIMESTAMP=$(date +%Y%m%d-%H%M)
EVIDENCE_DIR="docs/evidence/${TIMESTAMP}/mailgun"

echo "🔧 Mailgun Webhook Setup for ${MAILGUN_DOMAIN}"
echo "=============================================="
echo "📡 Webhook URL: ${WEBHOOK_URL}"
echo ""

# Create evidence directory
mkdir -p "${EVIDENCE_DIR}"

api() {
    curl -sS --user "api:${MAILGUN_API_KEY}" "$@"
}

# Webhook events to configure
EVENTS=("delivered" "permanent_fail" "temporary_fail" "complained" "unsubscribed" "opened" "clicked")

declare -A webhook_results

echo "Setting up webhooks..."
echo ""

for event in "${EVENTS[@]}"; do
    echo "  → Configuring ${event} webhook..."

    # Delete existing webhook if present (ignore errors)
    api -X DELETE "https://api.mailgun.net/v3/domains/${MAILGUN_DOMAIN}/webhooks/${event}" 2>/dev/null || true

    # Create new webhook
    result=$(api -X POST "https://api.mailgun.net/v3/domains/${MAILGUN_DOMAIN}/webhooks" \
        -F "id=${event}" \
        -F "url=${WEBHOOK_URL}" 2>&1)

    if echo "$result" | grep -q '"webhook"'; then
        echo "    ✅ ${event}: configured"
        webhook_results["${event}"]="configured"
    elif echo "$result" | grep -q '"message"'; then
        message=$(echo "$result" | jq -r '.message // "Unknown error"')
        echo "    ⚠️  ${event}: ${message}"
        webhook_results["${event}"]="warning: ${message}"
    else
        echo "    ❌ ${event}: failed"
        echo "       Response: ${result}"
        webhook_results["${event}"]="failed"
    fi
done

echo ""
echo "🔍 Verifying webhook configuration..."
echo ""

# Get current webhooks
webhooks_json=$(api "https://api.mailgun.net/v3/domains/${MAILGUN_DOMAIN}/webhooks" 2>&1)

if command -v jq &> /dev/null; then
    echo "Configured webhooks:"
    echo "$webhooks_json" | jq -r '.webhooks | to_entries[] | "  • \(.key): \(.value.urls[0] // "not set")"'
else
    echo "$webhooks_json"
fi

# Generate JSON evidence
cat > "${EVIDENCE_DIR}/webhook_setup.json" << EOF
{
  "timestamp": "$(date -Iseconds)",
  "domain": "${MAILGUN_DOMAIN}",
  "webhook_url": "${WEBHOOK_URL}",
  "events_configured": $(printf '%s\n' "${!webhook_results[@]}" | jq -R -s -c 'split("\n") | map(select(. != ""))'),
  "results": {
$(for event in "${EVENTS[@]}"; do
    echo "    \"${event}\": \"${webhook_results[$event]:-unknown}\","
done | sed '$ s/,$//')
  },
  "verification_response": $(echo "$webhooks_json" | jq '.' 2>/dev/null || echo '{}')
}
EOF

echo ""
echo "📄 Evidence written to: ${EVIDENCE_DIR}/webhook_setup.json"

# Generate markdown report
cat > "${EVIDENCE_DIR}/webhook_setup.md" << EOF
# Mailgun Webhook Setup Report

**Domain:** ${MAILGUN_DOMAIN}
**Webhook URL:** ${WEBHOOK_URL}
**Timestamp:** $(date -Iseconds)

## Configured Events

| Event | Purpose | Status |
|-------|---------|--------|
| delivered | Successful delivery | ${webhook_results["delivered"]:-pending} |
| permanent_fail | Hard bounces | ${webhook_results["permanent_fail"]:-pending} |
| temporary_fail | Soft bounces | ${webhook_results["temporary_fail"]:-pending} |
| complained | Spam reports | ${webhook_results["complained"]:-pending} |
| unsubscribed | Opt-outs | ${webhook_results["unsubscribed"]:-pending} |
| opened | Email opens | ${webhook_results["opened"]:-pending} |
| clicked | Link clicks | ${webhook_results["clicked"]:-pending} |

## Next Steps

1. Get your Webhook Signing Key from Mailgun Dashboard
2. Add \`MAILGUN_WEBHOOK_SIGNING_KEY\` to n8n/Supabase environment
3. Enable tracking in Mailgun: Send → Domain Settings → Tracking
4. Test webhook endpoint:
   \`\`\`bash
   curl -X POST ${WEBHOOK_URL} \\
     -H 'Content-Type: application/json' \\
     -d '{"event":"test","recipient":"test@example.com"}'
   \`\`\`
EOF

echo "📄 Report written to: ${EVIDENCE_DIR}/webhook_setup.md"
echo ""
echo "✅ Webhook setup complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Get your Webhook Signing Key from Mailgun Dashboard"
echo "   2. Add MAILGUN_WEBHOOK_SIGNING_KEY to your n8n/Supabase environment"
echo "   3. Enable tracking in Mailgun: Send → Domain Settings → Tracking"
echo "   4. Test with:"
echo "      curl -X POST ${WEBHOOK_URL} -H 'Content-Type: application/json' -d '{\"event\":\"test\"}'"
