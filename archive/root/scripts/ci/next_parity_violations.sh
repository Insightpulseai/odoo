#!/usr/bin/env bash
set -euo pipefail

BASELINE="scripts/ci/baselines/parity_boundaries_baseline.json"
N="${1:-10}"

if [ ! -f "$BASELINE" ]; then
  echo "❌ FAIL: missing $BASELINE"
  exit 1
fi

python3 - "$N" <<'PY'
import json, sys

n = int(sys.argv[1])
path = "scripts/ci/baselines/parity_boundaries_baseline.json"

with open(path) as f:
    data = json.load(f)

# Extract violations from baseline
violations = data.get("violations", [])

print(f"Next {min(n, len(violations))} baseline violations to address:\n")
for i, violation in enumerate(violations[:n], 1):
    print(f"{i}. {violation}")

print(f"\nTotal violations: {len(violations)}")
print(f"Target date: {data.get('target_date', '2026-08-20')}")
print(f"Migration policy: {data.get('migration_policy', 'incremental')}")
PY
