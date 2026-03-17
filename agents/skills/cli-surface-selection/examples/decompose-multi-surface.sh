#!/usr/bin/env bash
# Example: Decompose a multi-surface task into sub-tasks
set -euo pipefail

echo "=== Multi-surface task decomposition ==="
echo "Task: Deploy ML model from Databricks to Azure serving"
echo ""
echo "Sub-task 1:"
echo '  {"surface": "DATABRICKS_CLI", "skill": "databricks-ml-serving-ops", "task": "Export model from registry"}'
echo ""
echo "Sub-task 2:"
echo '  {"surface": "DATABRICKS_CLI", "skill": "databricks-ml-serving-ops", "task": "Create serving endpoint"}'
echo ""
echo "Sub-task 3:"
echo '  {"surface": "AZURE_CLI", "skill": "azure-cli-safe", "task": "Configure Azure Front Door route to endpoint"}'
echo ""
echo "Execution order: sequential (each depends on previous)"
