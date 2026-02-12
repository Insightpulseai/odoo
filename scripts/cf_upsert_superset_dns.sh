#!/usr/bin/env bash
set -euo pipefail

###############################################################################
# cf_upsert_superset_dns.sh
# Creates or updates an A record for superset.insightpulseai.com → 178.128.112.214
# via the Cloudflare API (idempotent).
###############################################################################

ZONE_NAME="insightpulseai.com"
RECORD_NAME="superset"
RECORD_TYPE="A"
TARGET_IP="178.128.112.214"
PROXIED=false  # Grey cloud (DNS only)
TTL=1          # Auto

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

echo "==> Checking if DNS record ${FQDN} already exists..."
EXISTING=$(curl -sS -X GET \
  "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/dns_records?type=${RECORD_TYPE}&name=${FQDN}" \
  -H "Authorization: Bearer ${CF_API_TOKEN}" \
  -H "Content-Type: application/json")

RECORD_ID=$(echo "${EXISTING}" | jq -r '.result[0].id // empty')

if [[ -n "${RECORD_ID}" ]]; then
  echo "    Found existing record ID: ${RECORD_ID}"
  echo "==> Updating DNS record..."
  curl -sS -X PUT \
    "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/dns_records/${RECORD_ID}" \
    -H "Authorization: Bearer ${CF_API_TOKEN}" \
    -H "Content-Type: application/json" \
    --data "{
      \"type\": \"${RECORD_TYPE}\",
      \"name\": \"${RECORD_NAME}\",
      \"content\": \"${TARGET_IP}\",
      \"ttl\": ${TTL},
      \"proxied\": ${PROXIED}
    }" | jq .
else
  echo "    No existing record found."
  echo "==> Creating DNS record..."
  curl -sS -X POST \
    "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/dns_records" \
    -H "Authorization: Bearer ${CF_API_TOKEN}" \
    -H "Content-Type: application/json" \
    --data "{
      \"type\": \"${RECORD_TYPE}\",
      \"name\": \"${RECORD_NAME}\",
      \"content\": \"${TARGET_IP}\",
      \"ttl\": ${TTL},
      \"proxied\": ${PROXIED}
    }" | jq .
fi

echo "==> DNS record upsert complete for ${FQDN} → ${TARGET_IP}"
