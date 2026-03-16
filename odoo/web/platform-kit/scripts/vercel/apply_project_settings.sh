#!/usr/bin/env bash
#
# Vercel Project Settings (Infrastructure as Code)
#
# Applies recommended Vercel project settings via REST API.
# This ensures settings are tracked in git and reproducible.
#
# Usage:
#   export VERCEL_TOKEN="***"
#   export VERCEL_PROJECT_ID="prj_***"
#   export VERCEL_TEAM_ID="team_***"  # optional for personal accounts
#   ./apply_project_settings.sh
#
# Optional overrides:
#   NODE_VERSION=22.x BUILD_MACHINE_TYPE=enhanced ./apply_project_settings.sh
#
set -euo pipefail

# Required environment variables
: "${VERCEL_TOKEN:?Missing VERCEL_TOKEN}"
: "${VERCEL_PROJECT_ID:?Missing VERCEL_PROJECT_ID}"
: "${VERCEL_TEAM_ID:=}"  # optional

# Configurable settings with sensible defaults
# - Node 22.x matches package.json engines >=22
# - enhanced is cost-effective; use turbo only for very large monorepos
NODE_VERSION="${NODE_VERSION:-22.x}"
BUILD_MACHINE_TYPE="${BUILD_MACHINE_TYPE:-enhanced}"
FLUID_COMPUTE="${FLUID_COMPUTE:-false}"

echo "Applying Vercel project settings:"
echo "  Project ID: ${VERCEL_PROJECT_ID}"
echo "  Node Version: ${NODE_VERSION}"
echo "  Build Machine: ${BUILD_MACHINE_TYPE}"
echo "  Fluid Compute: ${FLUID_COMPUTE}"
echo ""

# Build JSON payload
payload=$(cat <<EOF
{
  "nodeVersion": "${NODE_VERSION}",
  "resourceConfig": {
    "buildMachineType": "${BUILD_MACHINE_TYPE}",
    "fluid": ${FLUID_COMPUTE}
  }
}
EOF
)

# Build query string for team ID
qs=""
if [ -n "${VERCEL_TEAM_ID}" ]; then
  qs="?teamId=${VERCEL_TEAM_ID}"
fi

# Apply settings via PATCH
response=$(curl -sS -X PATCH \
  -H "Authorization: Bearer ${VERCEL_TOKEN}" \
  -H "Content-Type: application/json" \
  "https://api.vercel.com/v9/projects/${VERCEL_PROJECT_ID}${qs}" \
  --data "${payload}")

# Check for errors
if echo "${response}" | grep -q '"error"'; then
  echo "ERROR: Failed to update project settings"
  echo "${response}" | python3 -m json.tool 2>/dev/null || echo "${response}"
  exit 1
fi

echo "SUCCESS: Project settings updated"
echo ""
echo "Verification:"
echo "${response}" | python3 -c "
import json, sys
p = json.load(sys.stdin)
print('  name:', p.get('name'))
print('  nodeVersion:', p.get('nodeVersion'))
rc = p.get('resourceConfig') or {}
print('  buildMachineType:', rc.get('buildMachineType'))
print('  fluid:', rc.get('fluid'))
" 2>/dev/null || echo "${response}" | head -c 500
