#!/usr/bin/env bash
# Validates fix effectiveness
# This test runs AFTER fixes are applied

set -euo pipefail

echo "=== Post-Fix Validation ==="
FAILURES=0

# Test 1: Linter catches doc violations
echo -n "Test 1: Linter passes (no violations)... "
if ./scripts/lint_odoo_entrypoint.sh > /dev/null 2>&1; then
  echo "✅ PASS"
else
  echo "❌ FAIL (linter found violations)"
  FAILURES=$((FAILURES + 1))
fi

# Test 2: All correct patterns still work
echo -n "Test 2: ./odoo-bin still works... "
if ./odoo-bin --help > /dev/null 2>&1 || [[ $? -eq 1 ]]; then
  echo "✅ PASS"
else
  echo "❌ FAIL"
  FAILURES=$((FAILURES + 1))
fi

echo -n "Test 3: ./scripts/odoo.sh still works... "
if ./scripts/odoo.sh --help > /dev/null 2>&1 || [[ $? -eq 1 ]]; then
  echo "✅ PASS"
else
  echo "❌ FAIL"
  FAILURES=$((FAILURES + 1))
fi

# Test 4: Documentation examples are correct (excluding educational guide)
echo -n "Test 4: Docs are clean (no bad patterns)... "
if rg -n 'python(?:3)?\s+.*odoo-bin\b' docs/ agents/ --glob='!**/evidence/**' --glob='!**/archive/**' --glob='!docs/ODOO_EXECUTION.md' 2>/dev/null; then
  echo "❌ FAIL (documentation still contains bad patterns)"
  FAILURES=$((FAILURES + 1))
else
  echo "✅ PASS"
fi

# Test 5: ODOO_EXECUTION.md exists
echo -n "Test 5: docs/ODOO_EXECUTION.md exists... "
if [[ -f "docs/ODOO_EXECUTION.md" ]]; then
  echo "✅ PASS"
else
  echo "❌ FAIL (documentation not created)"
  FAILURES=$((FAILURES + 1))
fi

# Test 6: README references execution guide
echo -n "Test 6: README.md references execution guide... "
if grep -q "ODOO_EXECUTION.md" README.md; then
  echo "✅ PASS"
else
  echo "❌ FAIL (README not updated)"
  FAILURES=$((FAILURES + 1))
fi

# Test 7: odoo-bin has helpful header
echo -n "Test 7: odoo-bin has helpful error documentation... "
if grep -q "IMPORTANT: This is a BASH SCRIPT" odoo-bin; then
  echo "✅ PASS"
else
  echo "❌ FAIL (guard not enhanced)"
  FAILURES=$((FAILURES + 1))
fi

echo ""
echo "=== Post-Fix Summary: $FAILURES failures ==="
exit $FAILURES
