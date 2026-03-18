#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# validate_parity_matrix.sh - Validate PARITY_MATRIX.yaml structure
# =============================================================================
# Checks:
#   1. File exists
#   2. Valid YAML syntax
#   3. Required fields present
#   4. Artifact paths resolve (for shipped features)
# =============================================================================

MATRIX_FILE="${MATRIX_FILE:-docs/parity/PARITY_MATRIX.yaml}"

echo "==> Validating PARITY_MATRIX.yaml"
echo "    File: $MATRIX_FILE"
echo ""

# Check file exists
if [ ! -f "$MATRIX_FILE" ]; then
  echo "ERROR: PARITY_MATRIX.yaml not found at $MATRIX_FILE"
  exit 1
fi
echo "[OK] File exists"

# Check YAML syntax (requires python3 + pyyaml)
if command -v python3 >/dev/null 2>&1; then
  if python3 -c "import yaml; yaml.safe_load(open('$MATRIX_FILE'))" 2>/dev/null; then
    echo "[OK] Valid YAML syntax"
  else
    echo "ERROR: Invalid YAML syntax in $MATRIX_FILE"
    python3 -c "import yaml; yaml.safe_load(open('$MATRIX_FILE'))" 2>&1 || true
    exit 1
  fi

  # Check required fields
  python3 - "$MATRIX_FILE" <<'PYTHON'
import sys
import yaml

with open(sys.argv[1]) as f:
    data = yaml.safe_load(f)

errors = []
warnings = []

# Check top-level required fields
required_fields = ['version', 'features']
for field in required_fields:
    if field not in data:
        errors.append(f"Missing required field: {field}")

# Check features structure
if 'features' in data:
    for i, feature in enumerate(data['features']):
        prefix = f"features[{i}]"

        # Required feature fields
        for field in ['id', 'name', 'phase', 'status', 'gates']:
            if field not in feature:
                errors.append(f"{prefix}: missing required field '{field}'")

        # Validate status
        valid_statuses = ['shipped', 'in_progress', 'planned', 'blocked']
        if 'status' in feature and feature['status'] not in valid_statuses:
            errors.append(f"{prefix}: invalid status '{feature['status']}' (valid: {valid_statuses})")

        # Validate gates structure
        if 'gates' in feature and not isinstance(feature['gates'], dict):
            errors.append(f"{prefix}: gates must be a dict")

# Report results
if errors:
    print("[FAIL] Validation errors:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)

if warnings:
    print("[WARN] Validation warnings:")
    for w in warnings:
        print(f"  - {w}")

print("[OK] Structure validation passed")

# Count features by status
if 'features' in data:
    counts = {}
    for f in data['features']:
        status = f.get('status', 'unknown')
        counts[status] = counts.get(status, 0) + 1
    print("")
    print("Feature counts by status:")
    for status, count in sorted(counts.items()):
        print(f"  - {status}: {count}")
PYTHON

else
  echo "[WARN] python3 not found, skipping YAML validation"
fi

# Check artifact paths for shipped features
echo ""
echo "Checking artifact paths for shipped features..."

# Extract shipped features and their module paths
if command -v python3 >/dev/null 2>&1; then
  python3 - "$MATRIX_FILE" <<'PYTHON'
import sys
import os
import yaml

with open(sys.argv[1]) as f:
    data = yaml.safe_load(f)

errors = []

for feature in data.get('features', []):
    if feature.get('status') != 'shipped':
        continue

    fid = feature.get('id', 'unknown')
    artifacts = feature.get('artifacts', {})

    # Check module path
    if 'module' in artifacts:
        module_path = artifacts['module']
        manifest_path = os.path.join(module_path, '__manifest__.py')
        if not os.path.isdir(module_path):
            errors.append(f"{fid}: module path not found: {module_path}")
        elif not os.path.isfile(manifest_path):
            errors.append(f"{fid}: __manifest__.py not found in {module_path}")
        else:
            print(f"[OK] {fid}: {module_path}")

    # Check script paths
    for script in artifacts.get('scripts', []):
        if not os.path.isfile(script):
            errors.append(f"{fid}: script not found: {script}")
        else:
            print(f"[OK] {fid}: {script}")

    # Check workflow paths
    for workflow in artifacts.get('workflows', []):
        if not os.path.isfile(workflow):
            errors.append(f"{fid}: workflow not found: {workflow}")
        else:
            print(f"[OK] {fid}: {workflow}")

if errors:
    print("")
    print("[FAIL] Artifact path errors:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)

print("")
print("[OK] All artifact paths verified")
PYTHON
else
  echo "[WARN] python3 not found, skipping artifact path check"
fi

echo ""
echo "OK: PARITY_MATRIX.yaml validation passed"
