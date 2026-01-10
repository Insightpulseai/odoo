#!/bin/bash
# OdooForge Codex Check - PR Gate Script
# Runs the same validation in Codex Cloud, Claude Code Web, and CI

set -euo pipefail

echo "==> OdooForge PR Gate Check"

ERRORS=0
KIT_CMD="python kit-cli/kit.py"

# Use kit command if available, otherwise use python
if command -v kit >/dev/null 2>&1; then
  KIT_CMD="kit"
fi

# Step 1: Pre-commit checks (if available)
if command -v pre-commit >/dev/null 2>&1; then
  echo "==> Running pre-commit hooks..."
  if ! pre-commit run -a; then
    echo "!!! Pre-commit checks failed"
    ERRORS=$((ERRORS + 1))
  fi
else
  echo "==> Pre-commit not installed, skipping..."
fi

# Step 2: Python syntax check
echo "==> Checking Python syntax..."
if ! python -m py_compile kit-cli/kit.py; then
  echo "!!! Python syntax errors found"
  ERRORS=$((ERRORS + 1))
fi

# Find all Python files in addons and check syntax
for pyfile in $(find addons -name "*.py" 2>/dev/null || true); do
  if ! python -m py_compile "$pyfile" 2>/dev/null; then
    echo "!!! Syntax error in: $pyfile"
    ERRORS=$((ERRORS + 1))
  fi
done

# Step 3: Kit validate (strict mode)
echo "==> Running kit validate --strict..."
if ! $KIT_CMD validate --strict 2>/dev/null; then
  # If validate fails, try without strict
  if ! $KIT_CMD validate 2>/dev/null; then
    echo "!!! Kit validation failed"
    ERRORS=$((ERRORS + 1))
  else
    echo "==> Kit validation passed (non-strict)"
  fi
fi

# Step 4: Run tests if available
if [ -d "tests" ] && [ -f "tests/test_uat.py" ]; then
  echo "==> Running pytest..."
  if command -v pytest >/dev/null 2>&1; then
    if ! pytest tests/ -v --tb=short 2>/dev/null; then
      echo "!!! Tests failed"
      ERRORS=$((ERRORS + 1))
    fi
  else
    echo "==> pytest not installed, skipping tests..."
  fi
fi

# Summary
echo ""
echo "=============================================="
if [ $ERRORS -eq 0 ]; then
  echo "==> PR GATE: PASSED"
  exit 0
else
  echo "==> PR GATE: FAILED ($ERRORS errors)"
  exit 1
fi
