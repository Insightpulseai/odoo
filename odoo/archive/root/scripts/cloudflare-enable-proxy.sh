#!/bin/bash
# =============================================================================
# Cloudflare DNS Proxy Enablement Script
# =============================================================================
# Purpose: Enable Cloudflare proxy for a specific subdomain
# Usage: ./cloudflare-enable-proxy.sh <subdomain>
# Example: ./cloudflare-enable-proxy.sh superset
# =============================================================================

set -euo pipefail

# Configuration
DOMAIN="insightpulseai.com"
CLOUDFLARE_API_TOKEN="${TF_VAR_cloudflare_api_token:-}"
CLOUDFLARE_API_BASE="https://api.cloudflare.com/client/v4"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Validation
if [[ $# -eq 0 ]]; then
  echo -e "${RED}ERROR: Subdomain required${NC}"
  echo "Usage: $0 <subdomain>"
  echo "Example: $0 superset"
  exit 1
fi

SUBDOMAIN="$1"
FQDN="${SUBDOMAIN}.${DOMAIN}"

if [[ -z "$CLOUDFLARE_API_TOKEN" ]]; then
  echo -e "${RED}ERROR: Cloudflare API token not found${NC}"
  echo "Set TF_VAR_cloudflare_api_token environment variable"
  exit 1
fi

echo "Enabling Cloudflare proxy for: $FQDN"

# Get Zone ID
echo "Fetching zone ID..."
ZONE_RESPONSE=$(curl -s -X GET \
  "${CLOUDFLARE_API_BASE}/zones?name=${DOMAIN}" \
  -H "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" \
  -H "Content-Type: application/json")

ZONE_ID=$(echo "$ZONE_RESPONSE" | jq -r '.result[0].id')

if [[ -z "$ZONE_ID" || "$ZONE_ID" == "null" ]]; then
  echo -e "${RED}ERROR: Failed to fetch zone ID${NC}"
  exit 1
fi

echo "Zone ID: $ZONE_ID"

# Find the DNS record
echo "Finding DNS record for $FQDN..."
RECORD_RESPONSE=$(curl -s -X GET \
  "${CLOUDFLARE_API_BASE}/zones/${ZONE_ID}/dns_records?name=${FQDN}" \
  -H "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" \
  -H "Content-Type: application/json")

RECORD_ID=$(echo "$RECORD_RESPONSE" | jq -r '.result[0].id')
RECORD_TYPE=$(echo "$RECORD_RESPONSE" | jq -r '.result[0].type')
RECORD_CONTENT=$(echo "$RECORD_RESPONSE" | jq -r '.result[0].content')
RECORD_PROXIED=$(echo "$RECORD_RESPONSE" | jq -r '.result[0].proxied')

if [[ -z "$RECORD_ID" || "$RECORD_ID" == "null" ]]; then
  echo -e "${RED}ERROR: DNS record not found for $FQDN${NC}"
  exit 1
fi

echo "Record found:"
echo "  ID: $RECORD_ID"
echo "  Type: $RECORD_TYPE"
echo "  Content: $RECORD_CONTENT"
echo "  Proxied: $RECORD_PROXIED"

# Check if already proxied
if [[ "$RECORD_PROXIED" == "true" ]]; then
  echo -e "${GREEN}✅ Record is already proxied${NC}"
  exit 0
fi

# Enable proxy
echo "Enabling proxy..."
UPDATE_RESPONSE=$(curl -s -X PATCH \
  "${CLOUDFLARE_API_BASE}/zones/${ZONE_ID}/dns_records/${RECORD_ID}" \
  -H "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" \
  -H "Content-Type: application/json" \
  --data "{
    \"type\": \"${RECORD_TYPE}\",
    \"name\": \"${FQDN}\",
    \"content\": \"${RECORD_CONTENT}\",
    \"proxied\": true
  }")

SUCCESS=$(echo "$UPDATE_RESPONSE" | jq -r '.success')

if [[ "$SUCCESS" == "true" ]]; then
  echo -e "${GREEN}✅ Successfully enabled proxy for $FQDN${NC}"

  # Verify the change
  echo "Verifying change..."
  VERIFY_RESPONSE=$(curl -s -X GET \
    "${CLOUDFLARE_API_BASE}/zones/${ZONE_ID}/dns_records/${RECORD_ID}" \
    -H "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" \
    -H "Content-Type: application/json")

  VERIFY_PROXIED=$(echo "$VERIFY_RESPONSE" | jq -r '.result.proxied')

  if [[ "$VERIFY_PROXIED" == "true" ]]; then
    echo -e "${GREEN}✅ Verification passed: Record is now proxied${NC}"

    # Save evidence
    EVIDENCE_DIR="docs/evidence/$(date +%Y%m%d-%H%M)-cloudflare-proxy-enable"
    mkdir -p "$EVIDENCE_DIR"

    cat > "$EVIDENCE_DIR/change-log.json" << EOF
{
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "action": "enable_proxy",
  "subdomain": "${SUBDOMAIN}",
  "fqdn": "${FQDN}",
  "record_id": "${RECORD_ID}",
  "record_type": "${RECORD_TYPE}",
  "record_content": "${RECORD_CONTENT}",
  "previous_state": "DNS-only (proxied: false)",
  "new_state": "Proxied (proxied: true)",
  "verification": "passed"
}
EOF

    echo "Evidence saved to: $EVIDENCE_DIR/change-log.json"
  else
    echo -e "${RED}⚠️ Verification failed: Proxy status not updated${NC}"
    exit 1
  fi
else
  echo -e "${RED}ERROR: Failed to enable proxy${NC}"
  echo "$UPDATE_RESPONSE" | jq '.'
  exit 1
fi
