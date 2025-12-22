#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Legacy Template Migration: v1.1.0 → v1.2.0
Migrates step-baked template codes (CT_X|PREP) to hierarchical parent+steps structure.

Old structure (v1.1.0):
  - Multiple records: CT_ADJUSTMENTS|PREP, CT_ADJUSTMENTS|REVIEW, CT_ADJUSTMENTS|APPROVAL
  - Steps baked into template_code field

New structure (v1.2.0):
  - One parent record: CT_ADJUSTMENTS
  - Three child step records linked via step_ids Many2many

Usage:
    # Run on production database
    ssh root@159.223.75.148 'cd /root/odoo-ce && docker exec -i odoo-ce odoo shell -d production' < addons/ipai_finance_ppm/scripts/migrate_templates_v1_2_0.py

    # Or via Python
    python3 migrate_templates_v1_2_0.py --db production
"""
import sys
import argparse
import odoo
from odoo import api, SUPERUSER_ID
from collections import defaultdict


STEP_SUFFIXES = ["|PREP", "|REVIEW", "|APPROVAL"]


def migrate_legacy_templates(env, dry_run=False):
    """
    Migrate legacy step-baked templates to hierarchical parent+steps structure.

    Returns:
        dict: Migration statistics
    """
    stats = {
        "legacy_found": 0,
        "parents_created": 0,
        "parents_updated": 0,
        "steps_created": 0,
        "legacy_deactivated": 0,
        "errors": [],
    }

    print("=" * 80)
    print("LEGACY TEMPLATE MIGRATION: v1.1.0 → v1.2.0")
    print("=" * 80)
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE MIGRATION'}")
    print()

    TemplateModel = env["ipai.close.task.template"]
    StepModel = env["ipai.close.task.step"]

    # 1. Find all legacy templates (those with step suffix in template_code)
    all_templates = TemplateModel.search([])
    legacy_templates = []

    for tmpl in all_templates:
        if any(suffix in tmpl.template_code for suffix in STEP_SUFFIXES):
            legacy_templates.append(tmpl)

    stats["legacy_found"] = len(legacy_templates)
    print(f"📦 Found {len(legacy_templates)} legacy templates with step suffixes")

    if not legacy_templates:
        print("✅ No legacy templates found - database already migrated!")
        return stats

    # 2. Group by base template code
    template_groups = defaultdict(list)
    for tmpl in legacy_templates:
        # Extract base code (everything before last pipe)
        base_code = tmpl.template_code
        for suffix in STEP_SUFFIXES:
            if suffix in base_code:
                base_code = base_code.replace(suffix, "")
                break
        template_groups[base_code].append(tmpl)

    print(f"\n🔍 Grouped into {len(template_groups)} unique base templates:")
    for base_code, templates in sorted(template_groups.items()):
        print(f"   - {base_code}: {len(templates)} step variants")

    # 3. Process each template group
    print(f"\n{'[DRY RUN] ' if dry_run else ''}Processing template groups...")
    print("-" * 80)

    for base_code, step_templates in sorted(template_groups.items()):
        try:
            print(f"\n📋 {base_code}")

            # Check if parent already exists
            existing_parent = TemplateModel.search(
                [("template_code", "=", base_code), ("is_active", "=", True)], limit=1
            )

            if existing_parent and not any(
                suffix in existing_parent.template_code for suffix in STEP_SUFFIXES
            ):
                print(f"   ℹ️  Parent already exists (ID: {existing_parent.id})")
                parent_template = existing_parent
                stats["parents_updated"] += 1
            else:
                # Create parent from first step template
                reference_tmpl = step_templates[0]

                parent_vals = {
                    "template_code": base_code,
                    "cycle_code": reference_tmpl.cycle_code,
                    "phase_code": reference_tmpl.phase_code,
                    "phase_type": reference_tmpl.phase_type,
                    "workstream_code": reference_tmpl.workstream_code,
                    "category_code": reference_tmpl.category_code,
                    "task_name_template": reference_tmpl.task_name_template.replace(
                        "|PREP", ""
                    )
                    .replace("|REVIEW", "")
                    .replace("|APPROVAL", ""),
                    "duration_days": reference_tmpl.duration_days,
                    "x_legacy_migration": True,  # Mark as migrated
                }

                # Add required name fields with defaults from reference template or generated from codes
                parent_vals["phase_name"] = (
                    getattr(reference_tmpl, "phase_name", None)
                    or reference_tmpl.phase_code
                    or "Unknown Phase"
                )
                parent_vals["workstream_name"] = (
                    getattr(reference_tmpl, "workstream_name", None)
                    or reference_tmpl.workstream_code
                    or ""
                )
                parent_vals["category_name"] = (
                    getattr(reference_tmpl, "category_name", None)
                    or reference_tmpl.category_code
                    or ""
                )

                # Add description_template if field exists
                if hasattr(reference_tmpl, "description_template"):
                    parent_vals["description_template"] = (
                        reference_tmpl.description_template or ""
                    )

                if not dry_run:
                    parent_template = TemplateModel.create(parent_vals)
                    print(
                        f"   ✅ Created parent template (ID: {parent_template.id if parent_template else 'N/A'})"
                    )
                    stats["parents_created"] += 1
                else:
                    parent_template = None
                    print(f"   [DRY RUN] Would create parent template")
                    stats["parents_created"] += 1

            # Create/link step records
            step_map = {}
            for step_tmpl in step_templates:
                # Determine step code from suffix
                step_code = None
                if "|PREP" in step_tmpl.template_code:
                    step_code = "PREP"
                elif "|REVIEW" in step_tmpl.template_code:
                    step_code = "REVIEW"
                elif "|APPROVAL" in step_tmpl.template_code:
                    step_code = "APPROVAL"

                if not step_code:
                    print(
                        f"   ⚠️  Could not determine step code for {step_tmpl.template_code}"
                    )
                    continue

                # Check if step already exists for this parent
                if not dry_run and parent_template:
                    existing_step = StepModel.search(
                        [
                            ("step_code", "=", step_code),
                            ("template_id", "=", parent_template.id),
                        ],
                        limit=1,
                    )

                    if existing_step:
                        print(f"   ℹ️  Step {step_code} already exists")
                        step_map[step_code] = existing_step
                    else:
                        # Create new step
                        step_vals = {
                            "step_code": step_code,
                            "step_name": f"{step_code.title()} Step",
                            "sequence": {"PREP": 10, "REVIEW": 20, "APPROVAL": 30}.get(
                                step_code, 99
                            ),
                            "template_id": parent_template.id,
                            "x_legacy_template_code": step_tmpl.template_code,  # Preserve old code
                        }

                        step_record = StepModel.create(step_vals)
                        step_map[step_code] = step_record
                        print(f"   ✅ Created step {step_code} (ID: {step_record.id})")
                        stats["steps_created"] += 1
                else:
                    print(f"   [DRY RUN] Would create step {step_code}")
                    stats["steps_created"] += 1

            # Deactivate legacy templates
            for step_tmpl in step_templates:
                if not dry_run:
                    # Mark as obsolete if field exists, otherwise just deactivate
                    if hasattr(step_tmpl, "x_obsolete"):
                        step_tmpl.write({"is_active": False, "x_obsolete": True})
                    else:
                        step_tmpl.write({"is_active": False})
                    stats["legacy_deactivated"] += 1
                else:
                    print(f"   [DRY RUN] Would deactivate {step_tmpl.template_code}")
                    stats["legacy_deactivated"] += 1

            print(
                f"   ✅ Migrated {base_code} ({len(step_templates)} legacy → 1 parent + {len(step_map)} steps)"
            )

        except Exception as e:
            error_msg = f"Error migrating {base_code}: {str(e)}"
            print(f"   ❌ {error_msg}")
            stats["errors"].append(error_msg)

    return stats


def print_migration_report(stats):
    """Print migration summary report."""
    print("\n" + "=" * 80)
    print("MIGRATION REPORT")
    print("=" * 80)
    print(f"Legacy templates found:      {stats['legacy_found']}")
    print(f"Parent templates created:    {stats['parents_created']}")
    print(f"Parent templates updated:    {stats['parents_updated']}")
    print(f"Step records created:        {stats['steps_created']}")
    print(f"Legacy templates deactivated: {stats['legacy_deactivated']}")

    if stats["errors"]:
        print(f"\n⚠️  Errors encountered: {len(stats['errors'])}")
        for error in stats["errors"]:
            print(f"   - {error}")

    print("\n" + "=" * 80)
    if stats["legacy_found"] > 0 and not stats["errors"]:
        print("✅ MIGRATION COMPLETED SUCCESSFULLY")
    elif stats["legacy_found"] == 0:
        print("ℹ️  NO MIGRATION NEEDED - Database already uses v1.2.0 structure")
    else:
        print("⚠️  MIGRATION COMPLETED WITH ERRORS - Review above")
    print("=" * 80)


def main():
    """Main migration entry point."""
    parser = argparse.ArgumentParser(
        description="Migrate legacy templates from v1.1.0 to v1.2.0 structure",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run (no changes)
  python3 migrate_templates_v1_2_0.py --db production --dry-run

  # Live migration
  python3 migrate_templates_v1_2_0.py --db production

  # Via Odoo shell
  odoo shell -d production < migrate_templates_v1_2_0.py
        """,
    )

    parser.add_argument(
        "--db", default="production", help="Database name (default: production)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without modifying database",
    )

    args = parser.parse_args()

    try:
        # Initialize Odoo
        odoo.tools.config.parse_config(["-d", args.db])
        registry = odoo.registry(args.db)

        with registry.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})

            # Run migration
            stats = migrate_legacy_templates(env, dry_run=args.dry_run)

            # Print report
            print_migration_report(stats)

            # Commit if not dry run
            if not args.dry_run:
                cr.commit()
                print("\n✅ Changes committed to database")
            else:
                print("\n[DRY RUN] No changes made to database")

            # Exit code
            sys.exit(0 if not stats["errors"] else 1)

    except Exception as e:
        print(f"\n❌ FATAL ERROR: {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(2)


if __name__ == "__main__":
    main()
