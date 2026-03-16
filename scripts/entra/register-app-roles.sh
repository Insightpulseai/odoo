#!/usr/bin/env bash
# register-app-roles.sh — Apply Entra app roles from manifest to an Azure AD app registration.
#
# Usage:
#   ./scripts/entra/register-app-roles.sh --app-id <app-object-id>
#   AZURE_APP_OBJECT_ID=<id> ./scripts/entra/register-app-roles.sh
#
# Prerequisites:
#   - Azure CLI authenticated (az login)
#   - Sufficient permissions: Application.ReadWrite.All or Application administrator role
#
# Security notes:
#   - No secrets are hardcoded or logged
#   - The manifest contains only role definitions, no credentials

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
MANIFEST="${REPO_ROOT}/infra/entra/app-roles-manifest.json"

# ---------------------------------------------------------------------------
# Parse arguments
# ---------------------------------------------------------------------------
APP_OBJECT_ID=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --app-id)
      APP_OBJECT_ID="$2"
      shift 2
      ;;
    --help|-h)
      echo "Usage: $0 [--app-id <azure-app-object-id>]"
      echo ""
      echo "If --app-id is not provided, the script reads AZURE_APP_OBJECT_ID from the environment."
      exit 0
      ;;
    *)
      echo "ERROR: Unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

# Fall back to env var
if [[ -z "${APP_OBJECT_ID}" ]]; then
  APP_OBJECT_ID="${AZURE_APP_OBJECT_ID:-}"
fi

if [[ -z "${APP_OBJECT_ID}" ]]; then
  echo "ERROR: No app object ID provided." >&2
  echo "       Pass --app-id <id> or set AZURE_APP_OBJECT_ID." >&2
  exit 1
fi

# ---------------------------------------------------------------------------
# Validate prerequisites
# ---------------------------------------------------------------------------
if ! command -v az &>/dev/null; then
  echo "ERROR: Azure CLI (az) is not installed or not in PATH." >&2
  exit 1
fi

if ! az account show &>/dev/null; then
  echo "ERROR: Not authenticated. Run 'az login' first." >&2
  exit 1
fi

if [[ ! -f "${MANIFEST}" ]]; then
  echo "ERROR: Manifest not found at ${MANIFEST}" >&2
  exit 1
fi

# ---------------------------------------------------------------------------
# Validate manifest structure
# ---------------------------------------------------------------------------
ROLE_COUNT=$(jq '.appRoles | length' "${MANIFEST}")
if [[ "${ROLE_COUNT}" -lt 1 ]]; then
  echo "ERROR: Manifest contains no app roles." >&2
  exit 1
fi

echo "=== Entra App Role Registration ==="
echo "App Object ID : ${APP_OBJECT_ID}"
echo "Manifest      : ${MANIFEST}"
echo "Role count    : ${ROLE_COUNT}"
echo ""

# ---------------------------------------------------------------------------
# Extract appRoles array and apply
# ---------------------------------------------------------------------------
APP_ROLES_JSON=$(jq -c '.appRoles' "${MANIFEST}")

echo "Applying app roles to app registration..."
az ad app update \
  --id "${APP_OBJECT_ID}" \
  --app-roles "${APP_ROLES_JSON}"

if [[ $? -ne 0 ]]; then
  echo "ERROR: Failed to apply app roles." >&2
  exit 1
fi

echo "App roles applied successfully."
echo ""

# ---------------------------------------------------------------------------
# Validate — fetch back and compare counts
# ---------------------------------------------------------------------------
echo "Validating applied roles..."
APPLIED_COUNT=$(az ad app show --id "${APP_OBJECT_ID}" --query "appRoles | length(@)" -o tsv)

if [[ "${APPLIED_COUNT}" -ne "${ROLE_COUNT}" ]]; then
  echo "WARNING: Expected ${ROLE_COUNT} roles, found ${APPLIED_COUNT} in app registration." >&2
  echo "         Some roles may have been merged or rejected. Inspect manually:" >&2
  echo "         az ad app show --id ${APP_OBJECT_ID} --query appRoles" >&2
  exit 1
fi

echo "Validation passed: ${APPLIED_COUNT} roles registered."
echo ""

# ---------------------------------------------------------------------------
# Print summary
# ---------------------------------------------------------------------------
echo "Registered roles:"
az ad app show --id "${APP_OBJECT_ID}" --query "appRoles[].{value:value, displayName:displayName, enabled:isEnabled}" -o table

echo ""
echo "Done. Roles are now available for assignment via Entra portal or assign-app-role.sh."
