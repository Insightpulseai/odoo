import csv
import sys
import json
from datetime import datetime

# =============================================================================
# Odoo CE Feature Inventory Introspector
# =============================================================================
# Exports:
# 1. Modules Inventory (installed)
# 2. Project Feature Flags
# 3. Backlog Summary
# =============================================================================


def export_csv(filename, headers, rows):
    path = f"/tmp/{filename}"
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    print(f"Exported {len(rows)} rows to {path}")


def main(env):
    print(f"Starting feature inventory introspection at {datetime.now()}")

    # 1. Modules Inventory
    modules = env["ir.module.module"].search(
        [("state", "=", "installed")], order="name"
    )
    module_rows = [
        [m.name, m.state, m.latest_version, m.category_id.name or ""] for m in modules
    ]
    export_csv(
        "feature_inventory.modules.csv",
        ["module", "state", "version", "category"],
        module_rows,
    )

    # 2. Project Feature Flags
    projects = env["project.project"].search([], order="name")
    flag_rows = []

    # Introspect available fields dynamically to be safe
    model_fields = env["project.project"].fields_get().keys()

    for p in projects:
        row = [
            p.name,
            p.allow_subtasks if "allow_subtasks" in model_fields else "N/A",
            (
                p.allow_recurring_tasks
                if "allow_recurring_tasks" in model_fields
                else "N/A"
            ),
            (
                p.allow_task_dependencies
                if "allow_task_dependencies" in model_fields
                else "N/A"
            ),
            p.allow_milestones if "allow_milestones" in model_fields else "N/A",
            p.allow_timesheets if "allow_timesheets" in model_fields else "N/A",
            p.privacy_visibility,
        ]
        flag_rows.append(row)

    export_csv(
        "feature_flags.projects.csv",
        [
            "project_name",
            "subtasks",
            "recurring",
            "deps",
            "milestones",
            "timesheets",
            "visibility",
        ],
        flag_rows,
    )

    # 3. Backlog Summary
    # Logic: count tasks in 'Backlog' stage + blocked tasks
    # Determine backlog stage ID(s)
    backlog_stages = env["project.task.type"].search([("name", "ilike", "Backlog")])
    backlog_stage_ids = backlog_stages.ids

    summary_rows = []
    for p in projects:
        domain = [("project_id", "=", p.id)]
        total = env["project.task"].search_count(domain)

        # Backlog count
        backlog_count = 0
        if backlog_stage_ids:
            backlog_count = env["project.task"].search_count(
                domain + [("stage_id", "in", backlog_stage_ids)]
            )

        # Blocked count
        blocked_count = env["project.task"].search_count(
            domain + [("kanban_state", "=", "blocked")]
        )

        # Overdue count
        overdue_count = env["project.task"].search_count(
            domain
            + [
                ("date_deadline", "<", datetime.now().date()),
                ("state", "!=", "1_done"),  # Assuming state usage, or stage fold
            ]
        )

        summary_rows.append(
            [p.name, total, backlog_count, blocked_count, overdue_count]
        )

    export_csv(
        "backlog.summary.csv",
        [
            "project_name",
            "total_tasks",
            "backlog_count",
            "blocked_count",
            "overdue_count",
        ],
        summary_rows,
    )

    # JSON Summary for CI drift check
    summary = {
        "timestamp": str(datetime.now()),
        "modules_installed": len(modules),
        "projects_active": len(projects),
        "backlog_stages_found": [s.name for s in backlog_stages],
    }
    with open("/tmp/feature_inventory.json", "w") as f:
        json.dump(summary, f, indent=2)
    print("Exported summary to /tmp/feature_inventory.json")


if __name__ == "__main__":
    # This script is meant to be run via odoo shell
    if "env" in globals():
        main(env)
