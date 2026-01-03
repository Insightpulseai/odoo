#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Post-Import Verification Script (READ-ONLY)
Verifies counts, dependencies, recurrence, and milestones after import.

Usage:
  docker exec -i odoo-core odoo shell -d odoo_core --no-http < scripts/import/verify_import.py
"""

import sys

print("=" * 70)
print("ODOO 18 CE PROJECT IMPORT VERIFICATION")
print("=" * 70)
print()

# =============================================================================
# 1. RECORD COUNTS
# =============================================================================
print("1. RECORD COUNTS")
print("-" * 50)

counts = {}
models_to_check = [
    ("project.project", "Projects"),
    ("project.task", "Tasks"),
    ("project.task.type", "Stages"),
    ("project.milestone", "Milestones"),
    ("project.task.recurrence", "Recurrence Rules"),
    ("mail.activity", "Activities"),
]

for model, label in models_to_check:
    try:
        count = env[model].search_count([])
        counts[model] = count
        print(f"  {label:<25} {count:>6}")
    except Exception as e:
        print(f"  {label:<25} ERROR: {e}")

# =============================================================================
# 2. IPAI SAMPLE RECORDS CHECK
# =============================================================================
print()
print("2. IPAI SAMPLE RECORDS (External IDs)")
print("-" * 50)

sample_xmlids = [
    "ipai_project.program_master",
    "ipai_project.project_q1_close",
    "ipai_project.ms_jan_close",
    "ipai_project.task_jan_prep",
    "ipai_project.task_weekly_status",
    "ipai_project.stage_in_progress",
]

for xmlid in sample_xmlids:
    try:
        rec = env.ref(xmlid, raise_if_not_found=False)
        if rec:
            print(f"  {xmlid:<45} OK (ID: {rec.id})")
        else:
            print(f"  {xmlid:<45} NOT FOUND")
    except Exception as e:
        print(f"  {xmlid:<45} ERROR: {e}")

# =============================================================================
# 3. DEPENDENCIES CHECK
# =============================================================================
print()
print("3. TASK DEPENDENCIES")
print("-" * 50)

# Check specific dependency chains
dep_checks = [
    ("ipai_project.task_jan_review", "ipai_project.task_jan_prep"),
    ("ipai_project.task_jan_approve", "ipai_project.task_jan_review"),
    ("ipai_project.task_bir_1601c_file", "ipai_project.task_bir_1601c_prep"),
]

dep_pass = 0
dep_fail = 0

for task_xmlid, predecessor_xmlid in dep_checks:
    task = env.ref(task_xmlid, raise_if_not_found=False)
    predecessor = env.ref(predecessor_xmlid, raise_if_not_found=False)

    if not task:
        print(f"  {task_xmlid}: SKIP (task not found)")
        continue
    if not predecessor:
        print(f"  {task_xmlid}: SKIP (predecessor not found)")
        continue

    if hasattr(task, 'depend_on_ids') and predecessor in task.depend_on_ids:
        print(f"  {task.name:<35} -> depends on '{predecessor.name}' OK")
        dep_pass += 1
    else:
        print(f"  {task.name:<35} -> MISSING dependency on '{predecessor.name}'")
        dep_fail += 1

print(f"\n  Dependencies: {dep_pass} passed, {dep_fail} failed")

# =============================================================================
# 4. RECURRENCE CHECK
# =============================================================================
print()
print("4. TASK RECURRENCE")
print("-" * 50)

recurring_task = env.ref("ipai_project.task_weekly_status", raise_if_not_found=False)

if recurring_task:
    print(f"  Task: {recurring_task.name}")
    print(f"  recurring_task: {getattr(recurring_task, 'recurring_task', 'N/A')}")
    print(f"  repeat_interval: {getattr(recurring_task, 'repeat_interval', 'N/A')}")
    print(f"  repeat_unit: {getattr(recurring_task, 'repeat_unit', 'N/A')}")
    print(f"  repeat_type: {getattr(recurring_task, 'repeat_type', 'N/A')}")
    print(f"  recurrence_id: {getattr(recurring_task, 'recurrence_id', 'N/A')}")

    is_recurring = getattr(recurring_task, 'recurring_task', False)
    if is_recurring:
        print(f"\n  Recurrence: CONFIGURED")
    else:
        print(f"\n  Recurrence: NOT SET")
else:
    print("  Recurring task not found: ipai_project.task_weekly_status")

# =============================================================================
# 5. MILESTONES CHECK
# =============================================================================
print()
print("5. MILESTONE LINKAGE")
print("-" * 50)

milestone_checks = [
    ("ipai_project.task_jan_approve", "ipai_project.ms_jan_close"),
    ("ipai_project.task_bir_1601c_file", "ipai_project.ms_q1_bir_1601c"),
]

ms_pass = 0
ms_fail = 0

for task_xmlid, milestone_xmlid in milestone_checks:
    task = env.ref(task_xmlid, raise_if_not_found=False)
    milestone = env.ref(milestone_xmlid, raise_if_not_found=False)

    if not task:
        print(f"  {task_xmlid}: SKIP (task not found)")
        continue
    if not milestone:
        print(f"  {task_xmlid}: SKIP (milestone not found)")
        continue

    if hasattr(task, 'milestone_id') and task.milestone_id.id == milestone.id:
        print(f"  {task.name:<35} -> milestone '{milestone.name}' OK")
        ms_pass += 1
    else:
        actual_ms = task.milestone_id.name if hasattr(task, 'milestone_id') and task.milestone_id else "None"
        print(f"  {task.name:<35} -> EXPECTED '{milestone.name}', GOT '{actual_ms}'")
        ms_fail += 1

print(f"\n  Milestones: {ms_pass} passed, {ms_fail} failed")

# =============================================================================
# 6. PROJECT TOGGLES CHECK
# =============================================================================
print()
print("6. PROJECT FEATURE TOGGLES")
print("-" * 50)

project = env.ref("ipai_project.project_q1_close", raise_if_not_found=False)

if project:
    print(f"  Project: {project.name}")
    toggles = [
        "allow_subtasks",
        "allow_recurring_tasks",
        "allow_task_dependencies",
        "allow_milestones",
        "allow_timesheets",
    ]
    for toggle in toggles:
        val = getattr(project, toggle, "N/A")
        status = "ON" if val else "OFF"
        print(f"    {toggle:<30} {status}")
else:
    print("  Project not found: ipai_project.project_q1_close")

# =============================================================================
# 7. IPAI CLARITY FIELDS CHECK
# =============================================================================
print()
print("7. IPAI CLARITY PPM FIELDS")
print("-" * 50)

if project:
    clarity_fields = [
        ("clarity_id", "Clarity ID"),
        ("health_status", "Health Status"),
        ("is_program", "Is Program"),
        ("program_type", "Program Type"),
        ("baseline_start", "Baseline Start"),
        ("baseline_finish", "Baseline Finish"),
    ]
    for field, label in clarity_fields:
        val = getattr(project, field, "N/A")
        print(f"    {label:<25} {val}")
else:
    print("  Project not found")

# =============================================================================
# SUMMARY
# =============================================================================
print()
print("=" * 70)
print("VERIFICATION SUMMARY")
print("=" * 70)

total_pass = dep_pass + ms_pass
total_fail = dep_fail + ms_fail

print(f"  Total checks passed: {total_pass}")
print(f"  Total checks failed: {total_fail}")

if total_fail == 0:
    print()
    print("  STATUS: ALL CHECKS PASSED")
else:
    print()
    print("  STATUS: SOME CHECKS FAILED - Review above for details")

print()
print("Done.")
