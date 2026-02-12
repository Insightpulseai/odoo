#!/usr/bin/env python3
"""
Parity Matrix Drift Validator

Compares committed parity matrix artifacts with freshly generated version
to detect unauthorized manual edits or drift. Enforces deterministic output
policy for parity gate integrity.

Usage:
    python scripts/parity/validate_parity_matrix.py
    python scripts/parity/validate_parity_matrix.py --committed artifacts/parity/parity_matrix.json
    python scripts/parity/validate_parity_matrix.py --verbose

Exit Codes:
    0: No drift detected (pass)
    1: Drift detected (fail)
    2: Missing inputs (error)
    3: Validation failure (error)

Created: 2026-02-12
Task: Week 2 - Parity Strengthening
"""

import argparse
import json
import logging
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def normalize_matrix(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize parity matrix for comparison by removing volatile fields.

    Removes:
    - generated_at / scraped_at timestamps (non-deterministic)
    - Any other metadata that varies between runs

    Sorts:
    - All lists alphabetically
    - All dictionary keys
    """
    if isinstance(data, dict):
        normalized = {}
        for key, value in sorted(data.items()):
            # Skip timestamp fields
            if key in ('generated_at', 'scraped_at', 'updated_at', 'created_at'):
                continue
            normalized[key] = normalize_matrix(value)
        return normalized
    elif isinstance(data, list):
        # Sort lists for deterministic comparison
        if all(isinstance(item, (str, int, float)) for item in data):
            return sorted(data)
        else:
            return [normalize_matrix(item) for item in data]
    else:
        return data


def load_json_file(file_path: Path) -> Dict[str, Any]:
    """Load and parse JSON file"""
    try:
        with file_path.open('r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        sys.exit(2)  # Missing inputs
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {file_path}: {e}")
        sys.exit(3)  # Validation failure


def generate_fresh_matrix(deterministic: bool = True) -> Dict[str, Any]:
    """
    Generate fresh parity matrix by running generator script.

    Args:
        deterministic: Use --deterministic flag for reproducible output

    Returns:
        Parsed JSON data from fresh generation
    """
    generator_script = Path("scripts/parity/generate_ee_parity_matrix.py")

    if not generator_script.exists():
        logger.error(f"Generator script not found: {generator_script}")
        sys.exit(2)

    # Generate to temporary file
    output_file = Path("artifacts/parity/parity_matrix_fresh.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "python3",
        str(generator_script),
        "--json",
        "--output", str(output_file.with_suffix('.sql'))
    ]

    if deterministic:
        cmd.append("--deterministic")

    logger.info(f"Generating fresh parity matrix: {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )

        if result.returncode != 0:
            logger.error(f"Generator failed with exit code {result.returncode}")
            logger.error(f"Stdout: {result.stdout}")
            logger.error(f"Stderr: {result.stderr}")
            sys.exit(3)

        logger.info("Fresh parity matrix generated successfully")

        # Load the generated JSON
        return load_json_file(output_file)

    except subprocess.TimeoutExpired:
        logger.error("Generator script timed out after 5 minutes")
        sys.exit(3)
    except Exception as e:
        logger.error(f"Failed to generate fresh matrix: {e}")
        sys.exit(3)


def compare_matrices(committed: Dict[str, Any], fresh: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    """
    Compare committed and fresh matrices for drift.

    Args:
        committed: Normalized committed matrix data
        fresh: Normalized fresh matrix data

    Returns:
        Tuple of (has_drift, diff_details)
    """
    # Normalize both for fair comparison
    norm_committed = normalize_matrix(committed)
    norm_fresh = normalize_matrix(fresh)

    # Deep equality check
    has_drift = norm_committed != norm_fresh

    diff_details = {
        "has_drift": has_drift,
        "committed_keys": sorted(norm_committed.keys()) if isinstance(norm_committed, dict) else None,
        "fresh_keys": sorted(norm_fresh.keys()) if isinstance(norm_fresh, dict) else None,
    }

    if has_drift:
        # Try to identify specific differences
        if isinstance(norm_committed, dict) and isinstance(norm_fresh, dict):
            added_keys = set(norm_fresh.keys()) - set(norm_committed.keys())
            removed_keys = set(norm_committed.keys()) - set(norm_fresh.keys())
            changed_keys = set()

            for key in set(norm_committed.keys()) & set(norm_fresh.keys()):
                if norm_committed[key] != norm_fresh[key]:
                    changed_keys.add(key)

            diff_details.update({
                "added_keys": sorted(added_keys),
                "removed_keys": sorted(removed_keys),
                "changed_keys": sorted(changed_keys)
            })

    return has_drift, diff_details


def main():
    parser = argparse.ArgumentParser(description="Validate parity matrix for drift")
    parser.add_argument(
        "--committed",
        default="artifacts/parity/parity_matrix.json",
        help="Path to committed parity matrix JSON (default: artifacts/parity/parity_matrix.json)"
    )
    parser.add_argument(
        "--deterministic",
        action="store_true",
        default=True,
        help="Generate fresh matrix with --deterministic flag (default: true)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    committed_path = Path(args.committed)

    logger.info("="*60)
    logger.info("PARITY MATRIX DRIFT VALIDATION")
    logger.info("="*60)
    logger.info(f"Committed matrix: {committed_path}")
    logger.info(f"Deterministic mode: {args.deterministic}")

    # Step 1: Load committed matrix
    logger.info("Loading committed parity matrix...")
    committed_data = load_json_file(committed_path)
    logger.info(f"Loaded committed matrix with {len(committed_data) if isinstance(committed_data, list) else 'unknown'} entries")

    # Step 2: Generate fresh matrix
    logger.info("Generating fresh parity matrix...")
    fresh_data = generate_fresh_matrix(deterministic=args.deterministic)
    logger.info(f"Generated fresh matrix with {len(fresh_data) if isinstance(fresh_data, list) else 'unknown'} entries")

    # Step 3: Compare matrices
    logger.info("Comparing matrices for drift...")
    has_drift, diff_details = compare_matrices(committed_data, fresh_data)

    # Step 4: Report results
    logger.info("="*60)
    if has_drift:
        logger.error("❌ DRIFT DETECTED")
        logger.error("="*60)
        logger.error("The committed parity matrix differs from freshly generated version.")
        logger.error("This indicates unauthorized manual edits or non-deterministic generation.")
        logger.error("")
        logger.error("Diff details:")
        logger.error(json.dumps(diff_details, indent=2))
        logger.error("")
        logger.error("Actions required:")
        logger.error("1. Review git diff for parity matrix changes")
        logger.error("2. Regenerate with: python scripts/parity/generate_ee_parity_matrix.py --deterministic --json")
        logger.error("3. Commit regenerated artifacts")
        logger.error("="*60)

        # Save diff details for CI artifact
        drift_report_path = Path("artifacts/parity/drift_report.json")
        drift_report_path.parent.mkdir(parents=True, exist_ok=True)
        with drift_report_path.open('w') as f:
            json.dump(diff_details, f, indent=2)
        logger.error(f"Drift report saved to: {drift_report_path}")

        sys.exit(1)  # Drift detected
    else:
        logger.info("✅ NO DRIFT DETECTED")
        logger.info("="*60)
        logger.info("Committed parity matrix matches freshly generated version.")
        logger.info("Deterministic output policy enforced successfully.")
        logger.info("="*60)
        sys.exit(0)  # No drift


if __name__ == "__main__":
    main()
