#!/usr/bin/env bash
# Mailgun Test Email Script for InsightPulse AI
# Domain: mg.insightpulseai.com
#
# Usage:
#   export MAILGUN_API_KEY=key-xxxxx
#   ./scripts/mailgun/send_test_email.sh recipient@example.com
#
# Prerequisites:
#   - MAILGUN_API_KEY environment variable set
#   - curl installed

set -euo pipefail

MAILGUN_API_KEY="${MAILGUN_API_KEY:?Missing MAILGUN_API_KEY environment variable}"
MAILGUN_DOMAIN="${MAILGUN_DOMAIN:-mg.insightpulseai.com}"
RECIPIENT="${1:?Usage: $0 recipient@example.com}"
TIMESTAMP=$(date +%Y%m%d-%H%M)
EVIDENCE_DIR="docs/evidence/${TIMESTAMP}/mailgun"

echo "📧 Sending Test Email via Mailgun"
echo "=============================================="
echo "From: postmaster@${MAILGUN_DOMAIN}"
echo "To: ${RECIPIENT}"
echo ""

# Create evidence directory
mkdir -p "${EVIDENCE_DIR}"

# Send test email
result=$(curl -s --user "api:${MAILGUN_API_KEY}" \
    "https://api.mailgun.net/v3/${MAILGUN_DOMAIN}/messages" \
    -F "from=InsightPulse AI Test <postmaster@${MAILGUN_DOMAIN}>" \
    -F "to=${RECIPIENT}" \
    -F "subject=Mailgun Setup Test - $(date +%Y-%m-%d\ %H:%M:%S)" \
    -F "text=This is a test email from InsightPulse AI Mailgun setup.

Domain: ${MAILGUN_DOMAIN}
Timestamp: $(date -Iseconds)
Environment: $(hostname 2>/dev/null || echo 'unknown')

If you received this email, Mailgun is configured correctly.

--
InsightPulse AI DevOps" \
    -F "html=<html>
<body style='font-family: sans-serif; max-width: 600px; margin: 0 auto;'>
<h2>Mailgun Setup Test</h2>
<p>This is a test email from InsightPulse AI Mailgun setup.</p>
<table style='border-collapse: collapse; margin: 20px 0;'>
<tr><td style='padding: 8px; border: 1px solid #ddd;'><strong>Domain</strong></td><td style='padding: 8px; border: 1px solid #ddd;'>${MAILGUN_DOMAIN}</td></tr>
<tr><td style='padding: 8px; border: 1px solid #ddd;'><strong>Timestamp</strong></td><td style='padding: 8px; border: 1px solid #ddd;'>$(date -Iseconds)</td></tr>
</table>
<p style='color: #28a745;'>✅ If you received this email, Mailgun is configured correctly.</p>
<hr style='border: none; border-top: 1px solid #ddd; margin: 20px 0;'>
<p style='color: #666; font-size: 12px;'>InsightPulse AI DevOps</p>
</body>
</html>")

# Parse response
if echo "$result" | grep -q '"id"'; then
    message_id=$(echo "$result" | grep -o '"id"[[:space:]]*:[[:space:]]*"[^"]*"' | cut -d'"' -f4)
    echo "✅ Email sent successfully!"
    echo "   Message ID: ${message_id}"
    status="success"
else
    error_message=$(echo "$result" | grep -o '"message"[[:space:]]*:[[:space:]]*"[^"]*"' | cut -d'"' -f4 || echo "Unknown error")
    echo "❌ Failed to send email"
    echo "   Error: ${error_message}"
    echo "   Full response: ${result}"
    status="failed"
    message_id=""
fi

# Generate evidence
cat > "${EVIDENCE_DIR}/test_email.json" << EOF
{
  "timestamp": "$(date -Iseconds)",
  "domain": "${MAILGUN_DOMAIN}",
  "recipient": "${RECIPIENT}",
  "status": "${status}",
  "message_id": "${message_id:-null}",
  "response": $(echo "$result" | jq '.' 2>/dev/null || echo "\"${result}\"")
}
EOF

echo ""
echo "📄 Evidence written to: ${EVIDENCE_DIR}/test_email.json"

if [ "${status}" = "success" ]; then
    echo ""
    echo "📋 Next steps:"
    echo "   1. Check ${RECIPIENT} inbox (and spam folder)"
    echo "   2. Verify email headers show SPF/DKIM/DMARC pass"
    echo "   3. Check Mailgun dashboard for delivery status"
    exit 0
else
    exit 1
fi
