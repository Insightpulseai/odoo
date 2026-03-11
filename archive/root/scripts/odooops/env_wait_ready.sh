#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/_common.sh"

RUN_ID="${1:?missing RUN_ID}"
MAX_WAIT_SECONDS="${2:-1200}"  # 20 minutes default
SLEEP_SECONDS="${3:-5}"

deadline=$(( $(date +%s) + MAX_WAIT_SECONDS ))

echo "Waiting for run ${RUN_ID} to complete (timeout: ${MAX_WAIT_SECONDS}s)..." >&2

while true; do
  # Query ops.runs table for status
  resp=$(curl -fsS -G \
    "${SUPABASE_URL}/rest/v1/ops.runs" \
    --data-urlencode "run_id=eq.${RUN_ID}" \
    --data-urlencode "select=run_id,status,git_ref,started_at,finished_at" \
    -H "apikey: ${SUPABASE_ANON_KEY}" \
    -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}")

  # Parse status
  status=$(python - <<'PY' <<<"$resp"
import json,sys
try:
  d=json.load(sys.stdin)
  if isinstance(d, list) and len(d) > 0:
    print(d[0].get("status",""))
  else:
    print("")
except:
  print("")
PY
)

  if [[ -z "$status" ]]; then
    echo "env_wait_ready: run not found: ${RUN_ID}" >&2
    exit 1
  fi

  # Show latest log entries (last 5 lines)
  logs=$(curl -fsS -G \
    "${SUPABASE_URL}/rest/v1/ops.run_events" \
    --data-urlencode "run_id=eq.${RUN_ID}" \
    --data-urlencode "select=level,message,created_at" \
    --data-urlencode "order=created_at.desc" \
    --data-urlencode "limit=5" \
    -H "apikey: ${SUPABASE_ANON_KEY}" \
    -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" 2>/dev/null || echo "[]")

  recent_logs=$(python - <<'PY' <<<"$logs"
import json,sys
try:
  d=json.load(sys.stdin)
  if isinstance(d, list) and len(d) > 0:
    for entry in reversed(d):
      print(f"[{entry.get('level','')}] {entry.get('message','')}")
except:
  pass
PY
)

  if [[ -n "$recent_logs" ]]; then
    echo "Recent logs:" >&2
    echo "$recent_logs" >&2
  fi

  # Check terminal states
  case "$status" in
    success)
      echo "Run completed successfully: ${RUN_ID}" >&2

      # Get artifact URL if available
      artifacts=$(curl -fsS -G \
        "${SUPABASE_URL}/rest/v1/ops.artifacts" \
        --data-urlencode "run_id=eq.${RUN_ID}" \
        --data-urlencode "select=artifact_type,storage_path" \
        -H "apikey: ${SUPABASE_ANON_KEY}" \
        -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" 2>/dev/null || echo "[]")

      artifact_url=$(python - <<'PY' <<<"$artifacts"
import json,sys
try:
  d=json.load(sys.stdin)
  if isinstance(d, list) and len(d) > 0:
    print(d[0].get("storage_path",""))
except:
  print("")
PY
)

      if [[ -n "$artifact_url" ]]; then
        echo "$artifact_url"
      else
        echo "success"
      fi
      exit 0
      ;;

    failed)
      echo "Run failed: ${RUN_ID}" >&2
      echo "Check ops.run_events for error details" >&2
      exit 1
      ;;

    cancelled)
      echo "Run was cancelled: ${RUN_ID}" >&2
      exit 1
      ;;

    queued|claimed|running)
      echo "Status: ${status} - waiting..." >&2
      ;;

    *)
      echo "Unknown status: ${status}" >&2
      ;;
  esac

  # Check timeout
  if [[ "$(date +%s)" -ge "$deadline" ]]; then
    echo "env_wait_ready: timeout waiting for run ${RUN_ID} (status: ${status})" >&2
    exit 1
  fi

  sleep "$SLEEP_SECONDS"
done
