#!/usr/bin/env bash
# cli-surface-selection: Validate a routing decision for cross-platform misuse
# Usage: validate-routing.sh <surface> "<task-description>"
set -euo pipefail

SURFACE="${1:?Usage: validate-routing.sh <surface> \"<task-description>\"}"
TASK="${2:?Usage: validate-routing.sh <surface> \"<task-description>\"}"

echo "Validating routing: ${SURFACE} for task: ${TASK}"

# Check for cross-platform misuse
VALID=true
REASON=""

case "${SURFACE}" in
  DATABRICKS_CLI)
    if echo "${TASK}" | grep -qiE "odoo|odoo-bin|module|scaffold"; then
      VALID=false
      REASON="Databricks CLI cannot be used for Odoo operations"
    fi
    ;;
  ODOO_CLI)
    if echo "${TASK}" | grep -qiE "databricks|notebook|cluster|warehouse"; then
      VALID=false
      REASON="Odoo CLI cannot be used for Databricks operations"
    fi
    ;;
  AZURE_CLI)
    if echo "${TASK}" | grep -qiE "databricks workspace|notebook|databricks job"; then
      VALID=false
      REASON="Azure CLI should not be used for Databricks workspace operations — use Databricks CLI"
    fi
    ;;
esac

if [ "${VALID}" = true ]; then
  echo "VALID: Routing ${SURFACE} is appropriate for this task"
  exit 0
else
  echo "INVALID: ${REASON}"
  exit 1
fi
