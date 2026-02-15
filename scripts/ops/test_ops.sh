#!/bin/bash
# Smoke test for OdooOps control plane RPC exposure
# Tests that public.list_projects(), list_environments(), list_runs() are accessible via PostgREST

set -e

# Load environment
source .env 2>/dev/null || true

# Verify credentials
if [[ -z "$SUPABASE_SERVICE_ROLE_KEY" ]]; then
    echo "❌ SUPABASE_SERVICE_ROLE_KEY not set"
    exit 1
fi

BASE_URL="https://spdtwktxdalcfigzeqrz.supabase.co"

echo "🧪 OdooOps Control Plane RPC Smoke Test"
echo "========================================"
echo ""

# Test 1: list_projects RPC
echo "1. Testing /rest/v1/rpc/list_projects..."
result=$(curl -s -X POST \
    "$BASE_URL/rest/v1/rpc/list_projects" \
    -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
    -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
    -H "Content-Type: application/json")

if echo "$result" | grep -q "PGRST202"; then
    echo "   ❌ FAIL: public.list_projects() not found in schema cache"
    echo "   Response: $result"
    echo ""
    echo "   This means the migration has NOT been applied or RPC is not exposed."
    echo "   Expected: [] or rows"
    echo "   Got: PGRST202 error"
    exit 1
elif echo "$result" | grep -q "error"; then
    echo "   ⚠️  ERROR: $result"
    exit 1
else
    echo "   ✅ PASS: RPC callable (returned: ${result:0:100}...)"
fi

# Test 2: list_environments RPC
echo ""
echo "2. Testing /rest/v1/rpc/list_environments..."
result=$(curl -s -X POST \
    "$BASE_URL/rest/v1/rpc/list_environments" \
    -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
    -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
    -H "Content-Type: application/json" \
    -d '{}')

if echo "$result" | grep -q "PGRST202"; then
    echo "   ❌ FAIL: public.list_environments() not found"
    exit 1
elif echo "$result" | grep -q "error"; then
    echo "   ⚠️  ERROR: $result"
    exit 1
else
    echo "   ✅ PASS: RPC callable (returned: ${result:0:100}...)"
fi

# Test 3: list_runs RPC
echo ""
echo "3. Testing /rest/v1/rpc/list_runs..."
result=$(curl -s -X POST \
    "$BASE_URL/rest/v1/rpc/list_runs" \
    -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
    -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
    -H "Content-Type: application/json" \
    -d '{}')

if echo "$result" | grep -q "PGRST202"; then
    echo "   ❌ FAIL: public.list_runs() not found"
    exit 1
elif echo "$result" | grep -q "error"; then
    echo "   ⚠️  ERROR: $result"
    exit 1
else
    echo "   ✅ PASS: RPC callable (returned: ${result:0:100}...)"
fi

echo ""
echo "========================================"
echo "✅ All RPC endpoints accessible and functional"
echo ""
echo "Summary:"
echo "  - public.list_projects() ✅"
echo "  - public.list_environments() ✅"
echo "  - public.list_runs() ✅"
echo ""
echo "OdooOps control plane RPC layer is ready for odooops-console integration."
