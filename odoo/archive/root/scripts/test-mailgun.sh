#!/usr/bin/env bash
# test-mailgun.sh — Test Mailgun email sending
#
# Usage:
#   ./scripts/test-mailgun.sh <recipient-email>
#
# Environment variables required:
#   MAILGUN_API_KEY - Your Mailgun API key
#   MAILGUN_DOMAIN  - Your sending domain (default: mg.insightpulseai.com)
#
# Example:
#   MAILGUN_API_KEY=key-xxx ./scripts/test-mailgun.sh you@example.com

set -euo pipefail

# Configuration
MAILGUN_DOMAIN="${MAILGUN_DOMAIN:-mg.insightpulseai.com}"
MAILGUN_API_URL="https://api.mailgun.net/v3/${MAILGUN_DOMAIN}/messages"

# Check required vars
if [[ -z "${MAILGUN_API_KEY:-}" ]]; then
    echo "ERROR: MAILGUN_API_KEY environment variable is required"
    echo "Usage: MAILGUN_API_KEY=key-xxx $0 <recipient-email>"
    exit 1
fi

if [[ $# -lt 1 ]]; then
    echo "ERROR: Recipient email required"
    echo "Usage: $0 <recipient-email>"
    exit 1
fi

RECIPIENT="$1"
TIMESTAMP=$(date -u +"%Y-%m-%d %H:%M:%S UTC")

echo "=== Mailgun Email Test ==="
echo "Domain: ${MAILGUN_DOMAIN}"
echo "Recipient: ${RECIPIENT}"
echo "Timestamp: ${TIMESTAMP}"
echo ""

# Send test email
echo "Sending test email..."
RESPONSE=$(curl -s -w "\n%{http_code}" \
    --user "api:${MAILGUN_API_KEY}" \
    "${MAILGUN_API_URL}" \
    -F from="InsightPulse AI <postmaster@${MAILGUN_DOMAIN}>" \
    -F to="${RECIPIENT}" \
    -F subject="[Test] Mailgun Configuration Verified - ${TIMESTAMP}" \
    -F text="This is a test email from InsightPulse AI.

Sent at: ${TIMESTAMP}
Domain: ${MAILGUN_DOMAIN}
Server: $(hostname -f 2>/dev/null || echo 'unknown')

If you received this email, your Mailgun configuration is working correctly.

--
InsightPulse AI Platform
https://insightpulseai.com")

# Parse response
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | head -n -1)

echo ""
echo "Response:"
echo "$BODY" | jq . 2>/dev/null || echo "$BODY"
echo ""
echo "HTTP Status: ${HTTP_CODE}"

if [[ "$HTTP_CODE" == "200" ]]; then
    echo ""
    echo "✅ SUCCESS: Email queued for delivery"
    echo "Check ${RECIPIENT} inbox (and spam folder) for the test email."
else
    echo ""
    echo "❌ FAILED: HTTP ${HTTP_CODE}"
    echo "Check your API key and domain configuration."
    exit 1
fi
