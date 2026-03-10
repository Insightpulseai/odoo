#!/usr/bin/env bash
# Verify Azure Container App health endpoint
set -euo pipefail

: "${RG:?RG required}"
: "${APP_NAME:?APP_NAME required}"

HEALTH_PATH="${HEALTH_PATH:-/web/health}"
MAX_RETRIES="${MAX_RETRIES:-12}"
RETRY_INTERVAL="${RETRY_INTERVAL:-10}"

# Get FQDN
FQDN=$(az containerapp show -n "$APP_NAME" -g "$RG" \
  --query "properties.configuration.ingress.fqdn" -o tsv)
echo "FQDN: $FQDN"

# Poll health endpoint
for i in $(seq 1 "$MAX_RETRIES"); do
  HTTP_STATUS=$(curl -sf -o /dev/null -w "%{http_code}" "https://${FQDN}${HEALTH_PATH}" || echo "000")
  echo "Attempt $i/$MAX_RETRIES: HTTP $HTTP_STATUS"

  if [[ "$HTTP_STATUS" = "200" ]]; then
    echo "PASS: health check passed"
    exit 0
  fi

  sleep "$RETRY_INTERVAL"
done

echo "FAIL: health check did not return 200 after $((MAX_RETRIES * RETRY_INTERVAL))s" >&2
exit 1
