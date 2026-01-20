#!/usr/bin/env bash
# Mailgun SMTP Connection Test for InsightPulse AI
# Domain: mg.insightpulseai.net
#
# Usage: ./scripts/mailgun/test_smtp.sh

set -euo pipefail

SMTP_HOST="${SMTP_HOST:-smtp.mailgun.org}"
SMTP_PORT="${SMTP_PORT:-465}"
TIMESTAMP=$(date +%Y%m%d-%H%M)
EVIDENCE_DIR="docs/evidence/${TIMESTAMP}/mailgun"

echo "🔌 Testing SMTP Connection to ${SMTP_HOST}:${SMTP_PORT}"
echo "=============================================="
echo ""

# Create evidence directory
mkdir -p "${EVIDENCE_DIR}"

# Test SSL connection
echo "Testing SSL/TLS connection..."
smtp_result=$(timeout 10 openssl s_client -connect "${SMTP_HOST}:${SMTP_PORT}" -quiet 2>&1 <<< "EHLO insightpulseai.net
QUIT" || echo "CONNECTION_FAILED")

if echo "$smtp_result" | grep -q "250"; then
    echo "✅ SMTP connection successful"
    smtp_status="pass"
    # Extract server capabilities
    capabilities=$(echo "$smtp_result" | grep "^250" | head -20)
    echo ""
    echo "Server capabilities:"
    echo "$capabilities" | sed 's/^/  /'
else
    echo "❌ SMTP connection failed"
    smtp_status="fail"
    echo "Response:"
    echo "$smtp_result" | head -20
fi

# Also test port 587 (STARTTLS)
echo ""
echo "Testing STARTTLS on port 587..."
starttls_result=$(timeout 10 openssl s_client -connect "${SMTP_HOST}:587" -starttls smtp -quiet 2>&1 <<< "EHLO insightpulseai.net
QUIT" || echo "CONNECTION_FAILED")

if echo "$starttls_result" | grep -q "250"; then
    echo "✅ STARTTLS connection successful"
    starttls_status="pass"
else
    echo "⚠️  STARTTLS connection not available or failed"
    starttls_status="fail"
fi

# Generate evidence
cat > "${EVIDENCE_DIR}/smtp_test.json" << EOF
{
  "timestamp": "$(date -Iseconds)",
  "smtp_host": "${SMTP_HOST}",
  "tests": {
    "port_465_ssl": "${smtp_status}",
    "port_587_starttls": "${starttls_status}"
  },
  "status": "$([ "${smtp_status}" = "pass" ] && echo "PASS" || echo "FAIL")"
}
EOF

echo ""
echo "📄 Evidence written to: ${EVIDENCE_DIR}/smtp_test.json"

if [ "${smtp_status}" = "pass" ]; then
    echo ""
    echo "✅ SMTP test passed!"
    exit 0
else
    echo ""
    echo "❌ SMTP test failed. Check firewall rules and credentials."
    exit 1
fi
