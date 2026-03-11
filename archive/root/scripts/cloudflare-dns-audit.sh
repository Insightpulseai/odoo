#!/bin/bash
# =============================================================================
# Cloudflare DNS Proxy Audit Script
# =============================================================================
# Purpose: Audit all DNS records and verify proxy status against SSOT
# SSOT: infra/dns/subdomain-registry.yaml
# Output: JSON report showing proxy status for all records
# =============================================================================

set -euo pipefail

# Configuration
DOMAIN="insightpulseai.com"
CLOUDFLARE_API_TOKEN="${TF_VAR_cloudflare_api_token:-}"
CLOUDFLARE_API_BASE="https://api.cloudflare.com/client/v4"
EVIDENCE_DIR="docs/evidence/$(date +%Y%m%d-%H%M)-cloudflare-dns-audit"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Validation
if [[ -z "$CLOUDFLARE_API_TOKEN" ]]; then
  echo -e "${RED}ERROR: Cloudflare API token not found${NC}"
  echo "Set TF_VAR_cloudflare_api_token environment variable"
  exit 1
fi

# Create evidence directory
mkdir -p "$EVIDENCE_DIR"

# Get Zone ID for insightpulseai.com
echo "Fetching zone ID for $DOMAIN..."
ZONE_RESPONSE=$(curl -s -X GET \
  "${CLOUDFLARE_API_BASE}/zones?name=${DOMAIN}" \
  -H "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" \
  -H "Content-Type: application/json")

ZONE_ID=$(echo "$ZONE_RESPONSE" | jq -r '.result[0].id')

if [[ -z "$ZONE_ID" || "$ZONE_ID" == "null" ]]; then
  echo -e "${RED}ERROR: Failed to fetch zone ID${NC}"
  echo "$ZONE_RESPONSE" | jq '.'
  exit 1
fi

echo "Zone ID: $ZONE_ID"

# Fetch all DNS records
echo "Fetching DNS records..."
DNS_RECORDS=$(curl -s -X GET \
  "${CLOUDFLARE_API_BASE}/zones/${ZONE_ID}/dns_records?per_page=100" \
  -H "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" \
  -H "Content-Type: application/json")

# Save raw response
echo "$DNS_RECORDS" | jq '.' > "$EVIDENCE_DIR/raw-dns-records.json"

# Parse and analyze records
echo "Analyzing DNS records..."

# Extract relevant fields
echo "$DNS_RECORDS" | jq -r '.result[] |
  [.type, .name, .content, (.proxied | tostring), .id] |
  @tsv' > "$EVIDENCE_DIR/dns-records.tsv"

# Generate audit report
cat > "$EVIDENCE_DIR/audit-report.md" << 'EOF'
# Cloudflare DNS Proxy Audit Report

**Domain**: insightpulseai.com
**Date**: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
**SSOT**: infra/dns/subdomain-registry.yaml

## Summary

EOF

# Count records by type and proxy status
TOTAL_RECORDS=$(echo "$DNS_RECORDS" | jq '.result | length')
A_RECORDS=$(echo "$DNS_RECORDS" | jq '[.result[] | select(.type == "A")] | length')
CNAME_RECORDS=$(echo "$DNS_RECORDS" | jq '[.result[] | select(.type == "CNAME")] | length')
MX_RECORDS=$(echo "$DNS_RECORDS" | jq '[.result[] | select(.type == "MX")] | length')
TXT_RECORDS=$(echo "$DNS_RECORDS" | jq '[.result[] | select(.type == "TXT")] | length')

PROXIED_RECORDS=$(echo "$DNS_RECORDS" | jq '[.result[] | select(.proxied == true)] | length')
DNS_ONLY_RECORDS=$(echo "$DNS_RECORDS" | jq '[.result[] | select(.proxied == false)] | length')

cat >> "$EVIDENCE_DIR/audit-report.md" << EOF
- **Total Records**: $TOTAL_RECORDS
- **A Records**: $A_RECORDS
- **CNAME Records**: $CNAME_RECORDS
- **MX Records**: $MX_RECORDS
- **TXT Records**: $TXT_RECORDS
- **Proxied (Protected)**: $PROXIED_RECORDS
- **DNS-only (Unprotected)**: $DNS_ONLY_RECORDS

## Proxied Records (Protected by Cloudflare)

| Name | Type | Target | Record ID |
|------|------|--------|-----------|
EOF

echo "$DNS_RECORDS" | jq -r '.result[] | select(.proxied == true) |
  [.name, .type, .content, .id] | @tsv' | \
  awk -F'\t' '{printf "| %s | %s | %s | `%s` |\n", $1, $2, $3, $4}' \
  >> "$EVIDENCE_DIR/audit-report.md"

cat >> "$EVIDENCE_DIR/audit-report.md" << EOF

## DNS-only Records (Not Proxied)

| Name | Type | Target | Status | Record ID |
|------|------|--------|--------|-----------|
EOF

echo "$DNS_RECORDS" | jq -r '.result[] | select(.proxied == false) |
  [.name, .type, .content, .id] | @tsv' | \
  while IFS=$'\t' read -r name type content id; do
    # Determine if this should be DNS-only or needs proxy
    STATUS="✅ Correct"

    # Mail records should always be DNS-only
    if [[ "$type" == "MX" ]] || [[ "$type" == "TXT" ]]; then
      STATUS="✅ Correct (Mail)"
    # A and CNAME records should generally be proxied
    elif [[ "$type" == "A" ]] || [[ "$type" == "CNAME" ]]; then
      # Check if this is superset
      if [[ "$name" == *"superset"* ]]; then
        STATUS="⚠️ SHOULD BE PROXIED"
      else
        STATUS="⚠️ Needs Review"
      fi
    fi

    printf "| %s | %s | %s | %s | \`%s\` |\n" "$name" "$type" "$content" "$STATUS" "$id"
  done >> "$EVIDENCE_DIR/audit-report.md"

cat >> "$EVIDENCE_DIR/audit-report.md" << 'EOF'

## SSOT Compliance Check

Checking against `infra/dns/subdomain-registry.yaml`:

EOF

# Parse SSOT file and check compliance
if [[ -f "infra/dns/subdomain-registry.yaml" ]]; then
  echo "Parsing SSOT file..."

  # Extract subdomains from SSOT that should be proxied
  SSOT_PROXIED=$(yq eval '.subdomains[] | select(.cloudflare_proxied == true) | .name' infra/dns/subdomain-registry.yaml)

  echo "### Expected Proxied Subdomains (from SSOT)" >> "$EVIDENCE_DIR/audit-report.md"
  echo "" >> "$EVIDENCE_DIR/audit-report.md"

  for subdomain in $SSOT_PROXIED; do
    FQDN="${subdomain}.${DOMAIN}"

    # Check if this record exists and is proxied in Cloudflare
    ACTUAL_PROXIED=$(echo "$DNS_RECORDS" | jq -r --arg name "$FQDN" \
      '.result[] | select(.name == $name) | .proxied')

    if [[ "$ACTUAL_PROXIED" == "true" ]]; then
      echo "- ✅ **${subdomain}**: Proxied (compliant)" >> "$EVIDENCE_DIR/audit-report.md"
    elif [[ "$ACTUAL_PROXIED" == "false" ]]; then
      echo "- ⚠️ **${subdomain}**: NOT proxied (non-compliant)" >> "$EVIDENCE_DIR/audit-report.md"
    else
      echo "- ❌ **${subdomain}**: Record not found in Cloudflare" >> "$EVIDENCE_DIR/audit-report.md"
    fi
  done
else
  echo "⚠️ SSOT file not found: infra/dns/subdomain-registry.yaml" >> "$EVIDENCE_DIR/audit-report.md"
fi

cat >> "$EVIDENCE_DIR/audit-report.md" << 'EOF'

## Action Items

1. **Enable Proxy for superset.insightpulseai.com**
   - Currently DNS-only (unprotected)
   - Should be proxied per SSOT configuration
   - Security: Enable DDoS protection and WAF

2. **Verify Mail Records Remain DNS-only**
   - MX records must NOT be proxied
   - SPF/DKIM TXT records must NOT be proxied

## Next Steps

Run `scripts/cloudflare-enable-proxy.sh superset` to enable proxy for superset subdomain.

EOF

# Display report
echo -e "${GREEN}Audit complete!${NC}"
echo "Report saved to: $EVIDENCE_DIR/audit-report.md"
echo ""
cat "$EVIDENCE_DIR/audit-report.md"
