#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Finance PPM Team Directory Validator
=====================================
Validates the canonical team directory CSV against invariants:
  - Exactly 9 team members
  - Tier counts: Director=1, Senior Manager=1, Manager=1, Analyst=6
  - JPAL role == Finance Analyst (never Finance Supervisor)
  - Unique codes and names
  - Allowed role/tier enums only
  - Cross-artifact parity with import script EMPLOYEES dict

Canonical source: data/seed/finance_ppm/tbwa_smp/team_directory.csv

Usage:
    python3 scripts/finance/validate_team_directory.py
    python3 scripts/finance/validate_team_directory.py --self-test
    python3 scripts/finance/validate_team_directory.py --check-import-script

Exit codes:
    0 = all checks passed
    1 = validation failure (details printed to stderr)
"""
import csv
import os
import re
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CANONICAL_CSV = os.path.join(REPO_ROOT, "data", "seed", "finance_ppm", "tbwa_smp", "team_directory.csv")
IMPORT_SCRIPT = os.path.join(REPO_ROOT, "scripts", "bulk_import_tasks_odoo19.py")

# ── Invariants ──────────────────────────────────────────────────────────────

EXPECTED_CODES = {"CKVC", "RIM", "BOM", "JPAL", "LAS", "JLI", "RMQB", "JAP", "JRMO"}
EXPECTED_COUNT = 9

ALLOWED_ROLES = {
    "Finance Director",
    "Senior Finance Manager",
    "Finance Manager",
    "Finance Analyst",
}

ALLOWED_TIERS = {
    "Director",
    "Senior Manager",
    "Manager",
    "Analyst",
}

EXPECTED_TIER_COUNTS = {
    "Director": 1,
    "Senior Manager": 1,
    "Manager": 1,
    "Analyst": 6,
}

# Role-to-Tier deterministic mapping
ROLE_TO_TIER = {
    "Finance Director": "Director",
    "Senior Finance Manager": "Senior Manager",
    "Finance Manager": "Manager",
    "Finance Analyst": "Analyst",
}

# Hard constraint: JPAL must be Finance Analyst
JPAL_REQUIRED_ROLE = "Finance Analyst"


def load_csv(path):
    """Load team directory CSV and return list of dicts."""
    if not os.path.exists(path):
        return None, f"File not found: {path}"
    with open(path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    return rows, None


def validate_directory(rows):
    """Run all invariant checks. Returns list of error strings."""
    errors = []

    # ── Check 1: Exact headcount ────────────────────────────────────────
    if len(rows) != EXPECTED_COUNT:
        errors.append(
            f"Headcount mismatch: expected {EXPECTED_COUNT}, got {len(rows)}"
        )

    # ── Check 2: Exact code set ─────────────────────────────────────────
    codes = {r.get("Code", "").strip().upper() for r in rows}
    missing = EXPECTED_CODES - codes
    extra = codes - EXPECTED_CODES
    if missing:
        errors.append(f"Missing codes: {sorted(missing)}")
    if extra:
        errors.append(f"Unexpected codes: {sorted(extra)}")

    # ── Check 3: Code uniqueness ────────────────────────────────────────
    code_list = [r.get("Code", "").strip().upper() for r in rows]
    dupes = [c for c in code_list if code_list.count(c) > 1]
    if dupes:
        errors.append(f"Duplicate codes: {sorted(set(dupes))}")

    # ── Check 4: Name uniqueness ────────────────────────────────────────
    names = [r.get("Name", "").strip() for r in rows]
    name_dupes = [n for n in names if names.count(n) > 1]
    if name_dupes:
        errors.append(f"Duplicate names: {sorted(set(name_dupes))}")

    # ── Check 5: Allowed roles only ─────────────────────────────────────
    for row in rows:
        role = row.get("Role", "").strip()
        if role not in ALLOWED_ROLES:
            errors.append(
                f"Invalid role for {row.get('Code', '?')}: '{role}' "
                f"(allowed: {sorted(ALLOWED_ROLES)})"
            )

    # ── Check 6: Allowed tiers only ─────────────────────────────────────
    has_tier_column = any("Tier" in r for r in rows)
    if has_tier_column:
        for row in rows:
            tier = row.get("Tier", "").strip()
            if tier not in ALLOWED_TIERS:
                errors.append(
                    f"Invalid tier for {row.get('Code', '?')}: '{tier}' "
                    f"(allowed: {sorted(ALLOWED_TIERS)})"
                )
    else:
        errors.append("Missing 'Tier' column in team_directory.csv")

    # ── Check 7: Tier counts ───────────────────────────────────────────
    if has_tier_column:
        tier_counts = {}
        for row in rows:
            tier = row.get("Tier", "").strip()
            tier_counts[tier] = tier_counts.get(tier, 0) + 1
        for tier, expected in EXPECTED_TIER_COUNTS.items():
            actual = tier_counts.get(tier, 0)
            if actual != expected:
                errors.append(
                    f"Tier count mismatch for '{tier}': expected {expected}, got {actual}"
                )

    # ── Check 8: Role-Tier consistency ──────────────────────────────────
    if has_tier_column:
        for row in rows:
            role = row.get("Role", "").strip()
            tier = row.get("Tier", "").strip()
            expected_tier = ROLE_TO_TIER.get(role)
            if expected_tier and tier != expected_tier:
                errors.append(
                    f"Role-Tier mismatch for {row.get('Code', '?')}: "
                    f"role='{role}' should map to tier='{expected_tier}', got '{tier}'"
                )

    # ── Check 9: JPAL must be Finance Analyst ───────────────────────────
    jpal_rows = [r for r in rows if r.get("Code", "").strip().upper() == "JPAL"]
    if jpal_rows:
        jpal_role = jpal_rows[0].get("Role", "").strip()
        if jpal_role != JPAL_REQUIRED_ROLE:
            errors.append(
                f"JPAL role mismatch: expected '{JPAL_REQUIRED_ROLE}', got '{jpal_role}'"
            )
    else:
        errors.append("JPAL not found in directory")

    return errors


def check_import_script_parity():
    """Cross-check import script EMPLOYEES dict matches canonical CSV."""
    errors = []

    if not os.path.exists(IMPORT_SCRIPT):
        errors.append(f"Import script not found: {IMPORT_SCRIPT}")
        return errors

    with open(IMPORT_SCRIPT, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract EMPLOYEES dict entries via regex
    pattern = r'"(\w+)":\s*\{\s*"name":\s*"([^"]+)",\s*"email":\s*"([^"]+)",\s*"role":\s*"([^"]+)"'
    matches = re.findall(pattern, content)

    if not matches:
        errors.append("Could not parse EMPLOYEES dict from import script")
        return errors

    script_employees = {code: {"name": name, "email": email, "role": role}
                        for code, name, email, role in matches}

    # Load canonical CSV
    rows, err = load_csv(CANONICAL_CSV)
    if err:
        errors.append(f"Cannot load canonical CSV: {err}")
        return errors

    csv_employees = {}
    for row in rows:
        code = row.get("Code", "").strip().upper()
        csv_employees[code] = {
            "name": row.get("Name", "").strip(),
            "email": row.get("Email", "").strip(),
            "role": row.get("Role", "").strip(),
        }

    # Compare
    csv_codes = set(csv_employees.keys())
    script_codes = set(script_employees.keys())

    if csv_codes != script_codes:
        errors.append(
            f"Code set mismatch between CSV and import script: "
            f"CSV={sorted(csv_codes)}, Script={sorted(script_codes)}"
        )

    for code in csv_codes & script_codes:
        csv_emp = csv_employees[code]
        script_emp = script_employees[code]
        for field in ["name", "email", "role"]:
            if csv_emp[field] != script_emp[field]:
                errors.append(
                    f"Parity mismatch for {code}.{field}: "
                    f"CSV='{csv_emp[field]}', Script='{script_emp[field]}'"
                )

    return errors


def run_self_test():
    """Run built-in self-test to verify validator logic."""
    print("Running self-test...")
    test_errors = 0

    # Test 1: Valid data should pass
    valid_rows = [
        {"Code": "CKVC", "Name": "Khalil Veracruz", "Role": "Finance Director", "Tier": "Director"},
        {"Code": "RIM", "Name": "Rey Meran", "Role": "Senior Finance Manager", "Tier": "Senior Manager"},
        {"Code": "BOM", "Name": "Beng Manalo", "Role": "Finance Manager", "Tier": "Manager"},
        {"Code": "JPAL", "Name": "Jinky Paladin", "Role": "Finance Analyst", "Tier": "Analyst"},
        {"Code": "LAS", "Name": "Amor Lasaga", "Role": "Finance Analyst", "Tier": "Analyst"},
        {"Code": "JLI", "Name": "Jerald Lorente", "Role": "Finance Analyst", "Tier": "Analyst"},
        {"Code": "RMQB", "Name": "Sally Brillantes", "Role": "Finance Analyst", "Tier": "Analyst"},
        {"Code": "JAP", "Name": "Jasmin Ignacio", "Role": "Finance Analyst", "Tier": "Analyst"},
        {"Code": "JRMO", "Name": "Jhoee Oliva", "Role": "Finance Analyst", "Tier": "Analyst"},
    ]
    errs = validate_directory(valid_rows)
    if errs:
        print(f"  FAIL: Valid data produced errors: {errs}")
        test_errors += 1
    else:
        print("  PASS: Valid data accepted")

    # Test 2: JPAL as Finance Supervisor should fail
    bad_jpal = [dict(r) for r in valid_rows]
    for r in bad_jpal:
        if r["Code"] == "JPAL":
            r["Role"] = "Finance Supervisor"
    errs = validate_directory(bad_jpal)
    jpal_errors = [e for e in errs if "JPAL" in e or "Invalid role" in e]
    if jpal_errors:
        print("  PASS: JPAL as Finance Supervisor correctly rejected")
    else:
        print("  FAIL: JPAL as Finance Supervisor was not caught")
        test_errors += 1

    # Test 3: Wrong tier count should fail
    bad_tier = [dict(r) for r in valid_rows]
    for r in bad_tier:
        if r["Code"] == "JRMO":
            r["Tier"] = "Manager"
    errs = validate_directory(bad_tier)
    tier_errors = [e for e in errs if "Tier count" in e or "Role-Tier" in e]
    if tier_errors:
        print("  PASS: Wrong tier count correctly rejected")
    else:
        print("  FAIL: Wrong tier count was not caught")
        test_errors += 1

    # Test 4: Duplicate code should fail
    bad_dupe = [dict(r) for r in valid_rows]
    bad_dupe[8]["Code"] = "JPAL"
    errs = validate_directory(bad_dupe)
    dupe_errors = [e for e in errs if "Duplicate" in e or "Missing" in e]
    if dupe_errors:
        print("  PASS: Duplicate code correctly rejected")
    else:
        print("  FAIL: Duplicate code was not caught")
        test_errors += 1

    # Test 5: Missing member should fail
    short = valid_rows[:8]
    errs = validate_directory(short)
    count_errors = [e for e in errs if "Headcount" in e or "Missing" in e]
    if count_errors:
        print("  PASS: Missing member correctly rejected")
    else:
        print("  FAIL: Missing member was not caught")
        test_errors += 1

    print()
    if test_errors == 0:
        print("Self-test: ALL 5 TESTS PASSED")
        return 0
    else:
        print(f"Self-test: {test_errors} TESTS FAILED")
        return 1


def main():
    if "--self-test" in sys.argv:
        sys.exit(run_self_test())

    print("=" * 60)
    print("Finance PPM Team Directory Validator")
    print("=" * 60)
    print(f"Canonical: {CANONICAL_CSV}")
    print()

    # Load and validate canonical CSV
    rows, err = load_csv(CANONICAL_CSV)
    if err:
        sys.stderr.write(f"FATAL: {err}\n")
        sys.exit(1)

    print(f"Loaded {len(rows)} rows")
    errors = validate_directory(rows)

    # Cross-check import script if requested or by default
    if "--check-import-script" in sys.argv or "--check-import-script" not in sys.argv:
        print()
        print("Checking import script parity...")
        parity_errors = check_import_script_parity()
        errors.extend(parity_errors)

    # Report
    print()
    if errors:
        print("VALIDATION FAILED:")
        for e in errors:
            sys.stderr.write(f"  ERROR: {e}\n")
        print(f"\n{len(errors)} error(s) found.")
        sys.exit(1)
    else:
        print("VALIDATION PASSED: All invariants satisfied")
        print("  - 9 members, unique codes/names")
        print("  - Tier counts: Director=1, Senior Manager=1, Manager=1, Analyst=6")
        print("  - JPAL = Finance Analyst")
        print("  - Import script parity confirmed")
        sys.exit(0)


if __name__ == "__main__":
    main()
