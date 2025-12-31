#!/bin/bash
# activate-n8n-workflows.sh
# Activate deployed n8n workflows programmatically

set -e

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
N8N_BASE_URL="${N8N_BASE_URL:-https://n8n.insightpulseai.net}"
N8N_API_KEY="${N8N_JWT:-${N8N_API_KEY}}"

# Validation
if [ -z "$N8N_API_KEY" ]; then
  echo -e "${RED}ERROR: N8N_JWT environment variable not set${NC}"
  echo "Run: source ~/.zshrc"
  exit 1
fi

echo -e "${GREEN}=== n8n Workflow Activation Script ===${NC}"
echo ""

# List of workflow IDs to activate (from latest deployment)
WORKFLOW_IDS=(
  "REucTgGSmARUVe0w"  # finance_closing_automation
  "K2f9hlsKiWigQfVD"  # odoo_reverse_mapper
  "V7plxQgTKeeVR5WX"  # ppm_monthly_close_automation
)

activate_workflow() {
  local workflow_id="$1"
  
  echo -e "${YELLOW}Activating workflow: $workflow_id${NC}"
  
  # Fetch current workflow
  local workflow=$(curl -s -X GET \
    "$N8N_BASE_URL/api/v1/workflows/$workflow_id" \
    -H "X-N8N-API-KEY: $N8N_API_KEY")
  
  # Update with active: true
  local response=$(curl -s -w "\n%{http_code}" -X PUT \
    "$N8N_BASE_URL/api/v1/workflows/$workflow_id" \
    -H "X-N8N-API-KEY: $N8N_API_KEY" \
    -H "Content-Type: application/json" \
    -d "$(echo "$workflow" | jq '. + {active: true}')")
  
  local http_code=$(echo "$response" | tail -n1)
  local response_body=$(echo "$response" | sed '$d')
  
  if [ "$http_code" = "200" ]; then
    local name=$(echo "$response_body" | jq -r '.name')
    echo -e "${GREEN}  ✓ Activated: $name${NC}"
  else
    echo -e "${RED}  ✗ Activation failed (HTTP $http_code)${NC}"
    echo "  Response: $(echo "$response_body" | jq -r '.message // .error // "Unknown error"')"
  fi
  echo ""
}

# Activate all workflows
for workflow_id in "${WORKFLOW_IDS[@]}"; do
  activate_workflow "$workflow_id"
done

echo -e "${GREEN}=== Activation Complete ===${NC}"
echo "Check status: https://n8n.insightpulseai.net"
