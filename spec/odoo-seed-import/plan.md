# Plan — Odoo Seed Import

## Architecture

- Target: Odoo CE 18 on `ca-ipai-odoo-dev` (sponsored sub)
- DB: `pg-ipai-odoo` → database `odoo_dev`
- Import method: Odoo XML-RPC or CSV import via UI
- Custom fields: 17 fields on `project.project` + `project.task`

## Tech decisions

1. Use Odoo's built-in CSV import (Settings → Technical → Import)
2. Create custom fields via Settings → Technical → Database Structure → Fields
3. Stage mapping: create 5 `project.task.type` records
4. No custom module needed — all via configuration + import

## Custom fields required

### On `project.project` (10 fields)
x_external_project_id, x_program_id, x_phase, x_business_domain,
x_control_tower_domain, x_deadline_risk, x_evidence_required,
x_pulser_ready, x_databricks_surface, x_genie_surface

### On `project.task` (12 fields)
x_external_task_id, x_is_milestone, x_task_category, x_activity_stage,
x_assigned_person_code, x_reviewer_code, x_approver_code,
x_evidence_required, x_evidence_status, x_deadline_risk,
x_automation_candidate, x_pulser_ready

### On `res.users` / `res.partner` (3 fields)
x_person_code, x_role_primary, x_department
