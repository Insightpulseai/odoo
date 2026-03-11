#!/usr/bin/env bash
# Add Azure Front Door custom domain validation TXT records to Cloudflare
# Requires: CLOUDFLARE_API_TOKEN and CLOUDFLARE_ZONE_ID
# Both should be sourced from Azure Key Vault:
#   export CLOUDFLARE_API_TOKEN=$(az keyvault secret show --vault-name kv-ipai-dev --name cloudflare-dns-api-token --query value -o tsv)
#   export CLOUDFLARE_ZONE_ID=$(az keyvault secret show --vault-name kv-ipai-dev --name cloudflare-zone-id --query value -o tsv)
set -euo pipefail

: "${CLOUDFLARE_API_TOKEN:?Missing CLOUDFLARE_API_TOKEN — set from Key Vault}"
: "${CLOUDFLARE_ZONE_ID:?Missing CLOUDFLARE_ZONE_ID — set from Key Vault}"

API="https://api.cloudflare.com/client/v4"
RG="rg-ipai-shared-dev"
PROFILE="ipai-fd-dev"

add_txt_record() {
  local name="$1" content="$2"
  echo "Adding TXT: $name → $content"

  # Check if record already exists
  existing=$(curl -sf -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
    "$API/zones/$CLOUDFLARE_ZONE_ID/dns_records?type=TXT&name=${name}.insightpulseai.com" \
    | python3 -c "import sys,json; r=json.load(sys.stdin)['result']; print(len(r))" 2>/dev/null)

  if [ "$existing" -gt 0 ]; then
    echo "  → Already exists, skipping"
    return 0
  fi

  curl -sf -X POST \
    -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
    -H "Content-Type: application/json" \
    "$API/zones/$CLOUDFLARE_ZONE_ID/dns_records" \
    -d "{
      \"type\": \"TXT\",
      \"name\": \"$name\",
      \"content\": \"$content\",
      \"ttl\": 300,
      \"proxied\": false
    }" | python3 -c "import sys,json; r=json.load(sys.stdin); print('  →', 'OK' if r['success'] else r['errors'])" 2>/dev/null
}

echo "=== Azure Front Door DNS Validation Records ==="
echo "Profile: $PROFILE | RG: $RG"
echo ""

# Fetch fresh validation tokens from Azure
for domain_name in erp n8n mcp plane shelf crm superset ocr auth "" www erp-azure n8n-azure; do
  if [ -z "$domain_name" ]; then
    cf_domain="insightpulseai-com"
    dns_name="_dnsauth"
  else
    cf_domain="${domain_name}-insightpulseai-com"
    dns_name="_dnsauth.${domain_name}"
  fi

  token=$(az afd custom-domain show \
    --profile-name "$PROFILE" \
    --custom-domain-name "$cf_domain" \
    -g "$RG" \
    --query "validationProperties.validationToken" -o tsv 2>/dev/null)

  if [ -n "$token" ]; then
    add_txt_record "$dns_name" "$token"
  else
    echo "SKIP: No validation token for $cf_domain"
  fi
done

echo ""
echo "=== Done. Validation tokens expire in 7 days. ==="
echo "Azure Front Door will auto-validate and issue managed TLS certificates."
