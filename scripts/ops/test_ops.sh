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

# Helper function: test RPC with retry for schema cache lag
test_rpc_with_retry() {
    local endpoint="$1"
    local data="${2:-{}}"
    local result

    result=$(curl -s -X POST \
        "$BASE_URL/rest/v1/rpc/$endpoint" \
        -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
        -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
        -H "Content-Type: application/json" \
        -d "$data")

    # If PGRST202, retry once after 2s (schema cache lag)
    if echo "$result" | grep -q "PGRST202"; then
        echo "   ⚠️  PGRST202 on first attempt, retrying after 2s (schema cache lag)..."
        sleep 2
        result=$(curl -s -X POST \
            "$BASE_URL/rest/v1/rpc/$endpoint" \
            -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
            -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
            -H "Content-Type: application/json" \
            -d "$data")
    fi

    echo "$result"
}

echo "🧪 OdooOps Control Plane RPC Smoke Test"
echo "========================================"
echo ""

# Test 1: list_projects RPC
echo "1. Testing /rest/v1/rpc/list_projects..."
result=$(test_rpc_with_retry "list_projects")

if echo "$result" | grep -q "PGRST202"; then
    echo "   ❌ FAIL: public.list_projects() not found in schema cache (after retry)"
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
result=$(test_rpc_with_retry "list_environments")

if echo "$result" | grep -q "PGRST202"; then
    echo "   ❌ FAIL: public.list_environments() not found (after retry)"
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
result=$(test_rpc_with_retry "list_runs")

if echo "$result" | grep -q "PGRST202"; then
    echo "   ❌ FAIL: public.list_runs() not found (after retry)"
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
