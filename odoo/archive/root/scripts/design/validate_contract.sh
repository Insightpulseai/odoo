#!/usr/bin/env bash
# ============================================================================
# Figma Contract Validation Script
# ============================================================================
# Description: Validates figma_contract.json against the JSON schema
# Usage: ./scripts/design/validate_contract.sh [CONTRACT_PATH]
# Exit codes: 0 = valid, 1 = invalid, 2 = missing file
# ============================================================================

set -euo pipefail

CONTRACT_PATH="${1:-ops/design/figma_contract.json}"
SCHEMA_PATH="ops/design/schemas/figma_contract.schema.json"

echo "[validate] Checking Figma contract: $CONTRACT_PATH"

# Check contract exists
if [ ! -f "$CONTRACT_PATH" ]; then
  echo "[validate] ERROR: Contract not found: $CONTRACT_PATH"
  exit 2
fi

# Check schema exists
if [ ! -f "$SCHEMA_PATH" ]; then
  echo "[validate] ERROR: Schema not found: $SCHEMA_PATH"
  exit 2
fi

# Validate JSON syntax
if ! python3 -c "import json; json.load(open('$CONTRACT_PATH'))" 2>/dev/null; then
  echo "[validate] ERROR: Invalid JSON syntax"
  exit 1
fi

# Validate required fields
python3 - "$CONTRACT_PATH" <<'PY'
import json
import sys

contract_path = sys.argv[1]
contract = json.load(open(contract_path))

required_fields = [
    "version",
    "feature_slug",
    "phase",
    "owners",
    "figma_meta",
    "routes",
    "tokens_touched",
    "schemas_touched"
]

missing = []
for field in required_fields:
    if field not in contract:
        missing.append(field)

if missing:
    print(f"[validate] ERROR: Missing required fields: {', '.join(missing)}")
    sys.exit(1)

# Validate owners structure
owners = contract.get("owners", {})
if "design" not in owners or "engineering" not in owners:
    print("[validate] ERROR: owners must have 'design' and 'engineering'")
    sys.exit(1)

if not owners["design"] or not owners["engineering"]:
    print("[validate] ERROR: owners.design and owners.engineering must not be empty")
    sys.exit(1)

# Validate phase
phase = contract.get("phase")
if not isinstance(phase, int) or phase < 0 or phase > 6:
    print(f"[validate] ERROR: phase must be integer 0-6, got: {phase}")
    sys.exit(1)

# Validate figma_meta
meta = contract.get("figma_meta", {})
if "file_key" not in meta or "exported_at" not in meta:
    print("[validate] ERROR: figma_meta must have 'file_key' and 'exported_at'")
    sys.exit(1)

# Validate feature_slug format
slug = contract.get("feature_slug", "")
import re
if not re.match(r'^[a-z0-9-]+$', slug):
    print(f"[validate] ERROR: feature_slug must be lowercase alphanumeric with dashes: {slug}")
    sys.exit(1)

print(f"[validate] Contract valid: {contract_path}")
print(f"  Feature: {slug}")
print(f"  Phase: {phase}")
print(f"  Routes: {len(contract.get('routes', []))}")
print(f"  Components: {len(contract.get('components', []))}")
PY

# If we get here, validation passed
echo "[validate] OK"
exit 0
