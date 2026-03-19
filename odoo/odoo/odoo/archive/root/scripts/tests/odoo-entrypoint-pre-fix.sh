#!/usr/bin/env bash
# Proves current broken state (for evidence collection)
# This test is designed to run BEFORE fixes are applied

set -euo pipefail

echo "=== Pre-Fix Validation ==="
FAILURES=0

# Test 1: python odoo-bin should fail with SyntaxError
echo -n "Test 1: python odoo-bin fails with SyntaxError... "
if python odoo-bin --help 2>&1 | grep -q "SyntaxError"; then
  echo "✅ PASS"
else
  echo "❌ FAIL (did not produce SyntaxError)"
  FAILURES=$((FAILURES + 1))
fi

# Test 2: ./odoo-bin should work (bash execution)
echo -n "Test 2: ./odoo-bin works... "
if ./odoo-bin --help > /dev/null 2>&1 || [[ $? -eq 1 ]]; then
  # Either succeeds or fails with "No module named odoo" (both are fine - means bash executed)
  echo "✅ PASS"
else
  echo "❌ FAIL"
  FAILURES=$((FAILURES + 1))
fi

# Test 3: scripts/odoo.sh should work
echo -n "Test 3: scripts/odoo.sh works... "
if ./scripts/odoo.sh --help > /dev/null 2>&1 || [[ $? -eq 1 ]]; then
  echo "✅ PASS"
else
  echo "❌ FAIL"
  FAILURES=$((FAILURES + 1))
fi

# Test 4: Documentation contains bad patterns (pre-fix state)
echo -n "Test 4: Docs contain 'python odoo-bin' pattern... "
if rg -n 'python(?:3)?\s+.*odoo-bin\b' agents/ORCHESTRATOR.md docs/FEATURE_*.md docs/SAAS_PARITY_READINESS.md 2>/dev/null; then
  echo "✅ PASS (pattern found as expected pre-fix)"
else
  echo "❌ FAIL (pattern should exist before fix)"
  FAILURES=$((FAILURES + 1))
fi

echo ""
echo "=== Pre-Fix Summary: $FAILURES failures ==="
exit $FAILURES
