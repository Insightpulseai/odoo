#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/_common.sh"

# Parse arguments
PROJECT_ID="${1:?missing PROJECT_ID}"
WORKFLOW_TYPE="${2:-build}"  # build|deploy|test
GIT_REF="${3:?missing GIT_REF}"
COMMIT_SHA="${4:?missing COMMIT_SHA}"
ENV_ID="${5:-dev}"  # dev|staging|prod

# Generate run_id with timestamp for uniqueness
RUN_ID="run-$(date +%Y%m%d-%H%M%S)-${COMMIT_SHA:0:7}"

# Insert queued run into ops.runs
payload=$(cat <<JSON
{
  "run_id": "${RUN_ID}",
  "project_id": "${PROJECT_ID}",
  "env_id": "${ENV_ID}",
  "git_sha": "${COMMIT_SHA}",
  "git_ref": "${GIT_REF}",
  "status": "queued",
  "metadata": {
    "workflow_type": "${WORKFLOW_TYPE}",
    "created_by": "env_create.sh",
    "git_ref": "${GIT_REF}"
  }
}
JSON
)

# Insert into Supabase ops.runs table
resp=$(curl -fsS -X POST \
  "${SUPABASE_URL}/rest/v1/ops.runs" \
  -H "apikey: ${SUPABASE_ANON_KEY}" \
  -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" \
  -H "Content-Type: application/json" \
  -H "Prefer: return=representation" \
  -d "${payload}")

# Verify run was created
created_run_id=$(python - <<'PY' <<<"$resp"
import json,sys
try:
  d=json.load(sys.stdin)
  if isinstance(d, list) and len(d) > 0:
    print(d[0].get("run_id",""))
  else:
    print(d.get("run_id",""))
except:
  print("")
PY
)

if [[ -z "$created_run_id" ]]; then
  echo "env_create: failed to create run in ops.runs" >&2
  echo "Response: $resp" >&2
  exit 1
fi

# Return run_id for caller to poll
echo "$created_run_id"
