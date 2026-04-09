#!/usr/bin/env bash
# Example: Batch test all IPAI modules
set -euo pipefail

ADDONS_DIR="addons/ipai"
RESULTS_FILE="/tmp/ipai-test-results-$(date +%Y%m%d).txt"
PASS_COUNT=0
FAIL_COUNT=0

echo "=== Batch testing IPAI modules ==="
echo "Results: ${RESULTS_FILE}"

for module_dir in "${ADDONS_DIR}"/ipai_*/; do
  MODULE=$(basename "${module_dir}")
  TEST_DB="test_${MODULE}"

  echo "--- Testing ${MODULE} ---"
  dropdb -h localhost -U tbwa --if-exists "${TEST_DB}" 2>/dev/null || true

  if ~/.pyenv/versions/odoo-18-dev/bin/python vendor/odoo/odoo-bin \
    --database="${TEST_DB}" \
    --db_host=localhost --db_port=5432 --db_user=tbwa --db_password=False \
    --addons-path=vendor/odoo/addons,addons/ipai \
    --init="${MODULE}" \
    --test-enable \
    --stop-after-init \
    --log-level=warn 2>/dev/null; then
    echo "${MODULE}: PASS" >> "${RESULTS_FILE}"
    PASS_COUNT=$((PASS_COUNT + 1))
  else
    echo "${MODULE}: FAIL" >> "${RESULTS_FILE}"
    FAIL_COUNT=$((FAIL_COUNT + 1))
  fi

  dropdb -h localhost -U tbwa --if-exists "${TEST_DB}" 2>/dev/null || true
done

echo ""
echo "=== Summary ==="
echo "Passed: ${PASS_COUNT}"
echo "Failed: ${FAIL_COUNT}"
echo "Details: ${RESULTS_FILE}"
