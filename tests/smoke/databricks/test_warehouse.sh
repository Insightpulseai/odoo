#!/usr/bin/env bash
# =============================================================================
# Smoke Test: Databricks SQL Warehouse
# =============================================================================
# Checks SQL Warehouse health by executing a trivial query via the
# Databricks REST API. Requires DATABRICKS_HOST and DATABRICKS_TOKEN.
#
# Usage:
#   DATABRICKS_HOST=https://adb-xxx.azuredatabricks.net \
#   DATABRICKS_TOKEN=dapi... \
#   ./tests/smoke/databricks/test_warehouse.sh
# =============================================================================
set -euo pipefail

DATABRICKS_HOST="${DATABRICKS_HOST:?DATABRICKS_HOST is required}"
WAREHOUSE_ID="${WAREHOUSE_ID:-e7d89eabce4c330c}"
TIMEOUT="${TIMEOUT:-30}"

echo "=== Databricks SQL Warehouse Smoke Test ==="
echo "Host: ${DATABRICKS_HOST}"
echo "Warehouse: ${WAREHOUSE_ID}"
echo ""

PASSED=0
FAILED=0

# Check if we have auth
if [[ -z "${DATABRICKS_TOKEN:-}" ]]; then
  # Try databricks CLI auth (profiles or AAD)
  if ! command -v databricks &>/dev/null; then
    echo "FAIL: Neither DATABRICKS_TOKEN nor databricks CLI available"
    exit 1
  fi
  USE_CLI=true
else
  USE_CLI=false
fi

# Test 1: Execute health query
PAYLOAD='{"warehouse_id":"'"${WAREHOUSE_ID}"'","statement":"SELECT 1 AS health","wait_timeout":"10s"}'

if [[ "${USE_CLI}" == "true" ]]; then
  RESULT=$(databricks api post /api/2.0/sql/statements --json "${PAYLOAD}" 2>&1)
else
  RESULT=$(curl -s --max-time "${TIMEOUT}" \
    -H "Authorization: Bearer ${DATABRICKS_TOKEN}" \
    -H "Content-Type: application/json" \
    -d "${PAYLOAD}" \
    "${DATABRICKS_HOST}/api/2.0/sql/statements" 2>&1)
fi

STATE=$(echo "${RESULT}" | python3 -c 'import sys,json; print(json.load(sys.stdin).get("status",{}).get("state","FAIL"))' 2>/dev/null || echo "PARSE_ERROR")

if [[ "${STATE}" == "SUCCEEDED" || "${STATE}" == "CLOSED" ]]; then
  echo "PASS: Warehouse health query returned ${STATE}"
  PASSED=$((PASSED + 1))
else
  echo "FAIL: Warehouse health query returned ${STATE}"
  echo "Response: ${RESULT}" | head -5
  FAILED=$((FAILED + 1))
fi

# Test 2: Check warehouse state via GET
if [[ "${USE_CLI}" == "true" ]]; then
  WH_INFO=$(databricks api get "/api/2.0/sql/warehouses/${WAREHOUSE_ID}" 2>&1 || echo '{}')
else
  WH_INFO=$(curl -s --max-time "${TIMEOUT}" \
    -H "Authorization: Bearer ${DATABRICKS_TOKEN}" \
    "${DATABRICKS_HOST}/api/2.0/sql/warehouses/${WAREHOUSE_ID}" 2>&1 || echo '{}')
fi

WH_STATE=$(echo "${WH_INFO}" | python3 -c 'import sys,json; print(json.load(sys.stdin).get("state","UNKNOWN"))' 2>/dev/null || echo "PARSE_ERROR")

if [[ "${WH_STATE}" == "RUNNING" || "${WH_STATE}" == "STARTING" || "${WH_STATE}" == "STOPPED" ]]; then
  echo "PASS: Warehouse state is ${WH_STATE}"
  PASSED=$((PASSED + 1))
else
  echo "FAIL: Warehouse state is ${WH_STATE}"
  FAILED=$((FAILED + 1))
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
