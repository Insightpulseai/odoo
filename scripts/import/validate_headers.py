#!/usr/bin/env python3
"""
Validate Odoo import CSV headers against the canonical contract.

This script compares the headers in import CSV files against the expected
headers from introspection, ensuring no schema drift occurs.

Usage:
    python scripts/import/validate_headers.py
    python scripts/import/validate_headers.py --update  # Update contract file
"""

import argparse
import csv
import os
import sys
from pathlib import Path

# Contract file location
PROJECT_ROOT = Path(__file__).parent.parent.parent
TEMPLATES_DIR = PROJECT_ROOT / "data" / "import_templates"
CONTRACT_FILE = TEMPLATES_DIR / "odoo_import_headers.contract.json"

# Models and their expected CSV files
IMPORT_FILES = {
    "project.task.type": "01_project.task.type.csv",
    "project.project": "02_project.project.csv",
    "project.milestone": "03_project.milestone.csv",
    "project.task": "04_project.task.csv",
    "project.task.dependencies": "05_project.task.dependencies.csv",
    "project.task.recurrence": "06_project.task.recurrence.csv",
    "mail.activity": "07_mail.activity.csv",
}


def get_csv_headers(csv_path: Path) -> list[str]:
    """Extract headers from a CSV file."""
    if not csv_path.exists():
        return []

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        try:
            headers = next(reader)
            return [h.strip() for h in headers]
        except StopIteration:
            return []


def load_contract() -> dict:
    """Load the header contract from JSON file."""
    import json

    if not CONTRACT_FILE.exists():
        return {}

    with open(CONTRACT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_contract(contract: dict):
    """Save the header contract to JSON file."""
    import json

    with open(CONTRACT_FILE, "w", encoding="utf-8") as f:
        json.dump(contract, f, indent=2, sort_keys=True)
    print(f"Contract saved to: {CONTRACT_FILE}")


def generate_current_contract() -> dict:
    """Generate contract from current CSV files."""
    contract = {}

    for model_name, csv_file in IMPORT_FILES.items():
        csv_path = TEMPLATES_DIR / csv_file
        headers = get_csv_headers(csv_path)

        if headers:
            contract[model_name] = {
                "file": csv_file,
                "headers": headers,
            }

    return contract


def validate_headers() -> bool:
    """Validate current CSV headers against contract."""
    contract = load_contract()
    current = generate_current_contract()

    if not contract:
        print("No contract file found. Run with --update to create one.")
        return True  # Not a failure if no contract exists

    errors = []

    for model_name, expected in contract.items():
        if model_name not in current:
            # File removed - only warn
            print(f"WARNING: {model_name} CSV file missing: {expected['file']}")
            continue

        actual_headers = current[model_name]["headers"]
        expected_headers = expected["headers"]

        # Check for header drift
        if actual_headers != expected_headers:
            errors.append({
                "model": model_name,
                "file": expected["file"],
                "expected": expected_headers,
                "actual": actual_headers,
            })

    # Check for new files not in contract
    for model_name in current:
        if model_name not in contract:
            print(f"INFO: New model {model_name} found - not in contract")

    if errors:
        print("=" * 60)
        print("HEADER DRIFT DETECTED")
        print("=" * 60)

        for err in errors:
            print(f"\nModel: {err['model']}")
            print(f"File:  {err['file']}")
            print(f"Expected: {err['expected']}")
            print(f"Actual:   {err['actual']}")

            # Show diff
            expected_set = set(err['expected'])
            actual_set = set(err['actual'])

            added = actual_set - expected_set
            removed = expected_set - actual_set

            if added:
                print(f"  + Added:   {list(added)}")
            if removed:
                print(f"  - Removed: {list(removed)}")

        print("\n" + "=" * 60)
        print("Fix by either:")
        print("  1. Update CSV headers to match contract")
        print("  2. Run with --update to accept new headers")
        print("=" * 60)

        return False

    print("All import headers match contract.")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Validate Odoo import CSV headers against contract"
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="Update the contract file with current headers"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Only output errors"
    )

    args = parser.parse_args()

    if args.update:
        contract = generate_current_contract()
        save_contract(contract)
        print(f"Contract updated with {len(contract)} models")
        return 0

    if not args.quiet:
        print("Validating import CSV headers...")
        print(f"Templates dir: {TEMPLATES_DIR}")
        print(f"Contract file: {CONTRACT_FILE}")
        print()

    if validate_headers():
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
