#!/usr/bin/env bash
# cli-surface-selection: Route a task description to the correct CLI surface
# Usage: route-task.sh "<task-description>"
# This is a helper script — real routing logic is in the agent prompt
set -euo pipefail

TASK="${1:?Usage: route-task.sh \"<task-description>\"}"

# Keyword-based routing (simplified — full logic is agent-driven)
if echo "${TASK}" | grep -qiE "databricks|workspace|notebook|cluster|job|pipeline|experiment|model.*(registry|serving)|warehouse|spark"; then
  echo '{"surface": "DATABRICKS_CLI", "reasoning": "Task involves Databricks platform operations"}'
elif echo "${TASK}" | grep -qiE "odoo|odoo-bin|module|scaffold|addons|ir_module|test.*odoo|neutralize|populate|cloc"; then
  echo '{"surface": "ODOO_CLI", "reasoning": "Task involves Odoo runtime/admin operations"}'
elif echo "${TASK}" | grep -qiE "az |azure|container.?app|acr|keyvault|resource.?group"; then
  echo '{"surface": "AZURE_CLI", "reasoning": "Task involves Azure resource management"}'
elif echo "${TASK}" | grep -qiE "azd |azure.?dev"; then
  echo '{"surface": "AZD", "reasoning": "Task involves Azure Developer CLI operations"}'
elif echo "${TASK}" | grep -qiE "odo |openshift"; then
  echo '{"surface": "REJECTED", "reasoning": "odo is deprecated — use canonical alternatives"}'
else
  echo '{"surface": "OTHER", "reasoning": "Task does not clearly map to a known CLI surface"}'
fi
