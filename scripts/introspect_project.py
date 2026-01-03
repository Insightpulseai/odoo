#!/usr/bin/env python3
"""
Odoo 18 CE Project Introspection Script (READ-ONLY)
Runs inside odoo-bin shell to extract Project schema information.

Usage:
  docker exec -i odoo-core odoo-bin shell -d odoo_core --no-http < scripts/introspect_project.py
"""

import json
import sys

# ============================================================================
# A) CONFIRM INSTALLED MODULES
# ============================================================================
print("\n" + "="*80)
print("A) INSTALLED MODULES RELEVANT TO PROJECT FEATURES")
print("="*80)

module_names = [
    'project', 'project_todo', 'project_timesheet_holidays',
    'hr', 'hr_timesheet', 'hr_holidays', 'hr_contract', 'hr_skills',
    'calendar', 'mail', 'rating', 'resource',
    'analytic', 'account_analytic_default',
    'sale_timesheet', 'timesheet_grid',
]

IrModule = env['ir.module.module']
modules = IrModule.search([('name', 'in', module_names)])

print(f"\n{'Module Name':<40} {'State':<15}")
print("-"*55)
for m in modules.sorted(key=lambda x: x.name):
    print(f"{m.name:<40} {m.state:<15}")

# Check for any project-related modules
project_modules = IrModule.search([('name', 'like', 'project%'), ('state', '=', 'installed')])
print(f"\nAll installed project* modules:")
for m in project_modules.sorted(key=lambda x: x.name):
    print(f"  - {m.name}")

# ============================================================================
# B) INTROSPECT PROJECT.TASK FIELDS
# ============================================================================
print("\n" + "="*80)
print("B) PROJECT.TASK FIELDS INTROSPECTION")
print("="*80)

task_fields_to_check = [
    'stage_id', 'project_id', 'milestone_id', 'parent_id',
    'depend_on_ids', 'dependent_ids',
    'recurrence_id', 'recurring_task',
    'repeat_interval', 'repeat_unit', 'repeat_type',
    'repeat_until', 'repeat_until_date', 'repeat_number',
    'date_deadline', 'user_ids', 'partner_id', 'description',
    'child_ids', 'subtask_count', 'tag_ids', 'priority',
    'date_assign', 'date_end', 'date_last_stage_update',
    'kanban_state', 'color', 'sequence', 'active',
    'company_id', 'planned_hours', 'remaining_hours',
    'effective_hours', 'total_hours_spent', 'progress',
    'timesheet_ids', 'analytic_account_id',
    'activity_ids', 'message_ids',
]

IrModelFields = env['ir.model.fields']
task_fields = IrModelFields.search([
    ('model', '=', 'project.task'),
    ('name', 'in', task_fields_to_check)
])

print(f"\n{'Field Name':<30} {'Type':<15} {'Relation':<30} {'Req':<5} {'Store':<6}")
print("-"*90)

task_field_info = {}
for f in task_fields.sorted(key=lambda x: x.name):
    rel = f.relation or ''
    req = 'Yes' if f.required else 'No'
    store = 'Yes' if f.store else 'No'
    print(f"{f.name:<30} {f.ttype:<15} {rel:<30} {req:<5} {store:<6}")
    task_field_info[f.name] = {
        'ttype': f.ttype,
        'relation': f.relation,
        'required': f.required,
        'store': f.store,
    }

# List fields NOT found
found_fields = set(f.name for f in task_fields)
missing_fields = set(task_fields_to_check) - found_fields
if missing_fields:
    print(f"\nFields NOT found on project.task: {', '.join(sorted(missing_fields))}")

# ============================================================================
# C) INTROSPECT PROJECT.PROJECT FIELDS
# ============================================================================
print("\n" + "="*80)
print("C) PROJECT.PROJECT FIELDS INTROSPECTION")
print("="*80)

project_fields_to_check = [
    'privacy_visibility', 'partner_id', 'company_id',
    'user_id', 'date_start', 'date', 'stage_id',
    'allow_subtasks', 'allow_recurring_tasks', 'allow_task_dependencies',
    'allow_milestones', 'allow_timesheets',
    'analytic_account_id', 'label_tasks',
    'task_ids', 'task_count', 'type_ids',
    'milestone_ids', 'milestone_count',
    'rating_active', 'rating_status',
    'sequence', 'active', 'color', 'tag_ids',
]

project_fields = IrModelFields.search([
    ('model', '=', 'project.project'),
    ('name', 'in', project_fields_to_check)
])

print(f"\n{'Field Name':<35} {'Type':<15} {'Relation':<30} {'Req':<5} {'Store':<6}")
print("-"*95)

project_field_info = {}
for f in project_fields.sorted(key=lambda x: x.name):
    rel = f.relation or ''
    req = 'Yes' if f.required else 'No'
    store = 'Yes' if f.store else 'No'
    print(f"{f.name:<35} {f.ttype:<15} {rel:<30} {req:<5} {store:<6}")
    project_field_info[f.name] = {
        'ttype': f.ttype,
        'relation': f.relation,
        'required': f.required,
        'store': f.store,
    }

# List fields NOT found
found_project_fields = set(f.name for f in project_fields)
missing_project_fields = set(project_fields_to_check) - found_project_fields
if missing_project_fields:
    print(f"\nFields NOT found on project.project: {', '.join(sorted(missing_project_fields))}")

# ============================================================================
# D) DETECT CANDIDATE MODELS FOR DEPENDENCIES/RECURRENCE/MILESTONES
# ============================================================================
print("\n" + "="*80)
print("D) MODEL EXISTENCE CHECK")
print("="*80)

candidate_models = [
    'project.milestone',
    'project.task.dependency',
    'project.task.recurrence',
    'project.task.recurrence.rule',
    'project.task.type',
    'project.tags',
    'project.project.stage',
]

IrModel = env['ir.model']
model_existence = {}

print(f"\n{'Model':<35} {'Exists':<10}")
print("-"*45)

for model_name in candidate_models:
    exists = bool(IrModel.search([('model', '=', model_name)], limit=1))
    model_existence[model_name] = exists
    print(f"{model_name:<35} {'YES' if exists else 'NO':<10}")

# For existing models, list their fields
print("\n--- Fields for existing models ---")
for model_name, exists in model_existence.items():
    if exists:
        print(f"\n{model_name}:")
        fields = IrModelFields.search([('model', '=', model_name), ('store', '=', True)])
        for f in fields.sorted(key=lambda x: x.name)[:30]:  # Limit to 30 fields
            rel = f.relation or ''
            print(f"  {f.name:<25} {f.ttype:<15} {rel:<25}")

# ============================================================================
# E) GENERATE CSV IMPORT HEADERS
# ============================================================================
print("\n" + "="*80)
print("E) SUGGESTED CSV IMPORT HEADERS")
print("="*80)

def get_import_header(field_name, field_info):
    """Convert field to Odoo import header format."""
    ttype = field_info.get('ttype', '')
    if ttype in ('many2one',):
        return f"{field_name}/id"
    elif ttype in ('many2many', 'one2many'):
        return f"{field_name}/id"
    return field_name

# project.project headers
print("\n--- project.project ---")
project_import_fields = [
    'id', 'name', 'active', 'sequence', 'partner_id', 'user_id', 'company_id',
    'date_start', 'date', 'privacy_visibility', 'analytic_account_id',
    'allow_subtasks', 'allow_recurring_tasks', 'allow_task_dependencies', 'allow_milestones',
    'label_tasks', 'color', 'tag_ids',
]
project_headers = []
for fn in project_import_fields:
    if fn in project_field_info:
        project_headers.append(get_import_header(fn, project_field_info[fn]))
    elif fn == 'id':
        project_headers.append('id')
    elif fn == 'name':
        project_headers.append('name')
print(','.join(project_headers))

# project.task headers
print("\n--- project.task ---")
task_import_fields = [
    'id', 'name', 'active', 'sequence', 'project_id', 'stage_id', 'user_ids',
    'partner_id', 'parent_id', 'milestone_id', 'priority', 'kanban_state',
    'date_deadline', 'date_assign', 'date_end', 'planned_hours',
    'depend_on_ids', 'recurring_task', 'recurrence_id',
    'repeat_interval', 'repeat_unit', 'repeat_type', 'repeat_until_date', 'repeat_number',
    'company_id', 'tag_ids', 'description', 'color',
]
task_headers = []
for fn in task_import_fields:
    if fn in task_field_info:
        task_headers.append(get_import_header(fn, task_field_info[fn]))
    elif fn == 'id':
        task_headers.append('id')
    elif fn in ('name', 'description'):
        task_headers.append(fn)
print(','.join(task_headers))

# project.task.type headers
print("\n--- project.task.type ---")
task_type_fields = IrModelFields.search([
    ('model', '=', 'project.task.type'),
    ('store', '=', True)
])
task_type_headers = ['id', 'name', 'sequence', 'fold', 'project_ids/id', 'description']
print(','.join(task_type_headers))

# project.milestone headers (if exists)
if model_existence.get('project.milestone'):
    print("\n--- project.milestone ---")
    milestone_headers = ['id', 'name', 'project_id/id', 'deadline', 'is_reached', 'reached_date']
    print(','.join(milestone_headers))

# mail.activity headers
print("\n--- mail.activity ---")
activity_headers = [
    'id', 'res_model', 'res_id', 'res_name', 'activity_type_id/id',
    'summary', 'note', 'date_deadline', 'user_id/id', 'state'
]
print(','.join(activity_headers))

# ============================================================================
# F) GENERATE DBML AND JSON SCHEMA
# ============================================================================
print("\n" + "="*80)
print("F) GENERATING DBML ERD AND JSON SCHEMA")
print("="*80)

# Models to include in DBML
models_for_schema = [
    'project.project', 'project.task', 'project.task.type', 'project.tags',
    'project.milestone', 'project.task.recurrence',
    'hr.employee', 'hr.department', 'hr.job',
    'calendar.event', 'calendar.attendee',
    'resource.resource', 'resource.calendar', 'resource.calendar.attendance',
    'mail.activity', 'mail.activity.type', 'mail.message',
    'rating.rating',
    'account.analytic.account', 'account.analytic.line',
    'res.users', 'res.partner', 'res.company',
]

# Filter to only existing models
existing_models = []
for model_name in models_for_schema:
    if IrModel.search([('model', '=', model_name)], limit=1):
        existing_models.append(model_name)

print(f"Found {len(existing_models)} models for schema export")

# Build DBML content
dbml_lines = ['// Odoo 18 CE Project ERD - Auto-generated', '// READ-ONLY INTROSPECTION', '']

json_schema = {}

for model_name in existing_models:
    table_name = model_name.replace('.', '_')

    # Get all stored fields for this model
    fields = IrModelFields.search([
        ('model', '=', model_name),
        ('store', '=', True)
    ])

    if not fields:
        continue

    # DBML table
    dbml_lines.append(f'Table {table_name} {{')

    # JSON schema for model
    json_schema[model_name] = {'fields': {}}

    for f in fields.sorted(key=lambda x: x.name):
        # Map Odoo types to SQL types for DBML
        type_map = {
            'integer': 'integer',
            'float': 'float',
            'monetary': 'decimal',
            'boolean': 'boolean',
            'char': 'varchar',
            'text': 'text',
            'html': 'text',
            'date': 'date',
            'datetime': 'timestamp',
            'binary': 'bytea',
            'selection': 'varchar',
            'many2one': 'integer',
            'many2many': 'integer[]',
            'one2many': 'integer[]',
        }

        sql_type = type_map.get(f.ttype, 'varchar')

        # Build DBML field line
        notes = []
        if f.required:
            notes.append('not null')
        if f.name == 'id':
            notes.append('pk')
        if f.relation:
            notes.append(f'ref: > {f.relation.replace(".", "_")}.id')

        note_str = f' [{", ".join(notes)}]' if notes else ''
        dbml_lines.append(f'  {f.name} {sql_type}{note_str}')

        # JSON schema field
        json_schema[model_name]['fields'][f.name] = {
            'type': f.ttype,
            'relation': f.relation or None,
            'required': f.required,
            'store': f.store,
            'readonly': f.readonly,
            'selection': f.selection if f.ttype == 'selection' else None,
        }

    dbml_lines.append('}')
    dbml_lines.append('')

dbml_content = '\n'.join(dbml_lines)

# Save to files
with open('/tmp/odoo_project_full.dbml', 'w') as f:
    f.write(dbml_content)
print("Saved: /tmp/odoo_project_full.dbml")

with open('/tmp/odoo_project_full.schema.json', 'w') as f:
    json.dump(json_schema, f, indent=2, default=str)
print("Saved: /tmp/odoo_project_full.schema.json")

# Save import headers
import_headers_content = """# Odoo 18 CE Import Headers - Auto-generated

## project.project
{project_headers}

## project.task
{task_headers}

## project.task.type
{task_type_headers}

## project.milestone (if enabled)
{milestone_headers}

## mail.activity
{activity_headers}

## IMPORT ORDER (recommended):
1. res.company (if multi-company)
2. res.partner (customers/contacts)
3. res.users (users must exist for assignments)
4. project.task.type (stages)
5. project.project (with toggle flags)
6. project.milestone (if allow_milestones=True)
7. project.task (main tasks, parent_id=False first)
8. project.task (subtasks with parent_id)
9. project.task (update depend_on_ids for dependencies)
10. mail.activity (activities linked to tasks)
""".format(
    project_headers=','.join(project_headers),
    task_headers=','.join(task_headers),
    task_type_headers=','.join(task_type_headers),
    milestone_headers=','.join(milestone_headers) if model_existence.get('project.milestone') else 'N/A - model not found',
    activity_headers=','.join(activity_headers),
)

with open('/tmp/odoo_import_headers.txt', 'w') as f:
    f.write(import_headers_content)
print("Saved: /tmp/odoo_import_headers.txt")

# ============================================================================
# G) SUMMARY
# ============================================================================
print("\n" + "="*80)
print("G) SUMMARY")
print("="*80)

print("""
ARTIFACTS SAVED:
  /tmp/odoo_project_full.dbml       - DBML ERD for database visualization
  /tmp/odoo_project_full.schema.json - Full JSON schema (ORM-friendly)
  /tmp/odoo_import_headers.txt      - CSV import headers with order

KEY FINDINGS:
""")

# Summarize toggle fields
toggle_fields = ['allow_subtasks', 'allow_recurring_tasks', 'allow_task_dependencies', 'allow_milestones']
print("Project Toggle Fields (project.project):")
for tf in toggle_fields:
    status = "FOUND" if tf in project_field_info else "NOT FOUND"
    print(f"  - {tf}: {status}")

print("\nRecurrence Fields (project.task):")
recurrence_fields = ['recurring_task', 'recurrence_id', 'repeat_interval', 'repeat_unit', 'repeat_type']
for rf in recurrence_fields:
    status = "FOUND" if rf in task_field_info else "NOT FOUND"
    print(f"  - {rf}: {status}")

print("\nDependency Fields (project.task):")
dep_fields = ['depend_on_ids', 'dependent_ids']
for df in dep_fields:
    status = "FOUND" if df in task_field_info else "NOT FOUND"
    print(f"  - {df}: {status}")

print("\nMilestone:")
print(f"  - project.milestone model: {'FOUND' if model_existence.get('project.milestone') else 'NOT FOUND'}")
print(f"  - milestone_id on project.task: {'FOUND' if 'milestone_id' in task_field_info else 'NOT FOUND'}")

print("\n" + "="*80)
print("INTROSPECTION COMPLETE")
print("="*80)

# Exit cleanly
sys.exit(0)
