#!/bin/bash
set -euo pipefail

# OdooOps Deploy Script
# Usage: deploy.sh [stage] [branch]

STAGE="${1:-preview}"
BRANCH="${2:-$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "main")}"
COMMIT_SHA="$(git rev-parse HEAD 2>/dev/null || echo "unknown")"

: "${ODOOOPS_API_BASE:?ODOOOPS_API_BASE not set}"
: "${ODOOOPS_TOKEN:?ODOOOPS_TOKEN not set}"
: "${ODOOOPS_PROJECT_ID:?ODOOOPS_PROJECT_ID not set}"

echo "Creating deployment for branch: ${BRANCH}" >&2
echo "Stage: ${STAGE}" >&2
echo "Commit SHA: ${COMMIT_SHA}" >&2
echo "" >&2

# Call existing env_create.sh script
BRANCH_NAME="${BRANCH}" COMMIT_SHA="${COMMIT_SHA}" STAGE="${STAGE}" \
  ENV_ID="$(bash "$(dirname "$0")/../../../../scripts/odooops/env_create.sh")"

echo "✓ Environment created: ${ENV_ID}" >&2
echo "" >&2
echo "Waiting for environment to be ready... (max 20 minutes)" >&2

# Call existing env_wait_ready.sh script
MAX_WAIT_SECONDS=1200 \
  ENV_URL="$(bash "$(dirname "$0")/../../../../scripts/odooops/env_wait_ready.sh" <<< "${ENV_ID}")"

echo "" >&2
echo "✓ Deployment successful!" >&2
echo "" >&2
echo "Environment URL: ${ENV_URL}" >&2
echo "Environment ID:  ${ENV_ID}" >&2
echo "Commit SHA:      ${COMMIT_SHA}" >&2

# Output JSON for programmatic use
cat <<JSON
{
  "environmentUrl": "${ENV_URL}",
  "environmentId": "${ENV_ID}",
  "commitSha": "${COMMIT_SHA}",
  "stage": "${STAGE}",
  "branch": "${BRANCH}"
}
JSON
