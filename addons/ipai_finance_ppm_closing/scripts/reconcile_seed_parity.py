#!/usr/bin/env python3
"""
Reconcile Finance PPM seed parity.

Fixes discrepancies between seed JSON and generated Odoo tasks:
- Creates missing tasks
- Renames drifted tasks
- Flags extra tasks as obsolete
- Resolves duplicates

Usage (inside container):
    odoo shell -d odoo_core -c /etc/odoo/odoo.conf <<EOF
    from odoo.addons.ipai_finance_ppm_closing.scripts.reconcile_seed_parity import main
    main(env)
    EOF
"""
import json
import logging
import sys
from pathlib import Path

_logger = logging.getLogger(__name__)

# Configuration
REPORT_FILE = Path(__file__).parent / "seed_parity_report.json"
SEED_FILE = Path(__file__).parent.parent / "seed" / "closing_v1_2_0.json"


def load_report() -> dict:
    """Load the validation report."""
    if not REPORT_FILE.exists():
        raise FileNotFoundError(
            f"Report file not found: {REPORT_FILE}\n"
            "Run validate_seed_parity.py first."
        )
    return json.loads(REPORT_FILE.read_text())


def load_seed() -> dict:
    """Load seed JSON."""
    if not SEED_FILE.exists():
        raise FileNotFoundError(f"Seed file not found: {SEED_FILE}")
    return json.loads(SEED_FILE.read_text())


def reconcile(env, report: dict, seed: dict, dry_run: bool = False):
    """
    Perform reconciliation based on validation report.

    Args:
        env: Odoo environment
        report: Validation report from validate_seed_parity.py
        seed: Seed JSON
        dry_run: If True, report changes without persisting
    """
    Task = env["project.task"].sudo()
    Map = env["ipai.close.generated.map"].sudo()
    Generator = env["ipai.close.generator"]

    cycle_key = report.get("cycle_key")
    changes = {
        "created": 0,
        "renamed": 0,
        "obsoleted": 0,
        "deduped": 0,
    }

    print(f"\nReconciling cycle: {cycle_key}")
    print(f"Dry run: {dry_run}")
    print("-" * 40)

    # 1. Handle missing tasks - trigger full generation
    if report.get("missing"):
        print(f"\nCreating {len(report['missing'])} missing tasks...")

        if not dry_run:
            # Re-run generator to create missing tasks
            cycle_code = cycle_key.split("|")[0] if "|" in cycle_key else cycle_key
            result = Generator.run(seed, cycle_code, cycle_key, dry_run=False)
            changes["created"] = result.get("counts", {}).get("created", 0)
            print(f"  Created: {changes['created']} tasks")
        else:
            print("  [DRY RUN] Would trigger generator")

    # 2. Handle drifted tasks (name mismatches)
    if report.get("drift"):
        print(f"\nFixing {len(report['drift'])} drifted tasks...")

        for item in report["drift"]:
            external_key = item.get("external_key")
            expected_name = item.get("expected_name")

            if not dry_run:
                mapping = Map.search([("external_key", "=", external_key)], limit=1)
                if mapping and mapping.task_id:
                    mapping.task_id.write({"name": expected_name})
                    changes["renamed"] += 1
                    print(f"  Renamed: {external_key}")
            else:
                print(f"  [DRY RUN] Would rename: {external_key}")

    # 3. Handle extra tasks (mark as obsolete)
    if report.get("extra"):
        print(f"\nMarking {len(report['extra'])} extra tasks as obsolete...")

        for item in report["extra"]:
            external_key = item.get("external_key")

            if not dry_run:
                mapping = Map.search([("external_key", "=", external_key)], limit=1)
                if mapping and mapping.task_id:
                    mapping.task_id.write({"x_obsolete": True})
                    changes["obsoleted"] += 1
                    print(f"  Obsoleted: {external_key}")
            else:
                print(f"  [DRY RUN] Would obsolete: {external_key}")

    # 4. Handle duplicates (keep first, obsolete others)
    if report.get("duplicates"):
        print(f"\nResolving {len(report['duplicates'])} duplicate patterns...")

        for dup in report["duplicates"]:
            keys = dup.get("keys", [])

            if len(keys) > 1:
                # Keep first, obsolete rest
                for key in keys[1:]:
                    if not dry_run:
                        mapping = Map.search([("external_key", "=", key)], limit=1)
                        if mapping and mapping.task_id:
                            mapping.task_id.write({"x_obsolete": True})
                            changes["deduped"] += 1
                            print(f"  Deduped (obsoleted): {key}")
                    else:
                        print(f"  [DRY RUN] Would obsolete duplicate: {key}")

    return changes


def main(env, dry_run: bool = False):
    """
    Main reconciliation entry point.

    Args:
        env: Odoo environment
        dry_run: If True, report changes without persisting
    """
    print("=" * 60)
    print("Finance PPM Seed Parity Reconciliation")
    print("=" * 60)

    # Load report
    try:
        report = load_report()
        print(f"Loaded report from: {REPORT_FILE}")
        print(f"Report status: {report.get('status')}")
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        sys.exit(2)

    # Check if reconciliation is needed
    if report.get("status") == "PASS":
        print("\nNo reconciliation needed - validation already passed.")
        return 0

    # Load seed
    try:
        seed = load_seed()
    except Exception as e:
        print(f"ERROR: Failed to load seed: {e}")
        sys.exit(2)

    # Perform reconciliation
    changes = reconcile(env, report, seed, dry_run=dry_run)

    # Print summary
    print("\n" + "-" * 40)
    print("Reconciliation Summary:")
    print(f"  Created:   {changes['created']}")
    print(f"  Renamed:   {changes['renamed']}")
    print(f"  Obsoleted: {changes['obsoleted']}")
    print(f"  Deduped:   {changes['deduped']}")
    print("-" * 40)

    if not dry_run:
        # Commit changes
        env.cr.commit()
        print("\nChanges committed to database.")

        # Re-run validation
        print("\nRe-running validation...")
        from odoo.addons.ipai_finance_ppm_closing.scripts.validate_seed_parity import main as validate
        return validate(env, report.get("cycle_key", "").split("|")[0])
    else:
        print("\n[DRY RUN] No changes were persisted.")
        return 0


if __name__ == "__main__":
    print("This script should be run within Odoo shell context.")
    print("Usage: odoo shell -d odoo_core < reconcile_seed_parity.py")
    sys.exit(1)
