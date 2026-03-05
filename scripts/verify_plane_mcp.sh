#!/bin/bash
# Plane MCP Server Verification Script
# Tests the self-hosted Plane MCP integration
# Usage: ./scripts/verify_plane_mcp.sh

set -euo pipefail

echo "==================================="
echo "Plane MCP Verification"
echo "==================================="
echo ""

# Check if required environment variables are set
echo "1. Checking environment variables..."
MISSING_VARS=()

if [ -z "${PLANE_API_URL:-}" ]; then
  MISSING_VARS+=("PLANE_API_URL")
fi
if [ -z "${PLANE_API_KEY:-}" ]; then
  MISSING_VARS+=("PLANE_API_KEY")
fi
if [ -z "${PLANE_WORKSPACE_SLUG:-}" ]; then
  MISSING_VARS+=("PLANE_WORKSPACE_SLUG")
fi

if [ ${#MISSING_VARS[@]} -gt 0 ]; then
  echo "❌ Missing required environment variables: ${MISSING_VARS[*]}"
  echo ""
  echo "Set the following in your .env or ~/.zshrc:"
  echo "  export PLANE_API_URL='https://plane.insightpulseai.com/api/v1'"
  echo "  export PLANE_API_KEY='your_api_key'"
  echo "  export PLANE_WORKSPACE_SLUG='fin-ops'"
  echo ""
  exit 1
fi

echo "✅ Environment variables set"
echo "  - PLANE_API_URL: ${PLANE_API_URL}"
echo "  - PLANE_WORKSPACE_SLUG: ${PLANE_WORKSPACE_SLUG}"
echo "  - PLANE_API_KEY: ${PLANE_API_KEY:0:15}..."
echo ""

# Check if Plane MCP server built
echo "2. Checking Plane MCP build..."
if [ ! -f "mcp/servers/plane/dist/index.js" ]; then
  echo "❌ Plane MCP not built. Run: cd mcp/servers/plane && npm run build"
  exit 1
fi
echo "✅ Plane MCP server built"
echo ""

# Check if MCP is registered
echo "3. Checking MCP server registration..."
if grep -q '"plane":' .claude/mcp-servers.json; then
  echo "✅ Plane MCP registered in .claude/mcp-servers.json"
else
  echo "❌ Plane MCP not registered. Add it to .claude/mcp-servers.json"
  exit 1
fi
echo ""

# Test Plane API connectivity (direct HTTP call)
echo "4. Testing Plane API connectivity..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
  -H "X-API-Key: ${PLANE_API_KEY}" \
  "${PLANE_API_URL}/workspaces/${PLANE_WORKSPACE_SLUG}/projects/" || echo "000")

if [ "$HTTP_CODE" = "200" ]; then
  echo "✅ Plane API accessible (HTTP 200)"
elif [ "$HTTP_CODE" = "401" ]; then
  echo "❌ Plane API authentication failed (HTTP 401) - check PLANE_API_KEY"
  exit 1
elif [ "$HTTP_CODE" = "404" ]; then
  echo "❌ Workspace not found (HTTP 404) - check PLANE_WORKSPACE_SLUG"
  exit 1
elif [ "$HTTP_CODE" = "000" ]; then
  echo "❌ Cannot connect to Plane API - check PLANE_API_URL and network"
  exit 1
else
  echo "⚠️  Unexpected HTTP code: $HTTP_CODE"
fi
echo ""

# Test listing projects (requires Plane API)
echo "5. Testing list_projects via API..."
PROJECTS_RESPONSE=$(curl -s \
  -H "X-API-Key: ${PLANE_API_KEY}" \
  "${PLANE_API_URL}/workspaces/${PLANE_WORKSPACE_SLUG}/projects/" || echo "ERROR")

if echo "$PROJECTS_RESPONSE" | jq . > /dev/null 2>&1; then
  PROJECT_COUNT=$(echo "$PROJECTS_RESPONSE" | jq 'length')
  echo "✅ Successfully fetched $PROJECT_COUNT projects"

  # Show first project if available
  if [ "$PROJECT_COUNT" -gt 0 ]; then
    FIRST_PROJECT=$(echo "$PROJECTS_RESPONSE" | jq -r '.[0].name')
    FIRST_PROJECT_ID=$(echo "$PROJECTS_RESPONSE" | jq -r '.[0].id')
    echo "  - Example: $FIRST_PROJECT (ID: ${FIRST_PROJECT_ID:0:8}...)"
  fi
else
  echo "⚠️  Could not parse projects response (may be API format change)"
fi
echo ""

# Check Supabase connection (for audit trail)
echo "6. Checking Supabase connection (audit trail)..."
if [ -z "${SUPABASE_URL:-}" ] || [ -z "${SUPABASE_SERVICE_ROLE_KEY:-}" ]; then
  echo "⚠️  Supabase not configured - audit trail will log to stderr"
  echo "   (This is OK for local dev, but required for production)"
else
  echo "✅ Supabase configured for audit trail"
fi
echo ""

echo "==================================="
echo "Verification Summary"
echo "==================================="
echo "✅ Plane MCP server ready for use"
echo ""
echo "Next steps:"
echo "  1. Restart Claude Code to load the MCP server"
echo "  2. Test with: 'List all Plane projects'"
echo "  3. Create an issue: 'Create a test issue in Plane project X'"
echo ""
echo "For marketplace GitHub integration:"
echo "  - Visit: https://plane.so/marketplace/github"
echo "  - Or build custom sync worker (see plan file)"
echo "==================================="
