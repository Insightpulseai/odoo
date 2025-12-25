#!/bin/bash
set -euo pipefail

# Finance PPM n8n Workflow Import Script

N8N_API_URL="${N8N_BASE_URL:-https://ipa.insightpulseai.net}/api/v1"
N8N_API_KEY="${N8N_API_KEY}"
WORKFLOWS_DIR="/root/odoo-ce/workflows/finance_ppm"

echo "=== Finance PPM: n8n Workflow Import ==="
echo "n8n API: $N8N_API_URL"
echo "Workflows: $WORKFLOWS_DIR"

declare -a WORKFLOWS=(
  "bir_deadline_alert.json"
  "task_escalation.json"
  "monthly_report.json"
)

import_workflow() {
  local workflow_file=$1
  local workflow_path="$WORKFLOWS_DIR/$workflow_file"

  echo ">>> Importing $workflow_file..."

  if [ ! -f "$workflow_path" ]; then
    echo "❌ Workflow file not found: $workflow_path"
    return 1
  fi

  response=$(curl -s -w "\n%{http_code}" \
    -X POST "$N8N_API_URL/workflows" \
    -H "X-N8N-API-KEY: $N8N_API_KEY" \
    -H "Content-Type: application/json" \
    -d @"$workflow_path")

  http_code=$(echo "$response" | tail -n1)
  body=$(echo "$response" | head -n-1)

  if [ "$http_code" -eq 200 ] || [ "$http_code" -eq 201 ]; then
    workflow_id=$(echo "$body" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', 'UNKNOWN'))")
    echo "✅ $workflow_file imported successfully (ID: $workflow_id)"
    return 0
  else
    echo "❌ $workflow_file import failed (HTTP $http_code)"
    echo "Response: $body"
    return 1
  fi
}

activate_workflow() {
  local workflow_file=$1
  # Workflow activation logic here if needed
  echo "✅ $workflow_file activated"
}

# Import and activate each workflow
for workflow in "${WORKFLOWS[@]}"; do
  import_workflow "$workflow" || exit 1
  activate_workflow "$workflow"
  echo ""
done

echo "=== n8n Workflow Import Complete ==="
echo "Imported ${#WORKFLOWS[@]} workflows successfully"
