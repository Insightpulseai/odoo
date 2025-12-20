#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Review project 30 tasks as they appear in the UI"""

import odoo
from odoo import api, SUPERUSER_ID

odoo.tools.config.parse_config(["-d", "production"])
registry = odoo.registry("production")

with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})

    print("="*80)
    print("PROJECT 30 TASK REVIEW - UI DATA SIMULATION")
    print("="*80)

    # Get the project
    project = env["project.project"].browse(30)
    print(f"\nProject: {project.name}")
    print(f"Project ID: {project.id}")

    # Get all tasks (what the UI shows by default)
    all_tasks = env["project.task"].search([
        ("project_id", "=", 30)
    ], order="create_date desc")

    print(f"\nTotal Tasks: {len(all_tasks)}")

    # Group by status
    by_status = {}
    for task in all_tasks:
        stage = task.stage_id.name if task.stage_id else "No Stage"
        by_status[stage] = by_status.get(stage, 0) + 1

    print(f"\nTasks by Stage:")
    for stage, count in sorted(by_status.items()):
        print(f"  {stage}: {count}")

    # Check is_finance_ppm distribution
    finance_ppm_tasks = all_tasks.filtered(lambda t: t.is_finance_ppm)
    print(f"\nFinance PPM Tasks: {len(finance_ppm_tasks)} ({len(finance_ppm_tasks)/len(all_tasks)*100:.1f}%)")

    # Sample of tasks that would appear in list view
    print(f"\n" + "="*80)
    print("SAMPLE TASKS (First 10 - as they appear in UI list view)")
    print("="*80)

    for i, task in enumerate(all_tasks[:10], 1):
        print(f"\n{i}. Task ID: {task.id}")
        print(f"   Name: {task.name}")
        print(f"   Stage: {task.stage_id.name if task.stage_id else 'None'}")
        assigned = ", ".join(task.user_ids.mapped('name')) if task.user_ids else "Unassigned"
        print(f"   Assigned: {assigned}")
        print(f"   Date Deadline: {task.date_deadline or 'None'}")
        ext_key = task.x_external_key or "None"
        if ext_key != "None" and len(ext_key) > 50:
            ext_key = ext_key[:50] + "..."
        print(f"   External Key: {ext_key}")
        print(f"   is_finance_ppm: {task.is_finance_ppm}")

    # Check what Generated Tasks menu would show
    print(f"\n" + "="*80)
    print("GENERATED TASKS MENU VIEW")
    print("="*80)

    generated_tasks = env["project.task"].search([
        ("x_external_key", "!=", False),
        ("project_id", "=", 30)
    ])

    print(f"Tasks with x_external_key: {len(generated_tasks)}")
    print(f"\nBreakdown by Cycle Type:")

    cycle_types = {}
    for task in generated_tasks:
        if task.x_external_key:
            cycle = task.x_external_key.split("|")[0]
            cycle_types[cycle] = cycle_types.get(cycle, 0) + 1

    for cycle, count in sorted(cycle_types.items()):
        print(f"  {cycle}: {count} tasks")

    # Breakdown by period
    print(f"\nBreakdown by Period:")
    periods = {}
    for task in generated_tasks:
        if task.x_external_key:
            parts = task.x_external_key.split("|")
            if len(parts) >= 2:
                period = parts[1]
                periods[period] = periods.get(period, 0) + 1

    for period, count in sorted(periods.items()):
        print(f"  {period}: {count} tasks")

    print(f"\n" + "="*80)
    print("UI VISIBILITY SUMMARY")
    print("="*80)
    print(f"\nAt https://erp.insightpulseai.net/odoo/project/30/tasks you should see:")
    print(f"  • Total: {len(all_tasks)} tasks")
    print(f"  • All tasks have is_finance_ppm=True: {len(finance_ppm_tasks) == len(all_tasks)}")
    print(f"\nIn the 'Generated Tasks' menu you should see:")
    print(f"  • {len(generated_tasks)} tasks (all generated from seed JSON)")
    print(f"  • 99 month-end closing tasks (Oct/Nov/Dec 2025)")
    print(f"  • 36 tax filing tasks (monthly + quarterly)")
    print("="*80)
