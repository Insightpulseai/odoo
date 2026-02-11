#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/_common.sh"

: "${ENV_ID:?missing ENV_ID}"
: "${MAX_WAIT_SECONDS:=1200}"
: "${SLEEP_SECONDS:=5}"

deadline=$(( $(date +%s) + MAX_WAIT_SECONDS ))

while true; do
  resp=$(curl -fsS -H "$(hdr_auth)" "${ODOOOPS_API_BASE}/envs/${ENV_ID}")
  ready=$(python - <<'PY' <<<"$resp"
import json,sys
d=json.load(sys.stdin)
print(str(d.get("ready", False)).lower())
PY
)
  url=$(python - <<'PY' <<<"$resp"
import json,sys
d=json.load(sys.stdin)
print(d.get("url",""))
PY
)

  if [[ "$ready" == "true" && -n "$url" ]]; then
    echo "$url"
    exit 0
  fi

  if [[ "$(date +%s)" -ge "$deadline" ]]; then
    echo "env_wait_ready: timeout waiting for ENV_ID=$ENV_ID" >&2
    echo "$resp" >&2
    exit 1
  fi

  sleep "$SLEEP_SECONDS"
done
