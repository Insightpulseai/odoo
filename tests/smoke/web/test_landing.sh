#!/usr/bin/env bash
# =============================================================================
# Smoke Test: Web Landing Page
# =============================================================================
# Checks that the public landing page is up, returns 200, and contains
# expected content. Exit 0 on pass, exit 1 on fail.
#
# Usage:
#   ./tests/smoke/web/test_landing.sh
#   URL=https://staging.insightpulseai.com ./tests/smoke/web/test_landing.sh
# =============================================================================
set -euo pipefail

URL="${URL:-https://www.insightpulseai.com}"
TIMEOUT="${TIMEOUT:-30}"
EXPECTED_CONTENT="${EXPECTED_CONTENT:-InsightPulse}"

echo "=== Web Landing Smoke Test ==="
echo "URL: ${URL}"
echo "Timeout: ${TIMEOUT}s"
echo ""

PASSED=0
FAILED=0

# Test 1: HTTP status
HTTP_CODE=$(curl -s -o /tmp/landing_body.txt -w "%{http_code}" \
  --max-time "${TIMEOUT}" -L "${URL}" 2>/dev/null || echo "000")

if [[ "${HTTP_CODE}" == "200" ]]; then
  echo "PASS: HTTP ${HTTP_CODE}"
  PASSED=$((PASSED + 1))
else
  echo "FAIL: Expected HTTP 200, got ${HTTP_CODE}"
  FAILED=$((FAILED + 1))
fi

# Test 2: Content contains expected string
if grep -qi "${EXPECTED_CONTENT}" /tmp/landing_body.txt 2>/dev/null; then
  echo "PASS: Content contains '${EXPECTED_CONTENT}'"
  PASSED=$((PASSED + 1))
else
  echo "FAIL: Content does not contain '${EXPECTED_CONTENT}'"
  FAILED=$((FAILED + 1))
fi

# Test 3: Body is non-trivial (> 1KB)
BODY_SIZE=$(wc -c < /tmp/landing_body.txt 2>/dev/null || echo "0")
if [[ ${BODY_SIZE} -gt 1024 ]]; then
  echo "PASS: Body size ${BODY_SIZE} bytes (> 1KB)"
  PASSED=$((PASSED + 1))
else
  echo "FAIL: Body size ${BODY_SIZE} bytes (expected > 1KB)"
  FAILED=$((FAILED + 1))
fi

# Test 4: No error page indicators
if grep -qi "Internal Server Error\|502 Bad Gateway\|503 Service Unavailable" /tmp/landing_body.txt 2>/dev/null; then
  echo "FAIL: Error page content detected"
  FAILED=$((FAILED + 1))
else
  echo "PASS: No error page indicators"
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
rm -f /tmp/landing_body.txt
