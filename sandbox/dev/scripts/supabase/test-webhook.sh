#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════════════
# Supabase Email Events - Test Webhook Script
# ═══════════════════════════════════════════════════════════════════════════════
# Purpose: Test the mailgun-events-proxy Edge Function with sample webhook
# Version: 1.0.0
# Date: 2026-01-28
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check environment
if [[ -z "${SUPABASE_URL:-}" ]]; then
    echo -e "${RED}✗ SUPABASE_URL not set${NC}"
    exit 1
fi

if [[ -z "${SUPABASE_ANON_KEY:-}" ]]; then
    echo -e "${RED}✗ SUPABASE_ANON_KEY not set${NC}"
    exit 1
fi

# Function URL
FUNCTION_URL="${SUPABASE_URL}/functions/v1/mailgun-events-proxy"

echo -e "${BLUE}Testing Mailgun Events Proxy Edge Function${NC}"
echo "URL: $FUNCTION_URL"
echo ""

# Sample Mailgun webhook payload
TIMESTAMP=$(date +%s)
TOKEN="test-token-$(date +%s%N)"

PAYLOAD=$(cat <<EOF
{
  "signature": {
    "timestamp": "$TIMESTAMP",
    "token": "$TOKEN",
    "signature": "test-signature-skip-verification"
  },
  "event-data": {
    "event": "delivered",
    "timestamp": $TIMESTAMP,
    "Message-Id": "<test-message-$(date +%s)@test.mailgun.org>",
    "recipient": "test@example.com",
    "sender": "noreply@test.com",
    "subject": "Test Email from Webhook Script",
    "delivery-status": {
      "message": "Message delivered successfully",
      "code": 250,
      "description": "OK"
    },
    "tags": ["test", "webhook-verification"],
    "campaigns": ["test-campaign"],
    "user-variables": {
      "test": true,
      "source": "verification-script",
      "timestamp": $TIMESTAMP
    }
  }
}
EOF
)

echo -e "${YELLOW}Sending test webhook...${NC}"
echo ""

RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$FUNCTION_URL" \
    -H "Content-Type: application/json" \
    -H "apikey: ${SUPABASE_ANON_KEY}" \
    -H "Authorization: Bearer ${SUPABASE_ANON_KEY}" \
    -d "$PAYLOAD")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

echo -e "${BLUE}Response:${NC}"
echo "HTTP Status: $HTTP_CODE"
echo "Body: $BODY"
echo ""

if [[ "$HTTP_CODE" == "200" ]]; then
    echo -e "${GREEN}✓ Webhook test successful!${NC}"
    echo ""
    echo "Event stored successfully."
    echo "Check Supabase Dashboard → Database → email.events"
    exit 0
else
    echo -e "${RED}✗ Webhook test failed${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Check Edge Function deployment: supabase functions list"
    echo "  2. Check Edge Function logs: supabase functions logs mailgun-events-proxy"
    echo "  3. Verify database schema: scripts/supabase/verify-integration.sh"
    exit 1
fi
