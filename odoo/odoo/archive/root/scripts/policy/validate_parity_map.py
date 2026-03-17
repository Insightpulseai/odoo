#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parity Map Validator
====================
Validates spec/<slug>/parity_map.yaml against the parity constitution:
  - Every capability has required fields
  - delta/bridge entries have a decision record + evidence pointer
  - decision records exist on disk
  - No unknown target_parity values

Usage:
    python3 scripts/policy/validate_parity_map.py
    python3 scripts/policy/validate_parity_map.py --spec-dir spec/finance-ppm
    python3 scripts/policy/validate_parity_map.py --self-test

Exit codes:
    0 = all checks passed
    1 = validation failure
"""
import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

ALLOWED_TARGETS = {"ce", "oca", "delta", "bridge"}
ALLOWED_STATUSES = {"verified", "unverified", "planned"}

REQUIRED_FIELDS = {"capability_id", "capability_name", "target_parity", "status"}
ESCALATION_REQUIRED_FIELDS = {"decision", "evidence"}


def load_yaml_simple(path):
    """Load YAML using PyYAML if available, otherwise basic parser."""
    try:
        import yaml
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f), None
    except ImportError:
        pass

    # Fallback: minimal YAML-like parser for our specific schema
    # This handles the flat list-of-dicts structure in parity_map.yaml
    return None, "PyYAML not installed. Install with: pip install pyyaml"


def validate_parity_map(spec_dir):
    """Validate parity_map.yaml in the given spec directory."""
    errors = []
    parity_map_path = os.path.join(spec_dir, "parity_map.yaml")
    decisions_dir = os.path.join(spec_dir, "decisions")

    # Check file exists
    if not os.path.exists(parity_map_path):
        return [f"parity_map.yaml not found: {parity_map_path}"]

    # Load YAML
    data, err = load_yaml_simple(parity_map_path)
    if err:
        return [f"Cannot load parity_map.yaml: {err}"]

    if not data or "capabilities" not in data:
        return ["parity_map.yaml missing 'capabilities' key"]

    capabilities = data["capabilities"]
    if not isinstance(capabilities, list):
        return ["'capabilities' must be a list"]

    seen_ids = set()

    for i, cap in enumerate(capabilities):
        if not isinstance(cap, dict):
            errors.append(f"Capability #{i}: must be a dict")
            continue

        cap_id = cap.get("capability_id", f"<unnamed-{i}>")

        # Check required fields
        for field in REQUIRED_FIELDS:
            if field not in cap or not cap[field]:
                errors.append(f"{cap_id}: missing required field '{field}'")

        # Check unique capability_id
        if cap_id in seen_ids:
            errors.append(f"{cap_id}: duplicate capability_id")
        seen_ids.add(cap_id)

        # Check target_parity enum
        target = cap.get("target_parity", "")
        if target and target not in ALLOWED_TARGETS:
            errors.append(
                f"{cap_id}: invalid target_parity '{target}' "
                f"(allowed: {sorted(ALLOWED_TARGETS)})"
            )

        # Check status enum
        status = cap.get("status", "")
        if status and status not in ALLOWED_STATUSES:
            errors.append(
                f"{cap_id}: invalid status '{status}' "
                f"(allowed: {sorted(ALLOWED_STATUSES)})"
            )

        # Escalation check: delta/bridge must have decision + evidence
        if target in ("delta", "bridge"):
            for field in ESCALATION_REQUIRED_FIELDS:
                if field not in cap or not cap[field]:
                    errors.append(
                        f"{cap_id}: target_parity='{target}' requires '{field}' field"
                    )

            # Verify decision record exists on disk
            evidence = cap.get("evidence", "")
            if evidence:
                evidence_path = os.path.join(REPO_ROOT, evidence)
                if not os.path.exists(evidence_path):
                    errors.append(
                        f"{cap_id}: evidence file not found: {evidence}"
                    )

    # Check decisions directory exists if any delta/bridge capabilities
    has_escalated = any(
        c.get("target_parity") in ("delta", "bridge")
        for c in capabilities if isinstance(c, dict)
    )
    if has_escalated and not os.path.isdir(decisions_dir):
        errors.append(f"decisions/ directory not found: {decisions_dir}")

    return errors


def run_self_test():
    """Built-in self-test."""
    print("Running self-test...")
    test_errors = 0

    # Test 1: Valid spec dir should pass
    finance_ppm = os.path.join(REPO_ROOT, "spec", "finance-ppm")
    if os.path.exists(os.path.join(finance_ppm, "parity_map.yaml")):
        errs = validate_parity_map(finance_ppm)
        if errs:
            print(f"  FAIL: Finance PPM parity map has errors: {errs}")
            test_errors += 1
        else:
            print("  PASS: Finance PPM parity map is valid")
    else:
        print("  SKIP: Finance PPM parity map not found")

    # Test 2: Missing file should fail
    errs = validate_parity_map("/tmp/nonexistent-spec-dir")
    if errs:
        print("  PASS: Missing parity map correctly rejected")
    else:
        print("  FAIL: Missing parity map was not caught")
        test_errors += 1

    print()
    if test_errors == 0:
        print("Self-test: ALL TESTS PASSED")
        return 0
    else:
        print(f"Self-test: {test_errors} TESTS FAILED")
        return 1


def find_all_spec_dirs():
    """Find all spec directories containing parity_map.yaml."""
    spec_root = os.path.join(REPO_ROOT, "spec")
    dirs = []
    if os.path.isdir(spec_root):
        for entry in os.listdir(spec_root):
            spec_dir = os.path.join(spec_root, entry)
            if os.path.isdir(spec_dir) and os.path.exists(
                os.path.join(spec_dir, "parity_map.yaml")
            ):
                dirs.append(spec_dir)
    return dirs


def main():
    if "--self-test" in sys.argv:
        sys.exit(run_self_test())

    # Determine spec directories to validate
    spec_dir_arg = None
    for i, arg in enumerate(sys.argv):
        if arg == "--spec-dir" and i + 1 < len(sys.argv):
            spec_dir_arg = sys.argv[i + 1]

    if spec_dir_arg:
        spec_dirs = [spec_dir_arg]
    else:
        spec_dirs = find_all_spec_dirs()

    if not spec_dirs:
        print("No spec directories with parity_map.yaml found")
        sys.exit(0)

    print("=" * 60)
    print("Parity Map Validator")
    print("=" * 60)

    all_errors = []
    for spec_dir in spec_dirs:
        slug = os.path.basename(spec_dir)
        print(f"\nValidating: spec/{slug}/parity_map.yaml")
        errors = validate_parity_map(spec_dir)
        if errors:
            for e in errors:
                sys.stderr.write(f"  ERROR: {e}\n")
            all_errors.extend(errors)
        else:
            print("  PASSED")

    print()
    if all_errors:
        print(f"VALIDATION FAILED: {len(all_errors)} error(s)")
        sys.exit(1)
    else:
        print("VALIDATION PASSED: All parity maps valid")
        sys.exit(0)


if __name__ == "__main__":
    main()
