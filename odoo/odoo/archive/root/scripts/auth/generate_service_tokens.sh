#!/bin/bash
set -euo pipefail

# =============================================================================
# Service Token Generator for InsightPulse AI Platform
# =============================================================================
# Generates JWT tokens for all platform services (n8n, Superset, MCP)
# Tokens are valid for 24 hours by default
#
# Usage:
#   ./scripts/auth/generate_service_tokens.sh
#   ./scripts/auth/generate_service_tokens.sh --exp 86400  # 24 hours
#
# Output:
#   - Tokens printed to stdout
#   - Optional: Save to .env.tokens for runtime use
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Default expiration: 24 hours
EXP=${1:-86400}

echo "🔐 Generating service tokens (expires in ${EXP}s = $((EXP / 3600))h)..."
echo ""

# Service definitions: subject | scope
declare -a SERVICES=(
    "svc:n8n|workflow:execute,ai:call,mcp:invoke,ocr:read"
    "svc:superset|ai:call,mcp:invoke,analytics:read"
    "svc:mcp|ai:call,ocr:read,workflow:trigger"
    "svc:docflow|ocr:read,ai:call,mcp:invoke,document:process"
    "svc:analytics|ai:call,analytics:read,analytics:write"
)

for service_def in "${SERVICES[@]}"; do
    IFS='|' read -r subject scope <<< "$service_def"

    echo "📦 ${subject}"
    token=$(python3 "$SCRIPT_DIR/mint_token.py" --sub "$subject" --scope "$scope" --exp "$EXP" 2>/dev/null | grep -A1 "Token:" | tail -1)

    # Extract service name from subject (e.g., svc:n8n -> N8N)
    service_name=$(echo "$subject" | sed 's/svc://' | tr '[:lower:]' '[:upper:]')

    echo "   Scope: $scope"
    echo "   Token: ${token:0:50}..."
    echo "   Variable: ${service_name}_JWT_TOKEN"
    echo ""
done

echo "✅ All service tokens generated"
echo ""
echo "💡 Usage examples:"
echo "   # n8n HTTP Request node"
echo "   curl -H 'Authorization: Bearer \$N8N_JWT_TOKEN' https://api.insightpulseai.com/v1/ai"
echo ""
echo "   # Superset SQL Lab"
echo "   curl -H 'Authorization: Bearer \$SUPERSET_JWT_TOKEN' https://api.insightpulseai.com/v1/analytics"
echo ""
echo "   # MCP server invocation"
echo "   curl -H 'Authorization: Bearer \$MCP_JWT_TOKEN' https://api.insightpulseai.com/v1/mcp"
