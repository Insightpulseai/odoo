#!/usr/bin/env bash
# assign-app-role.sh — Assign an Entra app role to a user or service principal.
#
# Usage:
#   ./scripts/entra/assign-app-role.sh \
#     --app-id <app-object-id> \
#     --principal-id <user-or-sp-object-id> \
#     --role-value <role-value>
#
# Example:
#   ./scripts/entra/assign-app-role.sh \
#     --app-id 00000000-0000-0000-0000-000000000000 \
#     --principal-id 11111111-1111-1111-1111-111111111111 \
#     --role-value finance.close.operator
#
# Prerequisites:
#   - Azure CLI authenticated (az login)
#   - Permissions: AppRoleAssignment.ReadWrite.All or Application administrator role
#
# Security notes:
#   - No secrets are hardcoded or logged
#   - Principal IDs are object IDs, not UPNs (no PII in arguments)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
MANIFEST="${REPO_ROOT}/infra/entra/app-roles-manifest.json"

# ---------------------------------------------------------------------------
# Parse arguments
# ---------------------------------------------------------------------------
APP_OBJECT_ID=""
PRINCIPAL_ID=""
ROLE_VALUE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --app-id)
      APP_OBJECT_ID="$2"
      shift 2
      ;;
    --principal-id)
      PRINCIPAL_ID="$2"
      shift 2
      ;;
    --role-value)
      ROLE_VALUE="$2"
      shift 2
      ;;
    --help|-h)
      echo "Usage: $0 --app-id <id> --principal-id <id> --role-value <value>"
      echo ""
      echo "Arguments:"
      echo "  --app-id        Azure AD app registration object ID (or set AZURE_APP_OBJECT_ID)"
      echo "  --principal-id  Object ID of the user or service principal to assign the role to"
      echo "  --role-value    Role value string (e.g., finance.close.operator)"
      echo ""
      echo "Available role values:"
      if [[ -f "${MANIFEST}" ]]; then
        jq -r '.appRoles[].value' "${MANIFEST}" | sed 's/^/  - /'
      fi
      exit 0
      ;;
    *)
      echo "ERROR: Unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

# Fall back to env var for app ID
if [[ -z "${APP_OBJECT_ID}" ]]; then
  APP_OBJECT_ID="${AZURE_APP_OBJECT_ID:-}"
fi

# ---------------------------------------------------------------------------
# Validate inputs
# ---------------------------------------------------------------------------
if [[ -z "${APP_OBJECT_ID}" ]]; then
  echo "ERROR: --app-id is required (or set AZURE_APP_OBJECT_ID)." >&2
  exit 1
fi

if [[ -z "${PRINCIPAL_ID}" ]]; then
  echo "ERROR: --principal-id is required." >&2
  exit 1
fi

if [[ -z "${ROLE_VALUE}" ]]; then
  echo "ERROR: --role-value is required." >&2
  exit 1
fi

if ! command -v az &>/dev/null; then
  echo "ERROR: Azure CLI (az) is not installed or not in PATH." >&2
  exit 1
fi

if ! az account show &>/dev/null; then
  echo "ERROR: Not authenticated. Run 'az login' first." >&2
  exit 1
fi

# ---------------------------------------------------------------------------
# Resolve role ID from manifest
# ---------------------------------------------------------------------------
if [[ ! -f "${MANIFEST}" ]]; then
  echo "ERROR: Manifest not found at ${MANIFEST}" >&2
  exit 1
fi

ROLE_ID=$(jq -r --arg val "${ROLE_VALUE}" '.appRoles[] | select(.value == $val) | .id' "${MANIFEST}")

if [[ -z "${ROLE_ID}" || "${ROLE_ID}" == "null" ]]; then
  echo "ERROR: Role value '${ROLE_VALUE}' not found in manifest." >&2
  echo "       Available roles:" >&2
  jq -r '.appRoles[].value' "${MANIFEST}" | sed 's/^/         - /' >&2
  exit 1
fi

echo "=== Entra App Role Assignment ==="
echo "App Object ID  : ${APP_OBJECT_ID}"
echo "Principal ID   : ${PRINCIPAL_ID}"
echo "Role Value     : ${ROLE_VALUE}"
echo "Role ID        : ${ROLE_ID}"
echo ""

# ---------------------------------------------------------------------------
# Get the service principal (enterprise app) for this app registration
# ---------------------------------------------------------------------------
echo "Resolving service principal for app registration..."
SP_ID=$(az ad sp list --filter "appId eq '$(az ad app show --id "${APP_OBJECT_ID}" --query appId -o tsv)'" --query "[0].id" -o tsv 2>/dev/null)

if [[ -z "${SP_ID}" || "${SP_ID}" == "None" ]]; then
  echo "ERROR: No service principal found for this app registration." >&2
  echo "       Create one first: az ad sp create --id <app-id>" >&2
  exit 1
fi

echo "Service Principal ID: ${SP_ID}"
echo ""

# ---------------------------------------------------------------------------
# Create the role assignment
# ---------------------------------------------------------------------------
echo "Assigning role..."
az rest \
  --method POST \
  --uri "https://graph.microsoft.com/v1.0/servicePrincipals/${SP_ID}/appRoleAssignedTo" \
  --headers "Content-Type=application/json" \
  --body "{
    \"principalId\": \"${PRINCIPAL_ID}\",
    \"resourceId\": \"${SP_ID}\",
    \"appRoleId\": \"${ROLE_ID}\"
  }"

if [[ $? -ne 0 ]]; then
  echo "ERROR: Failed to assign role." >&2
  exit 1
fi

echo ""
echo "Role assigned successfully."
echo ""

# ---------------------------------------------------------------------------
# Validate assignment
# ---------------------------------------------------------------------------
echo "Validating assignment..."
ASSIGNMENT_EXISTS=$(az rest \
  --method GET \
  --uri "https://graph.microsoft.com/v1.0/servicePrincipals/${SP_ID}/appRoleAssignedTo" \
  --query "value[?principalId=='${PRINCIPAL_ID}' && appRoleId=='${ROLE_ID}'] | length(@)" \
  -o tsv 2>/dev/null)

if [[ "${ASSIGNMENT_EXISTS}" -ge 1 ]]; then
  echo "Validation passed: role '${ROLE_VALUE}' is assigned to principal ${PRINCIPAL_ID}."
else
  echo "WARNING: Could not confirm assignment via query. Check manually:" >&2
  echo "         az rest --method GET --uri 'https://graph.microsoft.com/v1.0/servicePrincipals/${SP_ID}/appRoleAssignedTo'" >&2
fi

echo ""
echo "Done."
