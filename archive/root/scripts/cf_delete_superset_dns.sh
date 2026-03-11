#!/usr/bin/env bash
set -euo pipefail

###############################################################################
# cf_delete_superset_dns.sh
# Deletes the A record for superset.insightpulseai.com via Cloudflare API
# (Rollback capability)
###############################################################################

ZONE_NAME="insightpulseai.com"
RECORD_NAME="superset"
RECORD_TYPE="A"

# Require CF_API_TOKEN from environment
: "${CF_API_TOKEN:?CF_API_TOKEN must be set}"

echo "==> Fetching zone ID for ${ZONE_NAME}..."
ZONE_ID=$(curl -sS -X GET \
  "https://api.cloudflare.com/client/v4/zones?name=${ZONE_NAME}" \
  -H "Authorization: Bearer ${CF_API_TOKEN}" \
  -H "Content-Type: application/json" \
| jq -r '.result[0].id // empty')

if [[ -z "${ZONE_ID}" ]]; then
  echo "ERROR: Could not find zone ID for ${ZONE_NAME}" >&2
  exit 1
fi

echo "    Zone ID: ${ZONE_ID}"

FQDN="${RECORD_NAME}.${ZONE_NAME}"

echo "==> Searching for DNS record ${FQDN}..."
EXISTING=$(curl -sS -X GET \
  "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/dns_records?type=${RECORD_TYPE}&name=${FQDN}" \
  -H "Authorization: Bearer ${CF_API_TOKEN}" \
  -H "Content-Type: application/json")

RECORD_ID=$(echo "${EXISTING}" | jq -r '.result[0].id // empty')

if [[ -z "${RECORD_ID}" ]]; then
  echo "    No DNS record found for ${FQDN}. Nothing to delete."
  exit 0
fi

echo "    Found record ID: ${RECORD_ID}"
echo "==> Deleting DNS record..."
curl -sS -X DELETE \
  "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/dns_records/${RECORD_ID}" \
  -H "Authorization: Bearer ${CF_API_TOKEN}" \
  -H "Content-Type: application/json" | jq .

echo "==> DNS record deleted for ${FQDN}"
