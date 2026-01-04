#!/usr/bin/env python3
"""Compare module audit results against a baseline to detect regressions."""

import argparse
import json
import sys
from pathlib import Path


STATUS_RANK = {"PASS": 0, "WARN": 1, "FAIL": 2}


def get_status(mod_data: dict) -> str:
    """Compute status from module data."""
    # If status field exists, use it directly
    if "status" in mod_data:
        return mod_data["status"]
    # Otherwise compute from issues/warnings
    if mod_data.get("issues"):
        return "FAIL"
    if mod_data.get("warnings"):
        return "WARN"
    return "PASS"


def load_audit(path: Path) -> dict:
    """Load audit JSON and return module dict."""
    with open(path) as f:
        data = json.load(f)
    modules = data.get("modules", {})
    # Handle both dict and list formats
    if isinstance(modules, dict):
        return modules
    return {m["module"]: m for m in modules}


def compare_audits(baseline: dict, current: dict, strict: bool = False) -> tuple:
    """Compare baseline vs current and return (regressions, improvements, new_modules)."""
    regressions = []
    improvements = []
    new_modules = []

    for mod_name, mod_data in current.items():
        curr_status = get_status(mod_data)

        if mod_name not in baseline:
            new_modules.append((mod_name, curr_status))
            continue

        base_status = get_status(baseline[mod_name])

        if STATUS_RANK.get(curr_status, 99) > STATUS_RANK.get(base_status, 99):
            regressions.append((mod_name, base_status, curr_status))
        elif STATUS_RANK.get(curr_status, 99) < STATUS_RANK.get(base_status, 99):
            improvements.append((mod_name, base_status, curr_status))

    return regressions, improvements, new_modules


def main():
    parser = argparse.ArgumentParser(description="Compare audit results")
    parser.add_argument("--baseline", required=True, help="Baseline JSON file")
    parser.add_argument("--current", required=True, help="Current JSON file")
    parser.add_argument("--strict", action="store_true", help="Fail on new modules with warnings")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    baseline_path = Path(args.baseline)
    current_path = Path(args.current)

    if not baseline_path.exists():
        print(f"Baseline not found: {baseline_path}", file=sys.stderr)
        sys.exit(2)

    if not current_path.exists():
        print(f"Current audit not found: {current_path}", file=sys.stderr)
        sys.exit(2)

    baseline = load_audit(baseline_path)
    current = load_audit(current_path)

    regressions, improvements, new_modules = compare_audits(baseline, current, args.strict)

    if args.json:
        result = {
            "baseline_count": len(baseline),
            "current_count": len(current),
            "regressions": [{"module": m, "from": f, "to": t} for m, f, t in regressions],
            "improvements": [{"module": m, "from": f, "to": t} for m, f, t in improvements],
            "new_modules": [{"module": m, "status": s} for m, s in new_modules],
            "passed": len(regressions) == 0,
        }
        print(json.dumps(result, indent=2))
    else:
        print(f"Modules checked: {len(current)}")
        print(f"New modules: {len(new_modules)}")
        print(f"Improvements: {len(improvements)}")
        print(f"Regressions: {len(regressions)}")
        print("")

        if improvements:
            print("✅ IMPROVEMENTS:")
            for mod, old, new in improvements:
                print(f"   {mod}: {old} → {new}")
            print("")

        if new_modules:
            print("📦 NEW MODULES:")
            for mod, status in new_modules:
                print(f"   {mod}: {status}")
            print("")

        if regressions:
            print("❌ REGRESSIONS DETECTED:")
            for mod, old, new in regressions:
                print(f"   {mod}: {old} → {new}")
            print("")
            print("DRIFT GATE FAILED: Module quality has regressed.")
            sys.exit(1)

        if args.strict and new_modules:
            warn_new = [m for m, s in new_modules if s != "PASS"]
            if warn_new:
                print("❌ STRICT MODE: New modules with warnings:")
                for mod in warn_new:
                    print(f"   {mod}")
                sys.exit(1)

        print("✅ DRIFT GATE PASSED: No regressions detected.")

    sys.exit(1 if regressions else 0)


if __name__ == "__main__":
    main()
