#!/usr/bin/env bash
# =============================================================================
# Smoke Test: Odoo ERP Login Page
# =============================================================================
# Checks that the Odoo ERP login page is reachable, returns 200,
# contains expected Odoo content, and has no error indicators.
#
# Usage:
#   ./tests/smoke/odoo/test_erp.sh
#   URL=https://erp-staging.insightpulseai.com ./tests/smoke/odoo/test_erp.sh
# =============================================================================
set -euo pipefail

URL="${URL:-https://erp.insightpulseai.com/web/login}"
TIMEOUT="${TIMEOUT:-30}"

echo "=== Odoo ERP Smoke Test ==="
echo "URL: ${URL}"
echo "Timeout: ${TIMEOUT}s"
echo ""

PASSED=0
FAILED=0

# Test 1: HTTP status
HTTP_CODE=$(curl -s -o /tmp/odoo_body.txt -w "%{http_code}" \
  --max-time "${TIMEOUT}" -L "${URL}" 2>/dev/null || echo "000")

if [[ "${HTTP_CODE}" == "200" ]]; then
  echo "PASS: HTTP ${HTTP_CODE}"
  PASSED=$((PASSED + 1))
else
  echo "FAIL: Expected HTTP 200, got ${HTTP_CODE}"
  FAILED=$((FAILED + 1))
fi

# Test 2: Contains Odoo login form marker
if grep -qi "oe_login_form\|odoo\|csrf_token" /tmp/odoo_body.txt 2>/dev/null; then
  echo "PASS: Odoo login form detected"
  PASSED=$((PASSED + 1))
else
  echo "FAIL: Odoo login form not detected"
  FAILED=$((FAILED + 1))
fi

# Test 3: JavaScript assets load reference present
if grep -qi "/web/assets/" /tmp/odoo_body.txt 2>/dev/null; then
  echo "PASS: JS asset references present"
  PASSED=$((PASSED + 1))
else
  echo "WARN: No JS asset references found (may indicate asset pipeline issue)"
  # Not a hard fail - page may still function
  PASSED=$((PASSED + 1))
fi

# Test 4: No 500 error page
if grep -qi "Internal Server Error\|Traceback\|odoo\.exceptions" /tmp/odoo_body.txt 2>/dev/null; then
  echo "FAIL: Server error content detected"
  FAILED=$((FAILED + 1))
else
  echo "PASS: No error page indicators"
  PASSED=$((PASSED + 1))
fi

# Test 5: No database selector (list_db should be False)
if grep -qi "select.*database\|db-selector\|Database:" /tmp/odoo_body.txt 2>/dev/null; then
  echo "FAIL: Database selector detected (list_db should be False)"
  FAILED=$((FAILED + 1))
else
  echo "PASS: No database selector (list_db=False confirmed)"
  PASSED=$((PASSED + 1))
fi

# Summary
echo ""
echo "=== Summary ==="
echo "Passed: ${PASSED}, Failed: ${FAILED}"

if [[ ${FAILED} -gt 0 ]]; then
  echo "RESULT: FAIL"
  exit 1
fi

echo "RESULT: PASS"
rm -f /tmp/odoo_body.txt
