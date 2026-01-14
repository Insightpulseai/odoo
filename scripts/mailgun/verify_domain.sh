#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# Mailgun Domain Verification Script
# Usage: ./verify_domain.sh
# Requires: MAILGUN_API_KEY, MAILGUN_DOMAIN, MAILGUN_REGION
# ============================================================

# Configuration from environment
API_KEY="${MAILGUN_API_KEY:-}"
DOMAIN="${MAILGUN_DOMAIN:-mg.insightpulseai.net}"
REGION="${MAILGUN_REGION:-us}"

# Validation
if [[ -z "$API_KEY" ]]; then
  echo "Error: MAILGUN_API_KEY not set" >&2
  echo "Export it first: export MAILGUN_API_KEY='your-key'" >&2
  exit 1
fi

# Set base URL based on region
if [[ "$REGION" == "eu" ]]; then
  BASE_URL="https://api.eu.mailgun.net/v3"
else
  BASE_URL="https://api.mailgun.net/v3"
fi

# Fetch domain verification status
echo "Fetching domain verification status for: $DOMAIN"
echo "Region: $REGION"
echo "---"

RESPONSE=$(curl -s --user "api:$API_KEY" \
  "$BASE_URL/domains/$DOMAIN" \
  -H "Accept: application/json")

# Check if request succeeded
if echo "$RESPONSE" | grep -q '"message":'; then
  echo "Error from Mailgun API:"
  echo "$RESPONSE" | grep -o '"message":"[^"]*"'
  exit 1
fi

# Parse and display key fields
echo "Domain Status:"
echo "$RESPONSE" | python3 -c "
import sys, json
data = json.load(sys.stdin)
domain = data.get('domain', {})

print(f\"  Domain: {domain.get('name', 'N/A')}\")
print(f\"  State: {domain.get('state', 'N/A')}\")
print(f\"  Created: {domain.get('created_at', 'N/A')}\")

# DNS records verification
receiving_records = domain.get('receiving_dns_records', [])
sending_records = domain.get('sending_dns_records', [])

print(\"\\nReceiving DNS Records (MX):\")
for rec in receiving_records:
    valid = '✅' if rec.get('valid') == 'valid' else '❌'
    print(f\"  {valid} {rec.get('record_type', 'N/A')} {rec.get('name', 'N/A')}\")
    print(f\"     Value: {rec.get('value', 'N/A')}\")

print(\"\\nSending DNS Records (SPF/DKIM):\")
for rec in sending_records:
    valid = '✅' if rec.get('valid') == 'valid' else '❌'
    print(f\"  {valid} {rec.get('record_type', 'N/A')} {rec.get('name', 'N/A')}\")
    if rec.get('record_type') == 'TXT':
        value = rec.get('value', 'N/A')
        if len(value) > 80:
            print(f\"     Value: {value[:80]}...\")
        else:
            print(f\"     Value: {value}\")
"

echo ""
echo "---"
echo "Full JSON response saved to: /tmp/mailgun_domain_status.json"
echo "$RESPONSE" | python3 -m json.tool > /tmp/mailgun_domain_status.json
