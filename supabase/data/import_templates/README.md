# Odoo 18 CE Project Import Templates

Production-ready CSV templates for importing Project data with IPAI extensions.

## Import Order (MANDATORY)

Import files in this exact sequence:

| Step | File | Model | Mode | Description |
|------|------|-------|------|-------------|
| 1 | `01_project.task.type.csv` | project.task.type | CREATE | Stages/columns |
| 2 | `02_project.project.csv` | project.project | CREATE | Projects & Programs |
| 3 | `03_project.milestone.csv` | project.milestone | CREATE | Milestones |
| 4 | `04_project.task.csv` | project.task | CREATE | Tasks |
| 5 | `05_project.task.dependencies.csv` | project.task | UPDATE | Set depend_on_ids |
| 6 | `06_project.task.recurrence.csv` | project.task | UPDATE | Set recurrence fields |
| 7 | `07_mail.activity.csv` | mail.activity | SCRIPT | Via import_activities.py |

## Quick Start

```bash
# Run full import sequence
./scripts/import/run_import_sequence.sh

# Verify import
./scripts/import/verify_import.sh
```

## CSV Format Notes

### External IDs
- All `id` columns contain External IDs (e.g., `ipai_project.task_001`)
- Many2one fields use `<field>/id` format (e.g., `project_id/id`)
- Many2many fields use comma-separated External IDs

### Selection Fields
- `health_status`: `green`, `yellow`, `red`
- `program_type`: `finance_ppm`, `bir`, `hybrid`
- `milestone_type`: `phase_gate`, `deliverable`, `approval`, `decision`, `review`, `checkpoint`
- `gate_status`: `not_started`, `in_progress`, `passed`, `failed`, `conditional`
- `repeat_unit`: `day`, `week`, `month`, `year`
- `repeat_type`: `forever`, `until`, `after`
- `priority`: `0` (Normal), `1` (High)
- `kanban_state`: `normal`, `done`, `blocked`

### Boolean Fields
- Use `true` or `false` (lowercase)

### Date Fields
- Use `YYYY-MM-DD` format

## File Descriptions

### 01_project.task.type.csv
Task stages/columns. Set `fold=true` for closed states.

### 02_project.project.csv
Projects with IPAI Clarity PPM extensions:
- `clarity_id`: Unique Clarity project ID
- `health_status`: Project health indicator
- `is_program`: True for parent Programs
- `parent_id/id`: Link to parent Program
- `program_type`: Classification

### 03_project.milestone.csv
Milestones with IPAI extensions:
- `milestone_type`: Classification
- `gate_status`: Gate review status
- `approval_required`: Needs formal approval

### 04_project.task.csv
Tasks (create pass only - no dependencies/recurrence yet):
- Standard task fields
- `milestone_id/id`: Link to milestone
- `parent_id/id`: For subtasks

### 05_project.task.dependencies.csv
UPDATE PASS - Sets `depend_on_ids/id` on existing tasks.
Tasks must exist before running this import.

### 06_project.task.recurrence.csv
UPDATE PASS - Sets recurrence fields on existing tasks:
- `recurring_task`: Enable recurrence
- `repeat_interval`: Frequency number
- `repeat_unit`: day/week/month/year
- `repeat_type`: forever/until/after

### 07_mail.activity.csv
Activities with `res_external_id` column (resolved by script).
Cannot use standard import due to `res_id` being an integer.

## Customizing Templates

1. Copy a template
2. Update External IDs with your prefix
3. Adjust field values
4. Run import sequence

## Troubleshooting

### "External ID not found"
Ensure dependencies are imported first (follow import order).

### "Constraint violation"
Check required fields and selection values.

### Dependencies not working
1. Verify `allow_task_dependencies=true` on project
2. Ensure tasks exist before dependency update pass

### Recurrence not working
1. Verify `allow_recurring_tasks=true` on project
2. Check `repeat_unit` uses valid value
