#!/usr/bin/env bash
# odoo-test-runner-ops: Run tests for an Odoo module in disposable database
# Usage: run-tests.sh <module_name> [--tags <test-tags>]
set -euo pipefail

MODULE="${1:?Usage: run-tests.sh <module_name> [--tags <test-tags>]}"
TEST_DB="test_${MODULE}"
TAGS=""

if [ "${2:-}" = "--tags" ]; then
  TAGS="--test-tags ${3}"
fi

ODOO_BIN="${ODOO_BIN:-vendor/odoo/odoo-bin}"
PYTHON="${PYTHON:-$HOME/.pyenv/versions/odoo-19-dev/bin/python}"
ADDONS_PATH="${ADDONS_PATH:-vendor/odoo/addons,addons/ipai}"

# Ensure clean database
dropdb -h localhost -U tbwa --if-exists "${TEST_DB}" 2>/dev/null || true

echo "Running tests for ${MODULE} in database ${TEST_DB}"

# Create evidence directory
EVIDENCE_DIR="docs/evidence/$(date +%Y%m%d-%H%M)/${MODULE}"
mkdir -p "${EVIDENCE_DIR}"

# Run tests
"${PYTHON}" "${ODOO_BIN}" \
  --database="${TEST_DB}" \
  --db_host=localhost --db_port=5432 --db_user=tbwa --db_password=False \
  --addons-path="${ADDONS_PATH}" \
  --init="${MODULE}" \
  --test-enable \
  ${TAGS} \
  --stop-after-init \
  --log-level=test \
  2>&1 | tee "${EVIDENCE_DIR}/test.log"

EXIT_CODE=${PIPESTATUS[0]}

# Classify results
echo ""
echo "=== Test Results ==="
echo "Module: ${MODULE}"
echo "Database: ${TEST_DB}"
echo "Evidence: ${EVIDENCE_DIR}/test.log"

if [ "${EXIT_CODE}" -eq 0 ]; then
  echo "Classification: passes locally"
else
  echo "Classification: REQUIRES REVIEW — check ${EVIDENCE_DIR}/test.log"
  grep -E "(ERROR|FAIL)" "${EVIDENCE_DIR}/test.log" | tail -20
fi

# Cleanup
dropdb -h localhost -U tbwa --if-exists "${TEST_DB}" 2>/dev/null || true

exit "${EXIT_CODE}"
