#!/bin/bash
set -euo pipefail

# Usage: ./import_via_api.sh YOUR_N8N_API_KEY

if [ $# -eq 0 ]; then
    echo "Usage: $0 <n8n-api-key>"
    echo "Get your API key from: https://n8n.insightpulseai.com → Settings → API"
    exit 1
fi

N8N_API_KEY="$1"
N8N_URL="https://n8n.insightpulseai.com/api/v1/workflows"

echo "🚀 Importing workflows to n8n via API..."
echo ""

# Function to import workflow
import_workflow() {
    local file="$1"
    local name=$(basename "$file")

    # Clean workflow JSON (remove read-only fields)
    local cleaned=$(jq 'del(.id, .meta, .tags) | walk(if type == "object" and has("id") then del(.id) else . end)' "$file")

    # Import via API
    local response=$(echo "$cleaned" | curl -s -X POST "$N8N_URL" \
        -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
        -H "Content-Type: application/json" \
        -d @-)

    # Check result
    local workflow_id=$(echo "$response" | jq -r '.id // empty')
    local workflow_name=$(echo "$response" | jq -r '.name // empty')
    local error_msg=$(echo "$response" | jq -r '.message // empty')

    if [ -n "$workflow_id" ]; then
        echo "✅ $name: $workflow_name (ID: $workflow_id)"

        # Activate workflow
        curl -s -X PATCH "${N8N_URL}/${workflow_id}" \
            -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
            -H "Content-Type: application/json" \
            -d '{"active": true}' > /dev/null

        echo "   🟢 Activated"
    else
        echo "❌ $name: $error_msg"
    fi
    echo ""
}

# Import read-only workflows
echo "📖 Read-Only Workflows:"
for file in automations/n8n/workflows/claude-ai-mcp/read-only/*.json; do
    import_workflow "$file"
done

# Import write-path workflows
echo "✍️  Write-Path Workflows:"
for file in automations/n8n/workflows/claude-ai-mcp/write-path/*.json; do
    import_workflow "$file"
done

echo "✅ Import complete!"
echo ""
echo "Next steps:"
echo "1. Verify workflows in n8n UI: https://n8n.insightpulseai.com"
echo "2. Configure Claude.ai connector"
echo "3. Test integration"
