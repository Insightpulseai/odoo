#!/usr/bin/env bash
# =============================================================================
# apply_project_settings.sh — Apply Vercel project settings from SSOT JSON
# =============================================================================
# Usage:
#   VERCEL_TOKEN=<token> bash scripts/vercel/apply_project_settings.sh ops-console
#
# Required env:
#   VERCEL_TOKEN  — Vercel personal access token (project scope minimum)
#
# What it does:
#   1. Reads infra/vercel/projects/<name>.json
#   2. PATCHes /v9/projects/{projectId} with rootDirectory + nodeVersion + framework
#   3. Verifies the response matches expected values
#   4. Exits 0 on success, 1 on any failure
#
# Idempotent: safe to run repeatedly — PATCH overwrites with same values.
# =============================================================================
set -euo pipefail

NAME="${1:-ops-console}"
REPO_ROOT="$(git rev-parse --show-toplevel)"
SSOT_FILE="${REPO_ROOT}/infra/vercel/projects/${NAME}.json"

# ── Validate prerequisites ───────────────────────────────────────────────────
if [[ -z "${VERCEL_TOKEN:-}" ]]; then
  echo "ERROR: VERCEL_TOKEN is not set." >&2
  echo "  Set it via: export VERCEL_TOKEN=<your_vercel_personal_access_token>" >&2
  echo "  (Get from: https://vercel.com/account/tokens)" >&2
  exit 1
fi

if [[ ! -f "${SSOT_FILE}" ]]; then
  echo "ERROR: SSOT file not found: ${SSOT_FILE}" >&2
  exit 1
fi

if ! command -v python3 &>/dev/null; then
  echo "ERROR: python3 required" >&2; exit 1
fi
if ! command -v curl &>/dev/null; then
  echo "ERROR: curl required" >&2; exit 1
fi

# ── Read SSOT fields ──────────────────────────────────────────────────────────
PROJECT_ID=$(python3 -c "import json; d=json.load(open('${SSOT_FILE}')); print(d['projectId'])")
ROOT_DIR=$(python3 -c "import json; d=json.load(open('${SSOT_FILE}')); print(d.get('rootDirectory') or 'null')")
NODE_VER=$(python3 -c "import json; d=json.load(open('${SSOT_FILE}')); print(d.get('nodeVersion','20.x'))")
FRAMEWORK=$(python3 -c "import json; d=json.load(open('${SSOT_FILE}')); print(d.get('framework','nextjs'))")

echo "=== Vercel Project Settings Apply ==="
echo "  Project ID   : ${PROJECT_ID}"
echo "  rootDirectory: ${ROOT_DIR}"
echo "  nodeVersion  : ${NODE_VER}"
echo "  framework    : ${FRAMEWORK}"
echo ""

# ── Build PATCH payload ───────────────────────────────────────────────────────
if [[ "${ROOT_DIR}" == "null" ]]; then
  ROOT_PAYLOAD='null'
else
  ROOT_PAYLOAD="\"${ROOT_DIR}\""
fi

PAYLOAD=$(cat <<EOF
{
  "rootDirectory": ${ROOT_PAYLOAD},
  "nodeVersion": "${NODE_VER}",
  "framework": "${FRAMEWORK}"
}
EOF
)

# ── Apply settings ────────────────────────────────────────────────────────────
echo "Sending PATCH to Vercel API..."
RESPONSE=$(curl -s -X PATCH \
  "https://api.vercel.com/v9/projects/${PROJECT_ID}" \
  -H "Authorization: Bearer ${VERCEL_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "${PAYLOAD}")

# ── Verify response ───────────────────────────────────────────────────────────
ACTUAL_ROOT=$(python3 -c "import json; d=json.loads('''${RESPONSE}'''); print(d.get('rootDirectory','ERROR'))" 2>/dev/null || echo "PARSE_ERROR")
ACTUAL_NODE=$(python3 -c "import json; d=json.loads('''${RESPONSE}'''); print(d.get('nodeVersion','ERROR'))" 2>/dev/null || echo "PARSE_ERROR")
API_ERR=$(python3 -c "import json; d=json.loads('''${RESPONSE}'''); print(d.get('error',{}).get('message',''))" 2>/dev/null || echo "")

if [[ -n "${API_ERR}" && "${API_ERR}" != "None" ]]; then
  echo "ERROR: Vercel API returned error: ${API_ERR}" >&2
  echo "Full response: ${RESPONSE}" >&2
  exit 1
fi

echo "  Response rootDirectory: ${ACTUAL_ROOT}"
echo "  Response nodeVersion  : ${ACTUAL_NODE}"

# ── Validate ──────────────────────────────────────────────────────────────────
FAIL=0
if [[ "${ACTUAL_ROOT}" != "${ROOT_DIR}" && "${ROOT_DIR}" != "null" ]]; then
  echo "FAIL: rootDirectory mismatch (got '${ACTUAL_ROOT}', want '${ROOT_DIR}')" >&2
  FAIL=1
fi
if [[ "${ACTUAL_NODE}" != "${NODE_VER}" ]]; then
  echo "FAIL: nodeVersion mismatch (got '${ACTUAL_NODE}', want '${NODE_VER}')" >&2
  FAIL=1
fi

if [[ "${FAIL}" -eq 0 ]]; then
  echo ""
  echo "✅ PASS — Vercel project settings applied successfully."
  echo "   rootDirectory = ${ACTUAL_ROOT}"
  echo "   nodeVersion   = ${ACTUAL_NODE}"
  echo ""
  echo "Next: trigger a production redeploy so new settings take effect:"
  echo "   vercel redeploy <latest-deployment-url> --prod"
else
  exit 1
fi
