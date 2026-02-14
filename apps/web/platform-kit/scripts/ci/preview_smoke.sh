#!/usr/bin/env bash
#
# Preview environment smoke tests
# Usage: ./scripts/ci/preview_smoke.sh
#
# Required environment variables:
#   SUPABASE_URL_PREVIEW
#   SUPABASE_SERVICE_ROLE_KEY_PREVIEW
#
set -euo pipefail

: "${SUPABASE_URL_PREVIEW:?missing SUPABASE_URL_PREVIEW}"
: "${SUPABASE_SERVICE_ROLE_KEY_PREVIEW:?missing SUPABASE_SERVICE_ROLE_KEY_PREVIEW}"

echo "================================"
echo "Preview Environment Smoke Tests"
echo "================================"

PASSED=0
FAILED=0

# Test helper
test_endpoint() {
  local name=$1
  local endpoint=$2

  echo -n "Testing $name... "
  if curl -sSf "${SUPABASE_URL_PREVIEW}${endpoint}" \
    -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY_PREVIEW" \
    -o /dev/null --max-time 30; then
    echo "PASSED"
    ((PASSED++))
  else
    echo "FAILED"
    ((FAILED++))
  fi
}

# Test REST API root
echo ""
echo "== REST API =="
test_endpoint "REST root" "/rest/v1/"

# Test Edge Functions
echo ""
echo "== Edge Functions =="
test_endpoint "ops-executor" "/functions/v1/ops-executor?action=status"
test_endpoint "health-check" "/functions/v1/health-check?action=database"
test_endpoint "plane-sync" "/functions/v1/plane-sync"

# Summary
echo ""
echo "================================"
echo "Results: $PASSED passed, $FAILED failed"
echo "================================"

if [ $FAILED -gt 0 ]; then
  echo "Some tests failed!"
  exit 1
fi

echo "All smoke tests passed!"
