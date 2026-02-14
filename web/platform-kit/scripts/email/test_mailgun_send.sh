#!/usr/bin/env bash
# =============================================================================
# Mailgun Test Email Script
# Sends a test email via Mailgun API to verify configuration
# =============================================================================

set -euo pipefail

# Configuration
MG_DOMAIN="${MAILGUN_DOMAIN:-mg.insightpulseai.com}"
MG_API_KEY="${MAILGUN_API_KEY:-}"
TEST_TO="${1:-}"

# Validate inputs
if [ -z "$MG_API_KEY" ]; then
    echo "Error: MAILGUN_API_KEY environment variable is not set"
    echo "Usage: MAILGUN_API_KEY=key-xxx ./test_mailgun_send.sh recipient@example.com"
    exit 1
fi

if [ -z "$TEST_TO" ]; then
    echo "Error: No recipient email provided"
    echo "Usage: ./test_mailgun_send.sh recipient@example.com"
    exit 1
fi

echo "Sending test email..."
echo "  From: test@${MG_DOMAIN}"
echo "  To: ${TEST_TO}"
echo "  Via: Mailgun API"
echo ""

RESPONSE=$(curl -s --user "api:${MG_API_KEY}" \
    "https://api.mailgun.net/v3/${MG_DOMAIN}/messages" \
    -F from="InsightPulse AI Test <test@${MG_DOMAIN}>" \
    -F to="${TEST_TO}" \
    -F subject="[Test] Mailgun Configuration Verified - $(date +%Y-%m-%d\ %H:%M:%S)" \
    -F text="This is a test email from InsightPulse AI.

Configuration Details:
- Mailgun Domain: ${MG_DOMAIN}
- Sent via: Mailgun API
- Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)

If you received this email, your Mailgun configuration is working correctly.

---
InsightPulse AI Platform
https://insightpulseai.com" \
    -F html="<html>
<body style='font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;'>
    <h2 style='color: #333;'>Mailgun Configuration Verified</h2>
    <p>This is a test email from <strong>InsightPulse AI</strong>.</p>

    <table style='border-collapse: collapse; width: 100%; margin: 20px 0;'>
        <tr style='background: #f5f5f5;'>
            <td style='padding: 10px; border: 1px solid #ddd;'><strong>Mailgun Domain</strong></td>
            <td style='padding: 10px; border: 1px solid #ddd;'>${MG_DOMAIN}</td>
        </tr>
        <tr>
            <td style='padding: 10px; border: 1px solid #ddd;'><strong>Sent via</strong></td>
            <td style='padding: 10px; border: 1px solid #ddd;'>Mailgun API</td>
        </tr>
        <tr style='background: #f5f5f5;'>
            <td style='padding: 10px; border: 1px solid #ddd;'><strong>Timestamp</strong></td>
            <td style='padding: 10px; border: 1px solid #ddd;'>$(date -u +%Y-%m-%dT%H:%M:%SZ)</td>
        </tr>
    </table>

    <p style='color: #28a745;'>✓ If you received this email, your Mailgun configuration is working correctly.</p>

    <hr style='border: none; border-top: 1px solid #ddd; margin: 20px 0;'>
    <p style='color: #666; font-size: 12px;'>
        InsightPulse AI Platform<br>
        <a href='https://insightpulseai.com'>https://insightpulseai.com</a>
    </p>
</body>
</html>")

echo "Response:"
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"

if echo "$RESPONSE" | grep -q '"id":'; then
    echo ""
    echo "✓ Email sent successfully!"
    MESSAGE_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', 'N/A'))" 2>/dev/null || echo "N/A")
    echo "  Message ID: $MESSAGE_ID"
else
    echo ""
    echo "✗ Failed to send email"
    exit 1
fi
