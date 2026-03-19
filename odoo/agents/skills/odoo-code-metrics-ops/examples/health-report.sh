#!/usr/bin/env bash
# Example: Generate code health report for IPAI modules
set -euo pipefail

echo "=== IPAI Code Health Report ==="
echo "Date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo ""

TOTAL_MODULES=0
MODULES_WITH_TESTS=0
TOTAL_PY=0
TOTAL_TEST_PY=0

for module_dir in addons/ipai/ipai_*/; do
  MODULE=$(basename "${module_dir}")
  TOTAL_MODULES=$((TOTAL_MODULES + 1))

  # Count test files
  TEST_FILES=$(find "${module_dir}" -path "*/tests/test_*.py" -type f 2>/dev/null | wc -l | tr -d ' ')
  if [ "${TEST_FILES}" -gt 0 ]; then
    MODULES_WITH_TESTS=$((MODULES_WITH_TESTS + 1))
  fi

  # Count dependencies
  if [ -f "${module_dir}/__manifest__.py" ]; then
    DEP_COUNT=$(grep -c "'[a-z_]*'" "${module_dir}/__manifest__.py" 2>/dev/null || echo 0)
  fi
done

echo "Total IPAI modules: ${TOTAL_MODULES}"
echo "Modules with tests: ${MODULES_WITH_TESTS}"
echo "Test coverage rate: $(( MODULES_WITH_TESTS * 100 / TOTAL_MODULES ))%"
