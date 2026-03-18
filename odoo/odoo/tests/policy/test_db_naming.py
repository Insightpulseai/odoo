#!/usr/bin/env python3
"""Test that database naming policy is respected in SSOT artifacts."""
import os
import re
import sys

import yaml

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FORBIDDEN_DB_NAMES = ["odoo_prod"]


def test_no_forbidden_db_names_in_ssot():
    """Fail when any SSOT artifact references forbidden database names."""
    violations = []
    ssot_dir = os.path.join(REPO_ROOT, "ssot")

    for root, _dirs, files in os.walk(ssot_dir):
        for fname in files:
            if not fname.endswith((".yaml", ".yml", ".json")):
                continue
            fpath = os.path.join(root, fname)
            rel = os.path.relpath(fpath, REPO_ROOT)
            try:
                with open(fpath) as f:
                    content = f.read()
                for forbidden in FORBIDDEN_DB_NAMES:
                    for i, line in enumerate(content.splitlines(), 1):
                        if forbidden in line and "forbidden" not in line.lower() and "violation" not in line.lower():
                            violations.append(f"{rel}:{i} references '{forbidden}'")
            except Exception:
                pass

    if violations:
        print("FAIL: Forbidden database names found in SSOT artifacts:")
        for v in violations:
            print(f"  - {v}")
        return 1
    print("PASS: No forbidden database names in SSOT artifacts")
    return 0


def test_topology_policy_consistency():
    """Verify database topology policy file is internally consistent."""
    policy_path = os.path.join(REPO_ROOT, "ssot", "azure",
                               "odoo__azure__database_topology__v1.policy.yaml")
    if not os.path.exists(policy_path):
        print("SKIP: Database topology policy not found")
        return 0

    with open(policy_path) as f:
        policy = yaml.safe_load(f)

    errors = []
    canonical = policy.get("databases", {}).get("canonical", {})
    forbidden = policy.get("databases", {}).get("forbidden", [])

    if canonical.get("prod") != "odoo":
        errors.append("canonical prod DB must be 'odoo'")
    if canonical.get("dev") != "odoo_dev":
        errors.append("canonical dev DB must be 'odoo_dev'")
    if canonical.get("staging") != "odoo_staging":
        errors.append("canonical staging DB must be 'odoo_staging'")
    if "odoo_prod" not in forbidden:
        errors.append("'odoo_prod' must be in forbidden list")

    if errors:
        print("FAIL: Topology policy inconsistencies:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("PASS: Database topology policy is consistent")
    return 0


if __name__ == "__main__":
    rc = 0
    rc |= test_no_forbidden_db_names_in_ssot()
    rc |= test_topology_policy_consistency()
    sys.exit(rc)
