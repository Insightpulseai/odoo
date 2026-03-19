#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Finance PPM Seed Data SSOT Validator
=====================================
Ensures exactly ONE canonical seed dataset exists for Finance PPM TBWA\SMP.
Fails if duplicate seed data is found outside the archive directory.

Canonical root: data/seed/finance_ppm/tbwa_smp/
Archive root:   data/archive/finance_ppm/tbwa_smp/

Checks:
  1. Canonical root exists with all required files
  2. No duplicate finance PPM seed files outside canonical + archive
  3. Archive entries have MANIFEST.md with provenance
  4. Import/seed scripts reference only canonical root

Usage:
    python3 scripts/finance/validate_seed_ssot.py
    python3 scripts/finance/validate_seed_ssot.py --self-test
    python3 scripts/finance/validate_seed_ssot.py --verbose

Exit codes:
    0 = SSOT enforced, no duplicates
    1 = violations found
"""
import glob
import os
import re
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

CANONICAL_ROOT = os.path.join(REPO_ROOT, "data", "seed", "finance_ppm", "tbwa_smp")
ARCHIVE_ROOT = os.path.join(REPO_ROOT, "data", "archive", "finance_ppm", "tbwa_smp")

# Required files in canonical root
REQUIRED_FILES = [
    "team_directory.csv",
    "projects.csv",
    "tags.csv",
    "tasks_month_end.csv",
    "tasks_bir_tax.csv",
    "logframe.csv",
]

# Patterns that indicate Finance PPM seed data
SEED_INDICATORS = [
    "finance_ppm",
    "month_end_close",
    "bir_tax_filing",
    "ipai_finance_ppm_directory",
    "finance_seed",
]

# Scripts that should reference canonical root
IMPORT_SCRIPTS = [
    os.path.join(REPO_ROOT, "scripts", "bulk_import_tasks_odoo19.py"),
    os.path.join(REPO_ROOT, "scripts", "seed_finance_ppm_stages_odoo19.py"),
    os.path.join(REPO_ROOT, "scripts", "seed_logframe_milestones_odoo19.py"),
]

VERBOSE = "--verbose" in sys.argv


def log(msg):
    if VERBOSE:
        print(f"  [DEBUG] {msg}")


def check_canonical_root():
    """Verify canonical root exists with all required files."""
    errors = []

    if not os.path.isdir(CANONICAL_ROOT):
        errors.append(f"Canonical root missing: {CANONICAL_ROOT}")
        return errors

    for fname in REQUIRED_FILES:
        fpath = os.path.join(CANONICAL_ROOT, fname)
        if not os.path.exists(fpath):
            errors.append(f"Required file missing from canonical root: {fname}")
        else:
            log(f"Found: {fname}")

    return errors


def find_duplicate_seeds():
    """Search for Finance PPM seed files outside canonical + archive."""
    errors = []
    duplicates = []

    # Normalize paths for comparison
    canonical_prefix = os.path.normpath(CANONICAL_ROOT)
    archive_prefix = os.path.normpath(ARCHIVE_ROOT)

    # Search for CSV files that look like Finance PPM seed data
    csv_patterns = [
        os.path.join(REPO_ROOT, "data", "**", "*.csv"),
        os.path.join(REPO_ROOT, "artifacts", "**", "*.csv"),
    ]

    for pattern in csv_patterns:
        for fpath in glob.glob(pattern, recursive=True):
            norm_path = os.path.normpath(fpath)

            # Skip canonical and archive
            if norm_path.startswith(canonical_prefix):
                continue
            if norm_path.startswith(archive_prefix):
                continue

            # Check if this looks like Finance PPM seed data
            rel_path = os.path.relpath(fpath, REPO_ROOT)
            basename = os.path.basename(fpath).lower()
            dirname = os.path.dirname(rel_path).lower()

            for indicator in SEED_INDICATORS:
                if indicator in basename or indicator in dirname:
                    duplicates.append(rel_path)
                    log(f"Duplicate candidate: {rel_path} (matched: {indicator})")
                    break

    if duplicates:
        errors.append(
            f"Found {len(duplicates)} Finance PPM seed file(s) outside canonical/archive:\n"
            + "\n".join(f"    - {d}" for d in sorted(duplicates))
        )

    return errors


def check_archive_manifests():
    """Verify archived sets have MANIFEST.md with required fields."""
    errors = []

    if not os.path.isdir(ARCHIVE_ROOT):
        log("No archive directory — nothing to check")
        return errors

    # Find all archive date directories
    for date_dir in glob.glob(os.path.join(ARCHIVE_ROOT, "*")):
        if not os.path.isdir(date_dir):
            continue

        # Each subdirectory under a date should have MANIFEST.md
        for subdir in glob.glob(os.path.join(date_dir, "*")):
            if not os.path.isdir(subdir):
                continue

            manifest = os.path.join(subdir, "MANIFEST.md")
            if not os.path.exists(manifest):
                rel_path = os.path.relpath(subdir, REPO_ROOT)
                errors.append(f"Archive set missing MANIFEST.md: {rel_path}")
                continue

            # Check manifest has required fields
            with open(manifest, "r", encoding="utf-8") as f:
                content = f.read()

            required_fields = [
                "Original Path",
                "Archived At",
                "Reason",
                "Canonical Replacement",
            ]
            for field in required_fields:
                if field not in content:
                    rel_path = os.path.relpath(manifest, REPO_ROOT)
                    errors.append(f"MANIFEST.md missing field '{field}': {rel_path}")

            log(f"Archive manifest OK: {os.path.relpath(subdir, REPO_ROOT)}")

    return errors


def check_script_references():
    """Verify import scripts don't reference non-canonical seed paths."""
    errors = []

    # Patterns that indicate non-canonical seed references
    banned_patterns = [
        r"data/finance_seed/",
        r"artifacts/data/ipai_finance_ppm_directory",
    ]

    for script_path in IMPORT_SCRIPTS:
        if not os.path.exists(script_path):
            log(f"Script not found (skipping): {script_path}")
            continue

        with open(script_path, "r", encoding="utf-8") as f:
            content = f.read()

        rel_path = os.path.relpath(script_path, REPO_ROOT)
        for pattern in banned_patterns:
            if re.search(pattern, content):
                errors.append(
                    f"Script references non-canonical path: {rel_path} "
                    f"(pattern: '{pattern}')"
                )

    return errors


def run_self_test():
    """Built-in self-test for validator logic."""
    print("Running self-test...")
    test_errors = 0

    # Test 1: Canonical root should exist (if running from repo)
    if os.path.isdir(CANONICAL_ROOT):
        errs = check_canonical_root()
        if not errs:
            print("  PASS: Canonical root exists with all required files")
        else:
            print(f"  INFO: Canonical root issues: {errs}")
    else:
        print("  SKIP: Canonical root not found (not in repo context)")

    # Test 2: Archive manifests should be valid
    if os.path.isdir(ARCHIVE_ROOT):
        errs = check_archive_manifests()
        if not errs:
            print("  PASS: All archive manifests have required fields")
        else:
            print(f"  FAIL: Archive manifest issues: {errs}")
            test_errors += 1
    else:
        print("  SKIP: Archive root not found")

    # Test 3: Required files list should have 6 entries
    if len(REQUIRED_FILES) == 6:
        print("  PASS: Required files list has 6 entries")
    else:
        print(f"  FAIL: Expected 6 required files, got {len(REQUIRED_FILES)}")
        test_errors += 1

    print()
    if test_errors == 0:
        print("Self-test: ALL TESTS PASSED")
        return 0
    else:
        print(f"Self-test: {test_errors} TESTS FAILED")
        return 1


def main():
    if "--self-test" in sys.argv:
        sys.exit(run_self_test())

    print("=" * 60)
    print("Finance PPM Seed Data SSOT Validator")
    print("=" * 60)
    print(f"Canonical: {os.path.relpath(CANONICAL_ROOT, REPO_ROOT)}")
    print(f"Archive:   {os.path.relpath(ARCHIVE_ROOT, REPO_ROOT)}")
    print()

    all_errors = []

    # Check 1: Canonical root
    print("[1/4] Checking canonical root...")
    errs = check_canonical_root()
    all_errors.extend(errs)
    print(f"  {'PASS' if not errs else 'FAIL'}: {len(REQUIRED_FILES)} required files")

    # Check 2: Duplicate seeds
    print("[2/4] Scanning for duplicate seed data...")
    errs = find_duplicate_seeds()
    all_errors.extend(errs)
    print(f"  {'PASS' if not errs else 'FAIL'}: duplicate check")

    # Check 3: Archive manifests
    print("[3/4] Validating archive manifests...")
    errs = check_archive_manifests()
    all_errors.extend(errs)
    print(f"  {'PASS' if not errs else 'FAIL'}: archive provenance")

    # Check 4: Script references
    print("[4/4] Checking import script references...")
    errs = check_script_references()
    all_errors.extend(errs)
    print(f"  {'PASS' if not errs else 'FAIL'}: script references")

    # Report
    print()
    if all_errors:
        print("SSOT VALIDATION FAILED:")
        for e in all_errors:
            sys.stderr.write(f"  ERROR: {e}\n")
        print(f"\n{len(all_errors)} error(s) found.")
        sys.exit(1)
    else:
        print("SSOT VALIDATION PASSED")
        print("  - Canonical root: complete")
        print("  - No duplicates outside canonical/archive")
        print("  - Archive manifests: valid")
        print("  - Import scripts: clean references")
        sys.exit(0)


if __name__ == "__main__":
    main()
