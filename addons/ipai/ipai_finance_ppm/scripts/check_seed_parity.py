#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multi-Database Seed Parity Checker
Compares JSON seed definition across multiple Odoo databases.

This script acts as a "diff tool" to identify:
- Templates missing in each DB (need to be loaded)
- Extra templates in each DB (potential cleanup candidates)
- Field value mismatches (drift between seed and DB)
- Differences between two databases (sync issues)

Usage:
    # Compare seed vs single database
    python3 check_seed_parity.py --db production

    # Compare seed vs TWO databases (odoo and production)
    python3 check_seed_parity.py --db odoo production

    # Copy to production server
    scp addons/ipai_finance_ppm/scripts/check_seed_parity.py root@159.223.75.148:/root/odoo-ce/addons/ipai_finance_ppm/scripts/

    # Run inside container (compare both DBs)
    ssh root@159.223.75.148 'cd /root/odoo-ce && docker exec -i odoo-ce python3 < addons/ipai_finance_ppm/scripts/check_seed_parity.py' -- --db odoo production
"""
import argparse
import json
import os
import sys
from pathlib import Path

import odoo
from odoo import SUPERUSER_ID, api

# Configuration
SEED_FILE_NAME = "closing_v1_2_0.json"
DEFAULT_DBS = ["odoo", "production"]  # Compare both by default


def find_seed_file():
    """Locate the seed file across multiple possible paths."""
    possible_paths = [
        # Container paths (actual mount point)
        f"/mnt/extra-addons/ipai_addons/ipai_finance_ppm/seed/{SEED_FILE_NAME}",
        f"/mnt/extra-addons/ipai_finance_ppm/seed/{SEED_FILE_NAME}",
        f"/root/odoo-ce/addons/ipai_finance_ppm/seed/{SEED_FILE_NAME}",
        # Local paths (if running locally)
        f"addons/ipai_finance_ppm/seed/{SEED_FILE_NAME}",
        f"../seed/{SEED_FILE_NAME}",
        # Relative to script location
        str(Path(__file__).parent.parent / "seed" / SEED_FILE_NAME),
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return path

    return None


def load_seed_json():
    """Load and parse the JSON seed file."""
    seed_path = find_seed_file()

    if not seed_path:
        print(f"❌ Could not find seed file: {SEED_FILE_NAME}")
        print("   Searched paths:")
        for p in [
            "/mnt/extra-addons/ipai_finance_ppm/seed/",
            "/root/odoo-ce/addons/ipai_finance_ppm/seed/",
            "addons/ipai_finance_ppm/seed/",
        ]:
            print(f"   - {p}")
        return None

    try:
        with open(seed_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"✅ Loaded seed JSON from: {seed_path}")
        return data
    except Exception as e:
        print(f"❌ Error loading seed file: {str(e)}")
        return None


def flatten_seed_templates(json_data):
    """
    Flatten hierarchical JSON into a dictionary keyed by template_code.

    Structure: cycles > phases > workstreams > categories > task_templates

    Returns:
        dict: {template_code: {metadata}}
    """
    templates = {}

    version = json_data.get("version") or json_data.get("seed_version")
    print(f"ℹ️  Seed Version: {version}")

    for cycle in json_data.get("cycles", []):
        cycle_code = cycle.get("cycle_code")

        for phase in cycle.get("phases", []):
            phase_code = phase.get("phase_code")
            phase_type = phase.get("phase_type")

            for workstream in phase.get("workstreams", []):
                ws_code = workstream.get("workstream_code")

                for category in workstream.get("categories", []):
                    cat_code = category.get("category_code")

                    for tmpl in category.get("task_templates", []):
                        template_code = tmpl.get("template_code")

                        if not template_code:
                            print(f"⚠️  Skipping template without code in {cat_code}")
                            continue

                        templates[template_code] = {
                            "cycle_code": cycle_code,
                            "phase_code": phase_code,
                            "phase_type": phase_type,
                            "workstream_code": ws_code,
                            "category_code": cat_code,
                            "task_name_template": tmpl.get("task_name_template"),
                            "description_template": tmpl.get("description_template"),
                            "duration_days": tmpl.get("duration_days"),
                            "steps": [
                                s.get("step_code") for s in tmpl.get("steps", [])
                            ],
                            "step_count": len(tmpl.get("steps", [])),
                        }

    return templates


def fetch_db_templates(env):
    """
    Fetch all template records from the database.

    Returns:
        tuple: (templates_dict, is_legacy_schema)
        - templates_dict: {template_code: record_data}
        - is_legacy_schema: True if database uses old step-baked structure
    """
    try:
        TemplateModel = env["ipai.close.task.template"]
    except KeyError:
        print("❌ Model 'ipai.close.task.template' not found in database.")
        print("   Available models with 'close' in name:")
        for model_name in sorted(env.registry.models.keys()):
            if "close" in model_name:
                print(f"   - {model_name}")
        return None, False

    records = TemplateModel.search([("is_active", "=", True)])

    # Detect legacy schema: check if any templates have step suffixes
    STEP_SUFFIXES = ["|PREP", "|REVIEW", "|APPROVAL"]
    legacy_count = 0
    hierarchical_count = 0

    templates = {}
    for rec in records:
        # Check if this is legacy (step-baked) or hierarchical (parent+steps)
        is_legacy = any(suffix in rec.template_code for suffix in STEP_SUFFIXES)

        if is_legacy:
            legacy_count += 1
        else:
            hierarchical_count += 1

        templates[rec.template_code] = {
            "id": rec.id,
            "cycle_code": rec.cycle_code,
            "phase_code": rec.phase_code,
            "phase_type": rec.phase_type,
            "workstream_code": rec.workstream_code,
            "category_code": rec.category_code,
            "task_name_template": rec.task_name_template,
            "description_template": getattr(rec, "description_template", "") or "",
            "duration_days": rec.duration_days,
            "step_count": len(rec.step_ids) if hasattr(rec, "step_ids") else 0,
            "is_legacy": is_legacy,
        }

    # Database is legacy if it has more legacy templates than hierarchical
    is_legacy_schema = legacy_count > hierarchical_count

    return templates, is_legacy_schema


def compare_template(template_code, seed_data, db_data):
    """
    Compare a single template between seed and DB.

    Returns:
        list: Issues found (empty list if perfect match)
    """
    issues = []

    # Check each field
    fields_to_check = [
        "cycle_code",
        "phase_code",
        "phase_type",
        "workstream_code",
        "category_code",
        "task_name_template",
        "description_template",
        "duration_days",
    ]

    for field in fields_to_check:
        seed_val = seed_data.get(field, "")
        db_val = db_data.get(field, "")

        # Normalize empty values
        if seed_val is None:
            seed_val = ""
        if db_val is None:
            db_val = ""

        if str(seed_val) != str(db_val):
            issues.append(f"{field}: '{seed_val}' ≠ '{db_val}'")

    # Check step count
    seed_steps = seed_data.get("step_count", 0)
    db_steps = db_data.get("step_count", 0)
    if seed_steps != db_steps:
        issues.append(f"step_count: {seed_steps} ≠ {db_steps}")

    return issues


def check_single_db(db_name, seed_templates):
    """Check parity for a single database against seed."""
    try:
        # Get registry directly (config already initialized in main)
        registry = odoo.registry(db_name)

        with registry.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})

            # Fetch DB templates (returns tuple: templates, is_legacy)
            result = fetch_db_templates(env)
            if result[0] is None:
                return None, False, 2

            db_templates, is_legacy_schema = result
            return db_templates, is_legacy_schema, 0

    except Exception as e:
        print(f"❌ Error accessing database '{db_name}': {str(e)}")
        return None, False, 2


def compare_databases(db1_name, db1_templates, db2_name, db2_templates):
    """Compare templates between two databases."""
    print(f"\n{'='*80}")
    print(f"DATABASE COMPARISON: {db1_name.upper()} ⇄ {db2_name.upper()}")
    print(f"{'='*80}")

    db1_codes = set(db1_templates.keys())
    db2_codes = set(db2_templates.keys())

    only_in_db1 = db1_codes - db2_codes
    only_in_db2 = db2_codes - db1_codes
    common = db1_codes & db2_codes

    # Report templates only in DB1
    if only_in_db1:
        print(f"\n⚠️  ONLY IN {db1_name.upper()} ({len(only_in_db1)} templates):")
        for code in sorted(only_in_db1):
            tmpl = db1_templates[code]
            print(f"   - {code}")
            print(f"     Name: {tmpl['task_name_template']}")
    else:
        print(f"\n✅ No templates exclusive to {db1_name}")

    # Report templates only in DB2
    if only_in_db2:
        print(f"\n⚠️  ONLY IN {db2_name.upper()} ({len(only_in_db2)} templates):")
        for code in sorted(only_in_db2):
            tmpl = db2_templates[code]
            print(f"   - {code}")
            print(f"     Name: {tmpl['task_name_template']}")
    else:
        print(f"\n✅ No templates exclusive to {db2_name}")

    # Check content parity for common templates
    print(f"\n🔍 CONTENT COMPARISON ({len(common)} shared templates)")
    print("-" * 80)

    mismatches = []
    for code in sorted(common):
        issues = compare_template(code, db1_templates[code], db2_templates[code])
        if issues:
            mismatches.append((code, issues))

    if mismatches:
        print(f"⚠️  Found {len(mismatches)} template(s) with differences:\n")
        for code, issues in mismatches:
            print(f"   ⚠️  {code}:")
            for issue in issues:
                print(f"      - {issue}")
            print()
    else:
        print("✅ All shared templates have matching content")

    has_issues = bool(only_in_db1 or only_in_db2 or mismatches)
    return has_issues


def check_parity(db_names=None):
    """Main parity check function supporting multiple databases."""
    try:
        if db_names is None:
            db_names = DEFAULT_DBS

        print("=" * 80)
        print("MULTI-DATABASE SEED PARITY CHECKER")
        print("=" * 80)
        print(f"Databases to check: {', '.join(db_names)}")
        print()

        # Initialize Odoo configuration once
        odoo.tools.config.parse_config([])

        # 1. Load Seed JSON
        json_data = load_seed_json()
        if not json_data:
            return 2

        seed_templates = flatten_seed_templates(json_data)
        print(f"\n📦 Seed Templates: {len(seed_templates)}")

        # 2. Fetch templates from all databases
        db_data = {}
        legacy_dbs = {}
        for db_name in db_names:
            print(f"\n🗄️  Connecting to database: {db_name}")
            templates, is_legacy, exit_code = check_single_db(db_name, seed_templates)
            if exit_code != 0:
                print(f"   ❌ Failed to access {db_name}")
                continue

            db_data[db_name] = templates
            legacy_dbs[db_name] = is_legacy

            if is_legacy:
                print(
                    f"   ⚠️  Loaded {len(templates)} templates from {db_name} (LEGACY SCHEMA DETECTED)"
                )
                print(
                    f"   ℹ️  Run migrate_templates_v1_2_0.py to upgrade to hierarchical structure"
                )
            else:
                print(f"   ✅ Loaded {len(templates)} templates from {db_name}")

        if not db_data:
            print("\n❌ No databases successfully loaded")
            return 2

        # 3. Compare each database against seed
        all_issues = []

        for db_name, db_templates in db_data.items():
            print(f"\n{'='*80}")
            print(f"SEED ⇄ {db_name.upper()} COMPARISON")
            print(f"{'='*80}")

            seed_codes = set(seed_templates.keys())
            db_codes = set(db_templates.keys())

            missing_in_db = seed_codes - db_codes
            extra_in_db = db_codes - seed_codes
            common = seed_codes & db_codes

            # Report missing templates
            if missing_in_db:
                print(
                    f"\n❌ MISSING IN {db_name.upper()} ({len(missing_in_db)} templates):"
                )
                for code in sorted(missing_in_db):
                    tmpl = seed_templates[code]
                    print(f"   - {code}: {tmpl['task_name_template']}")
                all_issues.append(f"{db_name}: {len(missing_in_db)} missing")
            else:
                print(f"\n✅ No missing templates in {db_name}")

            # Report extra templates
            if extra_in_db:
                print(
                    f"\n⚠️  EXTRA IN {db_name.upper()} ({len(extra_in_db)} templates):"
                )
                for code in sorted(extra_in_db):
                    tmpl = db_templates[code]
                    print(f"   - {code}: {tmpl['task_name_template']}")
                all_issues.append(f"{db_name}: {len(extra_in_db)} extra")
            else:
                print(f"\n✅ No extra templates in {db_name}")

            # Check content parity
            print(f"\n🔍 CONTENT PARITY ({len(common)} shared templates)")
            print("-" * 80)

            mismatches = []
            for code in sorted(common):
                issues = compare_template(
                    code, seed_templates[code], db_templates[code]
                )
                if issues:
                    mismatches.append((code, issues))

            if mismatches:
                print(
                    f"⚠️  Found {len(mismatches)} template(s) with content mismatches:"
                )
                for code, issues in mismatches[:5]:  # Show first 5
                    print(f"   ⚠️  {code}:")
                    for issue in issues:
                        print(f"      - {issue}")
                if len(mismatches) > 5:
                    print(f"   ... and {len(mismatches) - 5} more")
                all_issues.append(f"{db_name}: {len(mismatches)} mismatches")
            else:
                print("✅ All shared templates have matching content")

        # 4. If multiple databases, compare them against each other
        if len(db_data) == 2:
            db_names_list = list(db_data.keys())
            has_db_diff = compare_databases(
                db_names_list[0],
                db_data[db_names_list[0]],
                db_names_list[1],
                db_data[db_names_list[1]],
            )
            if has_db_diff:
                all_issues.append("Databases not in sync")

        # 5. Final Summary
        print(f"\n{'='*80}")
        print("FINAL SUMMARY")
        print(f"{'='*80}")
        print(f"Seed Templates: {len(seed_templates)}")
        for db_name, db_templates in db_data.items():
            print(f"{db_name.upper()} Templates: {len(db_templates)}")
        print()

        if all_issues:
            print("Status: ⚠️  PARITY ISSUES DETECTED")
            print("\nIssues found:")
            for issue in all_issues:
                print(f"  - {issue}")
            print("\nRecommended Actions:")
            print("  1. Sync databases: Run generator on missing databases")
            print("  2. Review extra templates: Archive or delete if obsolete")
            print("  3. Update mismatched templates: Re-run generator")
            return 1
        else:
            print("Status: ✅ PERFECT PARITY ACROSS ALL DATABASES")
            return 0

    except Exception as e:
        print(f"\n❌ FATAL ERROR: {str(e)}")
        import traceback

        traceback.print_exc()
        return 2


def main():
    """Parse arguments and run parity check."""
    parser = argparse.ArgumentParser(
        description="Multi-Database Seed Parity Checker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check both default databases (odoo + production)
  python3 check_seed_parity.py

  # Check single database
  python3 check_seed_parity.py --db production

  # Check two specific databases
  python3 check_seed_parity.py --db staging production
        """,
    )

    parser.add_argument(
        "--db",
        nargs="+",
        default=DEFAULT_DBS,
        help=f'Database name(s) to check (default: {" ".join(DEFAULT_DBS)})',
    )

    args = parser.parse_args()

    exit_code = check_parity(args.db)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
