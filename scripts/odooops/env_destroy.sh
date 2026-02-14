#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/_common.sh"

RUN_ID="${1:?missing RUN_ID}"

# Mark run as cancelled in ops.runs
payload='{"status":"cancelled"}'

resp=$(curl -fsS -X PATCH \
  "${SUPABASE_URL}/rest/v1/ops.runs?run_id=eq.${RUN_ID}" \
  -H "apikey: ${SUPABASE_ANON_KEY}" \
  -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" \
  -H "Content-Type: application/json" \
  -H "Prefer: return=representation" \
  -d "${payload}")

# Add cancel event to ops.run_events
event_payload=$(cat <<JSON
{
  "run_id": "${RUN_ID}",
  "level": "info",
  "message": "Run cancelled by env_destroy.sh",
  "payload": {
    "action": "cancel",
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  }
}
JSON
)

curl -fsS -X POST \
  "${SUPABASE_URL}/rest/v1/ops.run_events" \
  -H "apikey: ${SUPABASE_ANON_KEY}" \
  -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" \
  -H "Content-Type: application/json" \
  -d "${event_payload}" >/dev/null

echo "cancelled:${RUN_ID}"
