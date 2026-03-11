#!/bin/bash
# deploy-n8n-workflows.sh
# Programmatic n8n workflow deployment using n8n REST API
# Replaces manual UI import from Phase 3 of deployment plan

set -e  # Exit on any error

# Color output for readability
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
N8N_BASE_URL="${N8N_BASE_URL:-https://n8n.insightpulseai.com}"
N8N_API_KEY="${N8N_JWT:-${N8N_API_KEY}}"  # Use N8N_JWT if available, fallback to N8N_API_KEY
WORKFLOW_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../automations/n8n/workflows" && pwd)"

# Validation
if [ -z "$N8N_API_KEY" ]; then
  echo -e "${RED}ERROR: N8N_JWT or N8N_API_KEY environment variable not set${NC}"
  echo "Please set N8N_JWT in ~/.zshrc or export it before running this script"
  echo "Example: export N8N_JWT='eyJhbGci...'"
  exit 1
fi

if [ ! -d "$WORKFLOW_DIR" ]; then
  echo -e "${RED}ERROR: Workflow directory not found: $WORKFLOW_DIR${NC}"
  exit 1
fi

echo -e "${GREEN}=== n8n Workflow Deployment Script ===${NC}"
echo "Base URL: $N8N_BASE_URL"
echo "Workflow Directory: $WORKFLOW_DIR"
echo ""

# Function to create or update workflow
deploy_workflow() {
  local workflow_file="$1"
  local workflow_name=$(basename "$workflow_file" .json)

  echo -e "${YELLOW}Processing: $workflow_name${NC}"

  # Check if file exists
  if [ ! -f "$workflow_file" ]; then
    echo -e "${RED}  ERROR: File not found${NC}"
    return 1
  fi

  # Read workflow JSON and filter to only allowed fields for API
  # Note: 'active' is read-only on creation, set via separate activate endpoint
  local workflow_data=$(cat "$workflow_file" | jq '{
    name: .name,
    nodes: .nodes,
    connections: .connections,
    settings: .settings
  }')

  # Extract workflow ID if present (for updates) from original file
  local workflow_id=$(cat "$workflow_file" | jq -r '.id // empty')

  if [ -z "$workflow_id" ]; then
    # Create new workflow
    echo "  Creating new workflow..."
    local response=$(curl -s -w "\n%{http_code}" -X POST \
      "$N8N_BASE_URL/api/v1/workflows" \
      -H "X-N8N-API-KEY: $N8N_API_KEY" \
      -H "Content-Type: application/json" \
      -d "$workflow_data")

    local http_code=$(echo "$response" | tail -n1)
    local response_body=$(echo "$response" | sed '$d')

    if [ "$http_code" = "200" ] || [ "$http_code" = "201" ]; then
      local new_id=$(echo "$response_body" | jq -r '.id')
      echo -e "${GREEN}  ✓ Created successfully (ID: $new_id)${NC}"

      # Activate workflow
      activate_workflow "$new_id"
    else
      echo -e "${RED}  ✗ Creation failed (HTTP $http_code)${NC}"
      echo "  Response: $response_body"
      return 1
    fi
  else
    # Update existing workflow
    echo "  Updating existing workflow (ID: $workflow_id)..."
    local response=$(curl -s -w "\n%{http_code}" -X PUT \
      "$N8N_BASE_URL/api/v1/workflows/$workflow_id" \
      -H "X-N8N-API-KEY: $N8N_API_KEY" \
      -H "Content-Type: application/json" \
      -d "$workflow_data")

    local http_code=$(echo "$response" | tail -n1)
    local response_body=$(echo "$response" | sed '$d')

    if [ "$http_code" = "200" ]; then
      echo -e "${GREEN}  ✓ Updated successfully${NC}"

      # Activate workflow
      activate_workflow "$workflow_id"
    else
      echo -e "${RED}  ✗ Update failed (HTTP $http_code)${NC}"
      echo "  Response: $response_body"
      return 1
    fi
  fi
}

# Function to activate workflow
activate_workflow() {
  local workflow_id="$1"

  echo "  Activating workflow..."
  # n8n API requires PUT to update workflow with active: true
  local response=$(curl -s -w "\n%{http_code}" -X PUT \
    "$N8N_BASE_URL/api/v1/workflows/$workflow_id" \
    -H "X-N8N-API-KEY: $N8N_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"active\": true}")

  local http_code=$(echo "$response" | tail -n1)

  if [ "$http_code" = "200" ]; then
    echo -e "${GREEN}  ✓ Activated successfully${NC}"
  else
    local response_body=$(echo "$response" | sed '$d')
    echo -e "${YELLOW}  ⚠ Activation via PUT failed (HTTP $http_code)${NC}"
    echo -e "${YELLOW}  Note: Manually activate workflow in n8n UI if needed${NC}"
  fi
}

# Main deployment loop
deployed_count=0
failed_count=0

for workflow_file in "$WORKFLOW_DIR"/*.json; do
  if [ -f "$workflow_file" ]; then
    if deploy_workflow "$workflow_file"; then
      ((deployed_count++))
    else
      ((failed_count++))
    fi
    echo ""
  fi
done

# Summary
echo -e "${GREEN}=== Deployment Summary ===${NC}"
echo "Total workflows processed: $((deployed_count + failed_count))"
echo -e "${GREEN}Successful: $deployed_count${NC}"
if [ $failed_count -gt 0 ]; then
  echo -e "${RED}Failed: $failed_count${NC}"
  exit 1
else
  echo -e "${GREEN}All workflows deployed successfully!${NC}"
fi
