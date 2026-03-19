#!/usr/bin/env python3
"""
Delta Contract Validator
========================

Validates all Delta table contracts for consistency and correctness.
Used in CI to prevent schema drift.

Usage:
    python scripts/lakehouse/validate_contracts.py

Exit codes:
    0 - All contracts valid
    1 - Validation errors found
"""

from __future__ import annotations
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from src.lakehouse.contracts import load_contracts
except ImportError as e:
    print(f"ERROR: Failed to import: {e}")
    print("Ensure PyYAML is installed: pip install pyyaml")
    sys.exit(1)


def main() -> int:
    contracts_dir = "contracts/delta"

    print("Delta Contract Validation")
    print("=" * 40)

    try:
        contracts = load_contracts(contracts_dir)
    except Exception as e:
        print(f"ERROR: Failed to load contracts: {e}")
        return 1

    if not contracts:
        print(f"WARNING: No contracts found in {contracts_dir}")
        return 0

    total_errors = 0
    warnings = 0

    for table_name, contract in sorted(contracts.items()):
        print(f"\nChecking: {table_name}")

        # Run validation
        errors = contract.validate()

        if errors:
            for err in errors:
                print(f"  ERROR: {err}")
            total_errors += len(errors)
        else:
            print(
                f"  OK: {len(contract.columns)} columns, "
                f"partition_by={list(contract.partition_by)}"
            )

        # Additional warnings
        if not contract.primary_key:
            print(f"  WARN: No primary_key defined (ok for append-only)")
            warnings += 1

        if contract.retention_days < 30:
            print(f"  WARN: Short retention ({contract.retention_days} days)")
            warnings += 1

        # Check column naming conventions
        for col in contract.columns:
            if col.name.upper() in ("SELECT", "FROM", "WHERE", "ORDER"):
                print(f"  WARN: Column '{col.name}' is a SQL keyword")
                warnings += 1

    print("\n" + "=" * 40)
    print(f"Contracts: {len(contracts)}")
    print(f"Errors: {total_errors}")
    print(f"Warnings: {warnings}")

    if total_errors > 0:
        print("\nFAILED: Fix errors above")
        return 1

    print("\nPASSED: All contracts valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
