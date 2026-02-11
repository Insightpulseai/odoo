#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/_common.sh"

: "${BRANCH_NAME:?missing BRANCH_NAME}"
: "${COMMIT_SHA:?missing COMMIT_SHA}"
: "${STAGE:=dev}"  # dev|staging|prod (policy-driven)

# TODO: align payload and endpoint to your actual OdooOps implementation
payload=$(cat <<JSON
{
  "branch": "${BRANCH_NAME}",
  "commit_sha": "${COMMIT_SHA}",
  "stage": "${STAGE}"
}
JSON
)

resp=$(curl -fsS -X POST \
  -H "$(hdr_auth)" \
  -H "Content-Type: application/json" \
  "${ODOOOPS_API_BASE}/projects/${ODOOOPS_PROJECT_ID}/envs" \
  -d "${payload}")

# Expecting {"env_id":"..."}; adjust if your schema differs.
env_id=$(python - <<'PY' <<<"$resp"
import json,sys
d=json.load(sys.stdin)
print(d.get("env_id",""))
PY
)

if [[ -z "$env_id" ]]; then
  echo "env_create: could not parse env_id from response:" >&2
  echo "$resp" >&2
  exit 1
fi

echo "$env_id"
