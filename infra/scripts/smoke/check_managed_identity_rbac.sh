#!/usr/bin/env bash
set -euo pipefail

: "${RESOURCE_GROUP:?RESOURCE_GROUP is required}"
: "${CONTAINER_APP_NAME:?CONTAINER_APP_NAME is required}"
: "${RBAC_SCOPE:?RBAC_SCOPE is required}"
: "${REQUIRED_ROLE_NAMES:?REQUIRED_ROLE_NAMES is required (comma-separated)}"

principal_id="$(
  az containerapp identity show \
    --resource-group "$RESOURCE_GROUP" \
    --name "$CONTAINER_APP_NAME" \
    --query principalId -o tsv
)"

if [[ -z "$principal_id" || "$principal_id" == "null" ]]; then
  echo "No managed identity principalId found for $CONTAINER_APP_NAME" >&2
  exit 1
fi

assigned_roles="$(
  az role assignment list \
    --assignee "$principal_id" \
    --scope "$RBAC_SCOPE" \
    --query "[].roleDefinitionName" -o tsv
)"

IFS=',' read -r -a required <<< "$REQUIRED_ROLE_NAMES"
for role in "${required[@]}"; do
  if ! grep -Fxq "$role" <<< "$assigned_roles"; then
    echo "Missing required role: $role" >&2
    exit 1
  fi
done

echo "Managed identity RBAC OK for $CONTAINER_APP_NAME"
