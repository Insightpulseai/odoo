import csv
import json
import os
import sys
from datetime import date, datetime


def serialize_date(obj):
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    return str(obj)


def get_xml_id(env, record):
    """Attempt to find XML ID for a record."""
    try:
        domain = [("model", "=", record._name), ("res_id", "=", record.id)]
        data = env["ir.model.data"].search(domain, limit=1)
        if data:
            return f"{data.module}.{data.name}"
    except Exception:
        pass
    return ""


def export_todo_seed(env):
    output_dir = "/tmp/odoo_seed_export"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"\n--- SEED EXPORT START ---\n")

    # 1. RESOLVE ACTION 334
    try:
        action = env["ir.actions.act_window"].browse(334)
        model_name = action.res_model
        print(f"ACTION 334 RESOLVED: Model={model_name} Name='{action.name}'")
    except Exception as e:
        print(f"ERROR resolving action 334: {e}")
        # Fallback to project.task as derived from context "To Do"
        model_name = "project.task"
        print(f"FALLBACK: Using Model={model_name}")

    if model_name != "project.task":
        print(f"WARNING: Unexpected model {model_name}. Proceeding with caution.")

    Task = env[model_name]
    Project = env["project.project"]

    # 2. RESOLVE PROJECTS
    target_projects = [
        "BIR Tax Filing",
        "Month-End Close Template",
        "Month-end closing",
    ]

    project_map = {}
    for name in target_projects:
        # Try exact match
        p = Project.search([("name", "=", name)], limit=1)
        if not p:
            # Try case insensitive
            p = Project.search([("name", "ilike", name)], limit=1)

        if p:
            project_map[p.id] = {"name": name, "record": p, "expected_count": 0}
            print(f"FOUND PROJECT: '{p.name}' (ID {p.id}) matches '{name}'")
        else:
            print(f"MISSING PROJECT: Could not find project '{name}'")

    # Assign expected counts manually for verification
    # "BIR Tax Filing" (51 tasks)
    # "Month-End Close Template" (26 tasks)
    # "Month-end closing" (37 tasks)

    # We need to map the found IDs to these expectations.
    # Since we searched by name, we iterate our targets.
    verification_counts = {
        "BIR Tax Filing": 51,
        "Month-End Close Template": 26,
        "Month-end closing": 37,
    }

    # 3. EXPORT TASKS
    project_ids = list(project_map.keys())
    domain = [
        ("project_id", "in", project_ids),
        ("active", "in", [True, False]),
    ]  # Include archived? User said "COMPLETE task seed data", implying all.

    # Specific filter? User didn't specify active only, but usually seed data implies current template structure.
    # We will check active=True first, if counts match, great. If not, check active=False.

    tasks = Task.search(domain)
    print(f"TOTAL TASKS FOUND: {len(tasks)}")

    # Data collection
    all_tasks_data = []

    # Reference sets
    ref_stages = set()
    ref_tags = set()
    ref_users = set()
    ref_projects = set()

    # Pre-fetch fields to avoid N+1
    # Fields to export:
    # name, project_id, stage_id, description, priority, user_ids, date_deadline, tag_ids, parent_id, sequence

    for t in tasks:
        p_name = project_map[t.project_id.id]["name"]

        # Update actual count (naive) - doing precise verification later

        task_data = {
            "id": t.id,
            "xml_id": get_xml_id(env, t),
            "name": t.name,
            "project_id": t.project_id.id,
            "project_name": t.project_id.name,
            "stage_id": t.stage_id.id if t.stage_id else "",
            "stage_name": t.stage_id.name if t.stage_id else "",
            "active": t.active,
            "description": t.description or "",  # HTML field
            "priority": t.priority,
            "sequence": t.sequence,
            "date_deadline": t.date_deadline,
            "parent_id": t.parent_id.id if t.parent_id else "",
            "parent_name": t.parent_id.name if t.parent_id else "",
            "company_id": t.company_id.id,
        }

        # Relations
        users = t.user_ids
        task_data["user_logins"] = ",".join([u.login for u in users])
        for u in users:
            ref_users.add(u)

        tags = t.tag_ids
        task_data["tag_names"] = ",".join([tag.name for tag in tags])
        for tag in tags:
            ref_tags.add(tag)

        if t.stage_id:
            ref_stages.add(t.stage_id)
        if t.project_id:
            ref_projects.add(t.project_id)

        all_tasks_data.append(task_data)

    # 4. WRITE CSVs

    # Tasks
    tasks_file = os.path.join(output_dir, "tasks.csv")
    fieldnames = [
        "id",
        "xml_id",
        "name",
        "project_id",
        "project_name",
        "stage_id",
        "stage_name",
        "active",
        "description",
        "priority",
        "sequence",
        "date_deadline",
        "parent_id",
        "parent_name",
        "company_id",
        "user_logins",
        "tag_names",
    ]

    with open(tasks_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_tasks_data)

    # Projects
    projects_file = os.path.join(output_dir, "projects.csv")
    with open(projects_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "xml_id", "name", "active"])
        for p in ref_projects:
            writer.writerow([p.id, get_xml_id(env, p), p.name, p.active])

    # Stages
    stages_file = os.path.join(output_dir, "stages.csv")
    with open(stages_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "xml_id", "name", "sequence", "project_ids/name"])
        for s in ref_stages:
            writer.writerow(
                [
                    s.id,
                    get_xml_id(env, s),
                    s.name,
                    s.sequence,
                    ",".join([p.name for p in s.project_ids]),
                ]
            )

    # Tags
    tags_file = os.path.join(output_dir, "tags.csv")
    with open(tags_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "xml_id", "name", "color"])
        for tag in ref_tags:
            writer.writerow([tag.id, get_xml_id(env, tag), tag.name, tag.color])

    # Users
    users_file = os.path.join(output_dir, "users.csv")
    with open(users_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "xml_id", "name", "login"])
        for u in ref_users:
            writer.writerow([u.id, get_xml_id(env, u), u.name, u.login])

    # 5. VERIFICATION
    print("\n--- VERIFICATION REPORT ---")

    actual_counts = {}
    for task in all_tasks_data:
        p_name = task["project_name"]
        actual_counts[p_name] = actual_counts.get(p_name, 0) + 1

    print(f"{'PROJECT':<30} | {'EXPECTED':<10} | {'ACTUAL':<10} | {'STATUS'}")
    print("-" * 65)

    total_expected = 0
    total_actual = len(all_tasks_data)

    # We iterate based on the target map to match names properly
    for target_name, expected in verification_counts.items():
        # Find connection to real project name (might case differ)
        # We search our project_map values
        real_name = None
        for pid, pdata in project_map.items():
            if pdata["name"] == target_name:  # This was the loop key above
                real_name = pdata["record"].name
                break

        count = actual_counts.get(real_name, 0)
        status = "PASS" if count == expected else "FAIL"
        print(f"{target_name:<30} | {expected:<10} | {count:<10} | {status}")
        total_expected += expected

    print("-" * 65)
    print(
        f"{'TOTAL':<30} | {total_expected:<10} | {total_actual:<10} | {'PASS' if total_expected == total_actual else 'FAIL'}"
    )

    print(f"\nArtifacts generated in container: {output_dir}")
    print("DONE")


if __name__ == "__main__":
    if "env" in globals():
        export_todo_seed(env)
    else:
        print("This script must be run within Odoo shell")
