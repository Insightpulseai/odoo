#!/usr/bin/env bash
set -euo pipefail

ODOO_URL="${ODOO_URL:-https://erp.insightpulseai.com/web/login}"
MM_WEBHOOK_URL="${MM_WEBHOOK_URL:-}"
SERVICE_NAME="${SERVICE_NAME:-odoo-ce-prod}"
N8N_WEBHOOK_URL="${N8N_WEBHOOK_URL:-}"

timestamp=$(date -Iseconds)

start_ts=$(date +%s%3N)
http_code=$(curl -k -s -o /dev/null -w "%{http_code}" "${ODOO_URL}" || echo "000")
end_ts=$(date +%s%3N)
latency_ms=$((end_ts - start_ts))

status="ok"
text="✅ ${SERVICE_NAME} healthcheck OK at ${timestamp} (HTTP ${http_code}, ${latency_ms} ms)"

if [[ "${http_code}" != "200" && "${http_code}" != "302" && "${http_code}" != "303" ]]; then
  status="down"
  text="❌ ${SERVICE_NAME} healthcheck FAILED at ${timestamp} (HTTP ${http_code}, ${latency_ms} ms)"
fi

echo "[${timestamp}] ${text}"

# 1) Mattermost (existing)
if [[ -n "${MM_WEBHOOK_URL}" ]]; then
  payload=$(cat <<EOF
{"text": "${text}"}
EOF
)
  curl -s -X POST -H 'Content-Type: application/json' \
    -d "${payload}" "${MM_WEBHOOK_URL}" >/dev/null || true
fi

# 2) n8n metric ingest (new)
if [[ -n "${N8N_WEBHOOK_URL}" ]]; then
  n8n_payload=$(cat <<EOF
{
  "service_name": "${SERVICE_NAME}",
  "checked_at": "${timestamp}",
  "is_up": $( [[ "${status}" == "ok" ]] && echo "true" || echo "false" ),
  "http_code": ${http_code:-0},
  "latency_ms": ${latency_ms},
  "source": "cron"
}
EOF
)
  curl -s -X POST -H 'Content-Type: application/json' \
    -d "${n8n_payload}" "${N8N_WEBHOOK_URL}" >/dev/null || true
fi

# exit non-zero on failure so we can hook it if needed
if [[ "${status}" != "ok" ]]; then
  exit 1
fi
