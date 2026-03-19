#!/usr/bin/env python3
"""
Roadmap Crosswalk Contract Gate

Validates ssot/roadmap/roadmap_crosswalk.yaml against
ssot/roadmap/product_roadmap.yaml:
  1. Every product_quarters reference matching YYYY-Qn:E-XXX-NN
     must point to an existing epic ID in product_roadmap.yaml.
  2. [NEEDS_CLARIFICATION: epic id] placeholders are allowed.
  3. All capability entries have required fields.

Exit 0 = PASS, exit 1 = validation error, exit 2 = file/parse error.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is required. pip install pyyaml")
    sys.exit(2)

CROSSWALK_PATH = Path("ssot/roadmap/roadmap_crosswalk.yaml")
ROADMAP_PATH = Path("ssot/roadmap/product_roadmap.yaml")

EPIC_REF_RE = re.compile(r"^\d{4}-Q[1-4]:E-[A-Z]+-\d+$")


def main() -> int:
    for p in (CROSSWALK_PATH, ROADMAP_PATH):
        if not p.exists():
            print(f"FAIL: {p} not found")
            return 2

    try:
        crosswalk = yaml.safe_load(CROSSWALK_PATH.read_text(encoding="utf-8"))
        roadmap = yaml.safe_load(ROADMAP_PATH.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        print(f"FAIL: YAML parse error: {e}")
        return 2

    # Build set of known epic IDs from product_roadmap.yaml
    known_epics: set[str] = set()
    for quarter in roadmap.get("quarters", []):
        qid = quarter.get("id", "")
        for epic in quarter.get("epics", []):
            eid = epic.get("id", "")
            if qid and eid:
                known_epics.add(f"{qid}:{eid}")

    capabilities = crosswalk.get("capabilities", [])
    if not isinstance(capabilities, list) or not capabilities:
        print("FAIL: No capabilities found in crosswalk")
        return 2

    errors: list[str] = []

    for i, cap in enumerate(capabilities):
        cid = cap.get("capability_id", f"<entry {i}>")

        # Required fields
        if not cap.get("capability_id"):
            errors.append(f"Entry {i}: missing capability_id")
        if not cap.get("tracks"):
            errors.append(f"{cid}: missing tracks")
            continue

        tracks = cap["tracks"]
        pq_refs = tracks.get("product_quarters", [])

        for ref in pq_refs:
            ref_str = str(ref)
            # Allow placeholders
            if ref_str.startswith("[NEEDS_CLARIFICATION"):
                continue
            # Validate epic reference format and existence
            if EPIC_REF_RE.match(ref_str):
                if ref_str not in known_epics:
                    errors.append(f"{cid}: product_quarters ref '{ref_str}' not found in product_roadmap.yaml")
            else:
                errors.append(f"{cid}: product_quarters ref '{ref_str}' does not match expected format YYYY-Qn:E-XXX-NN")

    if errors:
        print(f"FAIL: {len(errors)} validation error(s):")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"Roadmap crosswalk gate PASS ({len(capabilities)} capabilities, {len(known_epics)} known epics)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
