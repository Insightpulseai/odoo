#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Import mail.activity from CSV with external ID resolution.

Usage:
  docker exec -i odoo-core odoo shell -d odoo_core --no-http < scripts/import/import_activities.py

Or with custom path:
  echo "ACTIVITY_CSV='/path/to/activities.csv'" | cat - scripts/import/import_activities.py | \
    docker exec -i odoo-core odoo shell -d odoo_core --no-http
"""

import csv
import os
import sys

# Configuration
ACTIVITY_CSV = os.environ.get(
    "ACTIVITY_CSV", "/mnt/extra-addons/../data/import_templates/07_mail.activity.csv"
)
DRY_RUN = os.environ.get("DRY_RUN", "false").lower() == "true"

print("=" * 60)
print("MAIL.ACTIVITY IMPORT FROM EXTERNAL IDS")
print("=" * 60)
print(f"CSV Path: {ACTIVITY_CSV}")
print(f"Dry Run: {DRY_RUN}")
print()


def xmlid_to_record(xmlid):
    """Resolve external ID to record, return None if not found."""
    if not xmlid or not xmlid.strip():
        return None
    try:
        return env.ref(xmlid.strip(), raise_if_not_found=False)
    except Exception:
        return None


def import_activities(csv_path):
    """Import activities from CSV with external ID resolution."""
    if not os.path.exists(csv_path):
        print(f"ERROR: File not found: {csv_path}")
        return 0, []

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        print("No rows to import")
        return 0, []

    Activity = env["mail.activity"].sudo()
    IrModelData = env["ir.model.data"].sudo()

    created = 0
    errors = []

    for i, row in enumerate(rows, 1):
        try:
            # Parse external ID for the activity record itself
            activity_xmlid = row.get("id", "").strip()
            if not activity_xmlid:
                errors.append(f"Row {i}: Missing 'id' (external ID)")
                continue

            # Check if already exists
            existing = xmlid_to_record(activity_xmlid)
            if existing:
                print(
                    f"Row {i}: SKIP - {activity_xmlid} already exists (ID: {existing.id})"
                )
                continue

            # Resolve target record (res_external_id -> res_id)
            res_external_id = row.get("res_external_id", "").strip()
            if not res_external_id:
                errors.append(f"Row {i}: Missing 'res_external_id'")
                continue

            target = xmlid_to_record(res_external_id)
            if not target:
                errors.append(f"Row {i}: Target not found: {res_external_id}")
                continue

            # Resolve activity type
            activity_type_xmlid = row.get("activity_type_id/id", "").strip()
            activity_type = xmlid_to_record(activity_type_xmlid)
            if not activity_type:
                # Fallback to To-Do
                activity_type = env.ref(
                    "mail.mail_activity_data_todo", raise_if_not_found=False
                )
            if not activity_type:
                errors.append(
                    f"Row {i}: Activity type not found: {activity_type_xmlid}"
                )
                continue

            # Resolve user (optional - defaults to current user)
            user_xmlid = row.get("user_id/id", "").strip()
            user = xmlid_to_record(user_xmlid) if user_xmlid else env.user
            if not user:
                user = env.user

            # Build values
            vals = {
                "res_model": row.get("res_model", "project.task").strip(),
                "res_id": target.id,
                "activity_type_id": activity_type.id,
                "summary": row.get("summary", "").strip() or False,
                "note": row.get("note", "").strip() or False,
                "date_deadline": row.get("date_deadline", "").strip(),
                "user_id": user.id,
            }

            if DRY_RUN:
                print(f"Row {i}: DRY RUN - would create: {vals}")
            else:
                # Create activity
                activity = Activity.create(vals)

                # Create external ID reference
                module, name = (
                    activity_xmlid.split(".", 1)
                    if "." in activity_xmlid
                    else ("__import__", activity_xmlid)
                )
                IrModelData.create(
                    {
                        "name": name,
                        "module": module,
                        "model": "mail.activity",
                        "res_id": activity.id,
                        "noupdate": True,
                    }
                )

                print(
                    f"Row {i}: CREATED - {activity_xmlid} -> mail.activity ID {activity.id}"
                )
                created += 1

        except Exception as e:
            errors.append(f"Row {i}: {str(e)}")

    return created, errors


# Run import
created, errors = import_activities(ACTIVITY_CSV)

print()
print("=" * 60)
print("IMPORT SUMMARY")
print("=" * 60)
print(f"Created: {created}")
print(f"Errors: {len(errors)}")

if errors:
    print()
    print("ERRORS:")
    for err in errors:
        print(f"  - {err}")

print()
print("Done.")
