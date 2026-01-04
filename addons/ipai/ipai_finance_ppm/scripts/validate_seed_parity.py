#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Seed JSON ⇄ Odoo Project 30 Task Parity Validator

Validates that project 30 tasks match seed JSON expectations for Q4 2025.

Usage:
    python3 validate_seed_parity.py [--dry-run] [--output report.json]

Exit codes:
    0: PASS (perfect parity)
    1: WARN (unresolvable assignees or minor issues)
    2: FAIL (missing templates, duplicate keys, or generator errors)
"""

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

# Odoo imports (assumes running via odoo shell or with PYTHONPATH set)
try:
    import odoo
    from odoo import SUPERUSER_ID, api
except ImportError:
    print(
        "ERROR: Cannot import Odoo. Run via: docker exec odoo-ce python3 /path/to/script.py"
    )
    sys.exit(2)


class SeedParityValidator:
    """Validates seed JSON vs Odoo project 30 tasks for Q4 2025"""

    # Q4 2025 periods for month-end closing
    Q4_2025_PERIODS = [
        ("2025-10-01", "2025-10-31", "MONTH_END_CLOSE|2025-10"),
        ("2025-11-01", "2025-11-30", "MONTH_END_CLOSE|2025-11"),
        ("2025-12-01", "2025-12-31", "MONTH_END_CLOSE|2025-12"),
    ]

    # Tax filing periods for Q4 2025
    TAX_FILING_PERIODS = [
        # Monthly (1601-C, 0619-E): Oct, Nov, Dec
        ("2025-10-01", "2025-10-31", "TAX_FILING_MONTHLY|2025-10"),
        ("2025-11-01", "2025-11-30", "TAX_FILING_MONTHLY|2025-11"),
        ("2025-12-01", "2025-12-31", "TAX_FILING_MONTHLY|2025-12"),
        # Quarterly (2550Q, 1601-EQ, 1601-FQ): Q4 2025
        ("2025-10-01", "2025-12-31", "TAX_FILING_QUARTERLY|2025-Q4"),
    ]

    PROJECT_ID = 30

    def __init__(self, env):
        self.env = env
        self.seed_base = Path(__file__).parent.parent / "seed"
        self.expected_keys = set()
        self.actual_keys = {}  # {external_key: task_id}
        self.warnings = []
        self.errors = []

    def load_seed_json(self, filename):
        """Load seed JSON file"""
        seed_path = self.seed_base / filename
        if not seed_path.exists():
            self.errors.append(f"Seed file not found: {seed_path}")
            return None

        with open(seed_path, "r") as f:
            return json.load(f)

    def expand_seed_to_external_keys(self, seed_data, periods):
        """
        Expand seed JSON to expected external keys for given periods

        Returns: set of external_key strings
        """
        keys = set()

        for cycle in seed_data.get("cycles", []):
            cycle_code = cycle.get("cycle_code")

            for phase in cycle.get("phases", []):
                phase_code = phase.get("phase_code")

                for workstream in phase.get("workstreams", []):
                    workstream_code = workstream.get("workstream_code")

                    for category in workstream.get("categories", []):
                        category_code = category.get("category_code")

                        for task_template in category.get("task_templates", []):
                            template_code = task_template.get("template_code")

                            for step in task_template.get("steps", []):
                                step_code = step.get("step_code")

                                # Generate external key for each period
                                for period_start, period_end, cycle_key in periods:
                                    # Match cycle type
                                    if cycle_key.split("|")[0] == cycle_code:
                                        external_key = f"{cycle_key}|{phase_code}|{workstream_code}|{category_code}|{template_code}|{step_code}"
                                        keys.add(external_key)

        return keys

    def query_actual_tasks(self):
        """Query Odoo for all project 30 tasks with external keys"""
        # Use raw SQL to bypass ORM field registration requirement
        query = """
            SELECT id, x_external_key
            FROM project_task
            WHERE project_id = %s AND x_external_key IS NOT NULL AND x_external_key != ''
        """
        self.env.cr.execute(query, (self.PROJECT_ID,))

        actual = {}
        for task_id, external_key in self.env.cr.fetchall():
            actual[external_key] = task_id

        return actual

    def validate_parity(self):
        """
        Main validation logic

        Returns:
            dict: {
                'status': 'PASS|WARN|FAIL',
                'expected_count': int,
                'actual_count': int,
                'missing_count': int,
                'extra_count': int,
                'duplicate_count': int,
                'malformed_count': int,
                'missing_keys': [str],
                'extra_keys': [str],
                'duplicate_keys': [str],
                'malformed_keys': [str],
                'warnings': [str],
                'errors': [str]
            }
        """
        print("=" * 80)
        print("SEED JSON ⇄ PROJECT 30 TASK PARITY VALIDATION")
        print("=" * 80)

        # Step 1: Load closing seed
        print("\n[1/6] Loading closing_v1_2_0.json...")
        closing_seed = self.load_seed_json("closing_v1_2_0.json")
        if not closing_seed:
            return self._fail_report("Cannot load closing seed")

        # Step 2: Load tax filing seed
        print("[2/6] Loading tax_filing_v1_2_0.json...")
        tax_seed = self.load_seed_json("tax_filing_v1_2_0.json")
        if not tax_seed:
            return self._fail_report("Cannot load tax filing seed")

        # Step 3: Expand seeds to expected external keys
        print("[3/6] Expanding seeds for Q4 2025 (Oct, Nov, Dec)...")
        closing_keys = self.expand_seed_to_external_keys(
            closing_seed, self.Q4_2025_PERIODS
        )
        tax_keys = self.expand_seed_to_external_keys(tax_seed, self.TAX_FILING_PERIODS)
        self.expected_keys = closing_keys | tax_keys

        print(f"  → Expected closing tasks: {len(closing_keys)}")
        print(f"  → Expected tax filing tasks: {len(tax_keys)}")
        print(f"  → Total expected: {len(self.expected_keys)}")

        # Step 4: Query actual tasks from Odoo
        print("[4/6] Querying project 30 tasks...")
        self.actual_keys = self.query_actual_tasks()
        print(f"  → Actual tasks with external_key: {len(self.actual_keys)}")

        # Step 5: Compare
        print("[5/6] Comparing expected vs actual...")
        missing_keys = self.expected_keys - set(self.actual_keys.keys())
        extra_keys = set(self.actual_keys.keys()) - self.expected_keys

        # Check for duplicates
        duplicate_keys = self._check_duplicates()

        # Check for malformed keys
        malformed_keys = self._check_malformed_keys()

        # Step 6: Generate report
        print("[6/6] Generating report...")

        status = "PASS"
        if self.errors or missing_keys or extra_keys or duplicate_keys:
            status = "FAIL"
        elif self.warnings or malformed_keys:
            status = "WARN"

        report = {
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
            "expected_count": len(self.expected_keys),
            "actual_count": len(self.actual_keys),
            "missing_count": len(missing_keys),
            "extra_count": len(extra_keys),
            "duplicate_count": len(duplicate_keys),
            "malformed_count": len(malformed_keys),
            "missing_keys": sorted(missing_keys),
            "extra_keys": sorted(extra_keys),
            "duplicate_keys": sorted(duplicate_keys),
            "malformed_keys": sorted(malformed_keys),
            "warnings": self.warnings,
            "errors": self.errors,
        }

        self._print_summary(report)
        return report

    def _check_duplicates(self):
        """Check for duplicate external_key in database"""
        query = """
            SELECT x_external_key, COUNT(*) as count
            FROM project_task
            WHERE project_id = %s AND x_external_key IS NOT NULL
            GROUP BY x_external_key
            HAVING COUNT(*) > 1
        """
        self.env.cr.execute(query, (self.PROJECT_ID,))
        duplicates = [row[0] for row in self.env.cr.fetchall()]

        if duplicates:
            self.errors.append(f"Found {len(duplicates)} duplicate external keys")

        return duplicates

    def _check_malformed_keys(self):
        """Check for malformed external keys (not 7 components)

        Expected format: CYCLE_TYPE|PERIOD|PHASE|WORKSTREAM|CATEGORY|TEMPLATE|STEP
        Example: MONTH_END_CLOSE|2025-10|I_INITIAL_COMPLIANCE|PAYROLL|PAYROLL_PERSONNEL|CT_PAYROLL_PROCESSING|PREP

        Note: cycle_key is CYCLE_TYPE|PERIOD (2 segments), so total is 7 components when split by pipe.
        """
        malformed = []
        for key in self.actual_keys.keys():
            components = key.split("|")
            if len(components) != 7:
                malformed.append(key)
                self.warnings.append(
                    f"Malformed key (expected 7 components, got {len(components)}): {key}"
                )

        return malformed

    def _fail_report(self, error_message):
        """Generate FAIL report with error"""
        self.errors.append(error_message)
        return {
            "status": "FAIL",
            "timestamp": datetime.utcnow().isoformat(),
            "errors": self.errors,
            "warnings": self.warnings,
        }

    def _print_summary(self, report):
        """Print validation summary"""
        print("\n" + "=" * 80)
        print(f"VALIDATION RESULT: {report['status']}")
        print("=" * 80)
        print(f"Expected: {report['expected_count']}")
        print(f"Actual:   {report['actual_count']}")
        print(f"Missing:  {report['missing_count']}")
        print(f"Extra:    {report['extra_count']}")
        print(f"Duplicates: {report['duplicate_count']}")
        print(f"Malformed: {report['malformed_count']}")

        if report["warnings"]:
            print(f"\n⚠️  WARNINGS ({len(report['warnings'])}):")
            for warning in report["warnings"][:10]:  # Show first 10
                print(f"  - {warning}")
            if len(report["warnings"]) > 10:
                print(f"  ... and {len(report['warnings']) - 10} more")

        if report["errors"]:
            print(f"\n❌ ERRORS ({len(report['errors'])}):")
            for error in report["errors"]:
                print(f"  - {error}")

        if report["missing_count"] > 0:
            print(f"\n📋 Missing tasks (first 5):")
            for key in report["missing_keys"][:5]:
                print(f"  - {key}")
            if report["missing_count"] > 5:
                print(f"  ... and {report['missing_count'] - 5} more")

        if report["extra_count"] > 0:
            print(f"\n🗑️  Extra tasks (first 5):")
            for key in report["extra_keys"][:5]:
                print(f"  - {key}")
            if report["extra_count"] > 5:
                print(f"  ... and {report['extra_count'] - 5} more")

        print("=" * 80)


def main():
    parser = argparse.ArgumentParser(description="Validate seed JSON vs Odoo tasks")
    parser.add_argument("--dry-run", action="store_true", help="Simulation mode")
    parser.add_argument("--output", type=str, help="Output JSON report file")
    parser.add_argument(
        "--database", type=str, default="production", help="Database name"
    )
    args = parser.parse_args()

    # Initialize Odoo environment
    odoo.tools.config.parse_config(["-d", args.database])
    registry = odoo.registry(args.database)
    with registry.cursor() as cr:
        env = api.Environment(cr, SUPERUSER_ID, {})

        # Run validation
        validator = SeedParityValidator(env)
        report = validator.validate_parity()

        # Write report to file if specified
        if args.output:
            output_path = Path(args.output)
            output_path.write_text(json.dumps(report, indent=2))
            print(f"\n📝 Report written to: {output_path}")

        # Exit with appropriate code
        if report["status"] == "PASS":
            sys.exit(0)
        elif report["status"] == "WARN":
            sys.exit(1)
        else:
            sys.exit(2)


if __name__ == "__main__":
    main()
