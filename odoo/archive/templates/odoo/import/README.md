# Odoo Month-end Close + Tax Filing Import (CE)

## Policy

**Commit templates + scripts only. Never commit real-filled CSV/XLSX files.**

Real import data may contain sensitive information (emails, client names, dates) and should be kept out of version control.

## Overview

This import system generates and imports Month-end Closing Tasks and Tax Filing schedules into Odoo CE projects.

### What Gets Created

- **2 Projects**: Month-end Close, Tax Filing
- **4 Stages**: Preparation, Review, Approval, Done
- **Tasks**: Parent tasks + subtasks per activity/stage
- **Calendar Events**: Holidays from calendar sheet

## Workflow

### 1. Generate CSVs from Source Workbook

```bash
python3 scripts/generate_month_end_imports.py \
    --workbook data/source.xlsx \
    --outdir data \
    --user_map data/user_map.csv
```

This generates:
- `odoo_import_month_end_projects.csv`
- `odoo_import_month_end_stages.csv`
- `odoo_import_month_end_tasks_PassA_parents.csv`
- `odoo_import_month_end_tasks_PassB_children.csv`
- `odoo_import_month_end_calendar_events.csv`

### 2. Replace Placeholders

Before importing, replace any `<<MAP:...>>` placeholders with actual email addresses:

```
Find: <<MAP:Finance Supervisor>>
Replace: supervisor@company.com

Find: <<MAP:Senior Finance Manager>>
Replace: manager@company.com

Find: <<MAP:Finance Director>>
Replace: director@company.com
```

### 3. Import via JSON-RPC

```bash
export ODOO_URL="https://erp.insightpulseai.com"
export ODOO_DB="odoo"
export ODOO_LOGIN="YOUR_LOGIN"
export ODOO_PASSWORD="YOUR_PASSWORD"

python3 scripts/odoo_import_project_suite.py \
    --projects data/odoo_import_month_end_projects.csv \
    --stages data/odoo_import_month_end_stages.csv \
    --tasks_parents data/odoo_import_month_end_tasks_PassA_parents.csv \
    --tasks_children data/odoo_import_month_end_tasks_PassB_children.csv \
    --calendar_events data/odoo_import_month_end_calendar_events.csv
```

## Import Order

1. **Projects** → `project.project`
2. **Stages** → `project.task.type`
3. **Tasks Pass A (parents)** → `project.task`
4. **Tasks Pass B (children)** → `project.task` (then set parent_id)
5. **Calendar Events** → `calendar.event` (requires Calendar module)

## Field Mapping Notes

### Projects
| CSV Column | Odoo Field |
|------------|------------|
| Project Name* | `name` |
| Privacy | `privacy_visibility` |
| Project Manager Email | `user_id` (by login) |
| Allow Timesheets | `allow_timesheets` |

### Stages
| CSV Column | Odoo Field |
|------------|------------|
| Stage Name* | `name` |
| Sequence | `sequence` |
| Folded in Kanban | `fold` |
| Applies to Projects | `project_ids` (M2M) |

### Tasks
| CSV Column | Odoo Field |
|------------|------------|
| Task Name* | `name` |
| Project Name* | `project_id` (by name) |
| Stage Name | `stage_id` (by name) |
| Assignee Emails | `user_ids` (by login/email) |
| Due Date | `date_deadline` |
| Start Date | `planned_date_begin` or `date_start` |
| End Date | `planned_date_end` |
| Parent Task External ID | `parent_id` (via ir.model.data) |

### Calendar Events
| CSV Column | Odoo Field |
|------------|------------|
| Event Title* | `name` |
| All Day | `allday` |
| Start | `start_date` or `start` |
| End | `stop_date` or `stop` |
| Tags | `categ_ids` |

## Source Workbook Sheets

The generator reads these sheets from the Excel workbook:

1. **Closing Task** - Matrix with assignee defaults per stage
2. **Closing Task - Gannt Chart** - Task schedule with dates
3. **Tax Filing** - BIR filing schedule with deadlines
4. **Holidays & Calendar** - Holiday dates for calendar events

## User Mapping

Create `data/user_map.csv` to map employee codes to emails:

```csv
employee_code,email
EMP001,person1@company.com
EMP002,person2@company.com
```

## Dry Run

Test without making changes:

```bash
python3 scripts/odoo_import_project_suite.py \
    --projects data/odoo_import_month_end_projects.csv \
    --stages data/odoo_import_month_end_stages.csv \
    --tasks_parents data/odoo_import_month_end_tasks_PassA_parents.csv \
    --tasks_children data/odoo_import_month_end_tasks_PassB_children.csv \
    --dry_run
```

## Troubleshooting

### Authentication Failed
- Check ODOO_URL, ODOO_DB, ODOO_LOGIN, ODOO_PASSWORD
- Ensure user has API access

### Project/Stage Not Found
- Import Projects and Stages first
- Check for typos in project/stage names

### Calendar Import Failed
- Calendar module must be installed in Odoo
- Calendar events are optional

### Assignees Not Linked
- Ensure user emails match `res.users.login` or `res.users.email`
- Replace `<<MAP:...>>` placeholders before import
