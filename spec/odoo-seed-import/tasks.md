# Tasks — Odoo Seed Import

## Phase 1 — Custom fields (prerequisite)

- [ ] T1: Create 3 custom fields on `res.partner` (x_person_code, x_role_primary, x_department)
- [ ] T2: Create 10 custom fields on `project.project`
- [ ] T3: Create 12 custom fields on `project.task`
- [ ] T4: Create 5 kanban stages in `project.task.type` (not_started, active, review, approval, done)

## Phase 2 — Master data

- [ ] T5: Import `people.csv` → `res.users` (10 users with @demo.local emails)

## Phase 3 — Core objects

- [ ] T6: Import `projects.csv` → `project.project` (8 projects)
- [ ] T7: Import `milestones.csv` → `project.task` with x_is_milestone=true (40 milestones)

## Phase 4 — Execution objects

- [ ] T8: Import `tasks.csv` → `project.task` (45 tasks)

## Phase 5 — UI configuration

- [ ] T9: Create 5 saved filter board views per `boards.csv`
- [ ] T10: Verify all boards show correct data

## Phase 6 — Validation

- [ ] T11: Verify Odoo kanban shows March 2026 Close project
- [ ] T12: Verify person assignments resolve correctly
- [ ] T13: Verify Databricks `odoo_erp` foreign catalog reflects new data
