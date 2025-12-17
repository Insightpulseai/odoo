#!/usr/bin/env python3
"""
Validate Finance PPM seed JSON against generated Odoo tasks.

Checks that all tasks defined in the seed have been generated in Odoo
and reports any discrepancies.

Exit codes:
    0 = PASS / WARN (all required tasks exist, possibly with warnings)
    2 = FAIL (missing tasks, duplicates, or critical errors)

Usage (inside container):
    odoo shell -d odoo_core -c /etc/odoo/odoo.conf <<EOF
    from odoo.addons.ipai_finance_ppm_closing.scripts.validate_seed_parity import main
    main(env)
    EOF

Or via command line:
    python validate_seed_parity.py --db odoo_core
"""
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

_logger = logging.getLogger(__name__)

# Configuration
SEED_FILE = Path(__file__).parent.parent / "seed" / "closing_v1_2_0.json"
REPORT_FILE = Path(__file__).parent / "seed_parity_report.json"
KEY_FMT = "{cycle_key}|{template_code}|{step_code}"


def load_seed() -> dict:
    """Load and parse seed JSON file."""
    if not SEED_FILE.exists():
        raise FileNotFoundError(f"Seed file not found: {SEED_FILE}")
    return json.loads(SEED_FILE.read_text())


def extract_expected_tasks(seed: dict) -> list[dict]:
    """
    Extract all expected tasks from seed JSON.

    Returns a list of task specifications with external keys.
    """
    tasks = []

    for cycle in seed.get("cycles", []):
        cycle_code = cycle.get("cycle_code")

        for phase in cycle.get("phases", []):
            for workstream in phase.get("workstreams", []):
                for template in workstream.get("task_templates", []):
                    tpl_code = template.get("task_template_code")

                    for step in template.get("steps", []):
                        step_code = step.get("step_code")

                        # Generate external key pattern (without date for comparison)
                        key_pattern = f"{cycle_code}|%|{tpl_code}|{step_code}"

                        tasks.append(
                            {
                                "cycle_code": cycle_code,
                                "template_code": tpl_code,
                                "template_name": template.get("name"),
                                "step_code": step_code,
                                "step_name": step.get("name"),
                                "default_assignee": step.get("default_assignee"),
                                "key_pattern": key_pattern,
                            }
                        )

    return tasks


def fetch_existing_tasks(env, cycle_code: str) -> dict:
    """
    Fetch existing generated tasks from Odoo.

    Returns:
        dict: {external_key: task_record}
    """
    Task = env["project.task"]
    Map = env["ipai.close.generated.map"]

    # Find all maps for this cycle
    maps = Map.search([("external_key", "like", f"{cycle_code}|%")])

    return {
        m.external_key: {
            "id": m.task_id.id,
            "name": m.task_id.name,
            "seed_hash": m.seed_hash,
        }
        for m in maps
    }


def compare_tasks(
    expected: list[dict],
    existing: dict,
    cycle_key: str,
) -> tuple[list, list, list, list]:
    """
    Compare expected tasks with existing tasks.

    Returns:
        missing: Tasks in seed but not in Odoo
        extra: Tasks in Odoo but not in seed
        drift: Tasks with name mismatches
        duplicates: Tasks with duplicate keys
    """
    # Build expected key patterns
    expected_patterns = set()
    expected_map = {}
    for task in expected:
        # For comparison, we check template and step code match
        pattern = f"{task['template_code']}|{task['step_code']}"
        expected_patterns.add(pattern)
        expected_map[pattern] = task

    # Extract template|step from existing keys
    existing_patterns = {}
    for key, data in existing.items():
        # Key format: cycle_key|template_code|step_code|date
        parts = key.split("|")
        if len(parts) >= 4:
            pattern = f"{parts[2]}|{parts[3]}"
            if pattern not in existing_patterns:
                existing_patterns[pattern] = []
            existing_patterns[pattern].append((key, data))

    # Find missing (in expected but not existing)
    missing = []
    for pattern in expected_patterns:
        if pattern not in existing_patterns:
            task = expected_map[pattern]
            missing.append(
                {
                    "template_code": task["template_code"],
                    "step_code": task["step_code"],
                    "template_name": task["template_name"],
                }
            )

    # Find extra (in existing but not expected)
    extra = []
    existing_pattern_set = set(existing_patterns.keys())
    for pattern in existing_pattern_set - expected_patterns:
        for key, data in existing_patterns[pattern]:
            extra.append(
                {
                    "external_key": key,
                    "task_name": data["name"],
                }
            )

    # Find duplicates
    duplicates = []
    for pattern, items in existing_patterns.items():
        if len(items) > 1:
            duplicates.append(
                {
                    "pattern": pattern,
                    "count": len(items),
                    "keys": [k for k, _ in items],
                }
            )

    # Find drift (name mismatches) - simplified for now
    drift = []

    return missing, extra, drift, duplicates


def generate_report(
    seed: dict,
    expected: list[dict],
    existing: dict,
    cycle_key: str,
) -> dict:
    """Generate comprehensive parity report."""
    missing, extra, drift, duplicates = compare_tasks(expected, existing, cycle_key)

    # Determine status
    if missing or duplicates:
        status = "FAIL"
    elif extra or drift:
        status = "WARN"
    else:
        status = "PASS"

    report = {
        "timestamp": datetime.utcnow().isoformat(),
        "seed_id": seed.get("seed_id"),
        "cycle_key": cycle_key,
        "status": status,
        "counts": {
            "expected": len(expected),
            "existing": len(existing),
            "missing": len(missing),
            "extra": len(extra),
            "drift": len(drift),
            "duplicates": len(duplicates),
        },
        "missing": missing,
        "extra": extra,
        "drift": drift,
        "duplicates": duplicates,
    }

    return report


def main(env, cycle_code: str = "MONTH_END_CLOSE", cycle_key: str = None):
    """
    Main validation entry point.

    Args:
        env: Odoo environment
        cycle_code: Cycle to validate (default: MONTH_END_CLOSE)
        cycle_key: Specific instance key (optional)
    """
    print("=" * 60)
    print("Finance PPM Seed Parity Validation")
    print("=" * 60)

    # Load seed
    try:
        seed = load_seed()
        print(f"Loaded seed: {seed.get('seed_id')}")
    except Exception as e:
        print(f"ERROR: Failed to load seed: {e}")
        sys.exit(2)

    # Extract expected tasks
    expected = extract_expected_tasks(seed)
    expected = [t for t in expected if t["cycle_code"] == cycle_code]
    print(f"Expected tasks for {cycle_code}: {len(expected)}")

    # Build default cycle_key if not provided
    if not cycle_key:
        from odoo import fields

        today = fields.Date.context_today(env.user)
        cycle_key = f"{cycle_code}|{today.strftime('%Y-%m')}"

    print(f"Checking cycle instance: {cycle_key}")

    # Fetch existing tasks
    existing = fetch_existing_tasks(env, cycle_code)
    print(f"Existing mapped tasks: {len(existing)}")

    # Generate report
    report = generate_report(seed, expected, existing, cycle_key)

    # Save report
    REPORT_FILE.write_text(json.dumps(report, indent=2))
    print(f"\nReport written to: {REPORT_FILE}")

    # Print summary
    print("\n" + "-" * 40)
    print(f"Status: {report['status']}")
    print(f"Expected: {report['counts']['expected']}")
    print(f"Existing: {report['counts']['existing']}")
    print(f"Missing:  {report['counts']['missing']}")
    print(f"Extra:    {report['counts']['extra']}")
    print(f"Drift:    {report['counts']['drift']}")
    print(f"Duplicates: {report['counts']['duplicates']}")
    print("-" * 40)

    if report["missing"]:
        print("\nMissing tasks:")
        for item in report["missing"][:10]:
            print(f"  - {item['template_code']}/{item['step_code']}")
        if len(report["missing"]) > 10:
            print(f"  ... and {len(report['missing']) - 10} more")

    if report["status"] == "FAIL":
        print("\nValidation FAILED - see report for details")
        return 2
    elif report["status"] == "WARN":
        print("\nValidation PASSED with warnings")
        return 0
    else:
        print("\nValidation PASSED")
        return 0


if __name__ == "__main__":
    # Standalone execution requires Odoo environment setup
    print("This script should be run within Odoo shell context.")
    print("Usage: odoo shell -d odoo_core < validate_seed_parity.py")
    sys.exit(1)
