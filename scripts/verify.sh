#!/usr/bin/env bash
# =============================================================================
# Verification Script
# Runs all verification checks before commit.
#
# Usage:
#   ./scripts/verify.sh           # Full verification
#   ./scripts/verify.sh --quick   # Quick syntax checks only
# =============================================================================
set -euo pipefail

QUICK="${1:-}"

echo "== Running Verification =="
echo ""

# Ensure scripts are executable
chmod +x scripts/*.sh 2>/dev/null || true
chmod +x scripts/ci/*.sh 2>/dev/null || true

# Step 1: Repo health
echo "[1/5] Repo health check..."
./scripts/repo_health.sh || true
echo ""

# Step 2: Spec validation
echo "[2/5] Spec kit validation..."
if [ -f "scripts/spec_validate.sh" ]; then
  ./scripts/spec_validate.sh || true
else
  echo "  No spec_validate.sh found, skipping"
fi
echo ""

# Step 3: Python syntax (addons)
echo "[3/5] Python syntax check..."
fail=0
while IFS= read -r pyfile; do
  python3 -m py_compile "$pyfile" 2>/dev/null || {
    echo "  ERROR: $pyfile"
    fail=1
  }
done < <(find addons -name "*.py" -type f 2>/dev/null || true)
if [ "$fail" -eq 0 ]; then
  echo "  All Python files OK"
fi
echo ""

if [ "$QUICK" == "--quick" ]; then
  echo "== Quick verification complete =="
  exit 0
fi

# Step 4: Formatting checks (if tools available)
echo "[4/5] Formatting checks..."
if command -v black >/dev/null 2>&1; then
  black --check addons/ packages/ apps/ 2>/dev/null || {
    echo "  WARN: Some files need formatting (run: black addons/ packages/ apps/)"
  }
else
  echo "  black not installed, skipping"
fi

if command -v isort >/dev/null 2>&1; then
  isort --check addons/ packages/ apps/ 2>/dev/null || {
    echo "  WARN: Some imports need sorting (run: isort addons/ packages/ apps/)"
  }
else
  echo "  isort not installed, skipping"
fi
echo ""

# Step 5: Local CI (if available)
echo "[5/5] Local CI..."
if [ -f "scripts/ci_local.sh" ]; then
  ./scripts/ci_local.sh --quick 2>/dev/null || {
    echo "  WARN: Local CI returned non-zero"
  }
else
  echo "  No ci_local.sh found, skipping"
fi
echo ""

echo "== Verification complete =="
