#!/usr/bin/env python3
import sys
import yaml
import re
from pathlib import Path

MATRIX_FILE = Path("spec/ipai_enterprise_bridge/ee-replacement-matrix.yaml")

def validate():
    if not MATRIX_FILE.exists():
        print(f"❌ Matrix file invalid: {MATRIX_FILE}")
        sys.exit(1)

    try:
        data = yaml.safe_load(MATRIX_FILE.read_text())
    except Exception as e:
        print(f"❌ Invalid YAML: {e}")
        sys.exit(1)

    areas = data.get("areas", [])
    errors = []

    for idx, item in enumerate(areas):
        area = item.get("ee_area", f"Index {idx}")

        # Check required fields
        if "ce_18_coverage" not in item:
            errors.append(f"[{area}] Missing ce_18_coverage list")

        if "oca_18_candidates" not in item:
            errors.append(f"[{area}] Missing oca_18_candidates list")

        # Check repo/module format for OCA
        for oca in item.get("oca_18_candidates", []):
            if "partial" in oca or "deprecated" in oca:
                continue # Skip annotation checks
            if not re.match(r"^OCA/[a-z0-9_-]+/[a-z0-9_]+", oca):
                errors.append(f"[{area}] Invalid OCA format '{oca}'. Expected 'OCA/repo/module'")

        # Check bridge logic
        if item.get("bridge_required") is True:
            if not item.get("bridge_scope"):
                errors.append(f"[{area}] bridge_required=true but bridge_scope is empty")
        elif item.get("bridge_required") is False:
            pass # No scope needed
        else:
            errors.append(f"[{area}] bridge_required must be boolean")

    if errors:
        print("❌ Matrix Validation Failed:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    print(f"✅ Matrix valid. Covered {len(areas)} EE areas.")

if __name__ == "__main__":
    validate()
