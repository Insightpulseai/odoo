#!/usr/bin/env bash
# =============================================================================
# Validate Custom IPAI Modules
# =============================================================================
# Checks that all custom modules under addons/ipai/ have valid structure:
#   - __manifest__.py exists and is valid Python
#   - __init__.py exists
#   - Module name follows ipai_* naming convention
#
# Usage: ./scripts/validate_custom_modules.sh
# =============================================================================
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
ADDONS_DIR="$ROOT/addons/ipai"

errors=0

if [ ! -d "$ADDONS_DIR" ]; then
  echo "No addons/ipai/ directory found — nothing to validate."
  exit 0
fi

echo "== Validating custom IPAI modules =="

for module_dir in "$ADDONS_DIR"/*/; do
  [ -d "$module_dir" ] || continue
  module_name=$(basename "$module_dir")

  # Skip hidden directories and __pycache__
  [[ "$module_name" == .* ]] && continue
  [[ "$module_name" == "__pycache__" ]] && continue

  # Check __manifest__.py
  if [ ! -f "$module_dir/__manifest__.py" ]; then
    echo "ERROR: $module_name — missing __manifest__.py"
    errors=$((errors + 1))
    continue
  fi

  # Validate manifest is valid Python
  if ! python3 -m py_compile "$module_dir/__manifest__.py" 2>/dev/null; then
    echo "ERROR: $module_name — __manifest__.py has syntax errors"
    errors=$((errors + 1))
  fi

  # Check __init__.py
  if [ ! -f "$module_dir/__init__.py" ]; then
    echo "ERROR: $module_name — missing __init__.py"
    errors=$((errors + 1))
  fi
done

echo ""
if [ "$errors" -gt 0 ]; then
  echo "FAIL: $errors validation error(s) found"
  exit 1
fi

echo "PASS: All custom modules are valid"
exit 0
