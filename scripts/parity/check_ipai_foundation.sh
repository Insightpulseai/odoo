#!/usr/bin/env bash
set -euo pipefail

# Validates the ipai_foundation module structure - Phase 1 vertical slice marker.
# This module proves the delivery pipeline works end-to-end.

MODULE="addons/ipai/ipai_foundation"

echo "=== Checking ipai_foundation module structure ==="

# Required files
test -f "$MODULE/__manifest__.py" || { echo "ERROR: Missing __manifest__.py"; exit 1; }
test -f "$MODULE/__init__.py" || { echo "ERROR: Missing __init__.py"; exit 1; }
test -f "$MODULE/models/__init__.py" || { echo "ERROR: Missing models/__init__.py"; exit 1; }
test -f "$MODULE/models/ipai_workspace.py" || { echo "ERROR: Missing models/ipai_workspace.py"; exit 1; }
test -f "$MODULE/security/ir.model.access.csv" || { echo "ERROR: Missing security/ir.model.access.csv"; exit 1; }

# Validate manifest is valid Python
python3 -c "
import ast
with open('$MODULE/__manifest__.py') as f:
    ast.literal_eval(f.read())
print('Manifest: valid Python dict')
"

# Validate model file syntax
python3 -m py_compile "$MODULE/models/ipai_workspace.py"
echo "Model: valid Python syntax"

# Validate security CSV has content
if [ $(wc -l < "$MODULE/security/ir.model.access.csv") -lt 2 ]; then
  echo "ERROR: security/ir.model.access.csv must have header + at least one rule"
  exit 1
fi
echo "Security: CSV has content"

echo ""
echo "OK: ipai_foundation module structure validated."
echo "Phase 1 vertical slice ready for Odoo install testing."
