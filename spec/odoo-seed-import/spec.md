# Spec — Odoo Seed Import

## What

Import 103 seed records from `data-intelligence/seeds/ppm/*.csv` into Odoo CE 18
to create the action surface for the Finance Operations Control Tower demo.

## Why

The Databricks understanding layer is live (gold + Genie). The Odoo doing layer
has no project/task data. Without it, the demo can show analytics but not action.

## Acceptance criteria

1. 10 `res.users` with person_code, role, department matching `people.csv`
2. 8 `project.project` with custom fields matching `projects.csv`
3. 40 `project.task` with `x_is_milestone=true` matching `milestones.csv`
4. 45 `project.task` (regular) matching `tasks.csv`
5. Kanban stages: not_started → active → review → approval → done
6. 5 saved filter boards per `boards.csv`
7. All person_code references resolve to valid Odoo users
8. Odoo kanban board shows the March 2026 Close project with tasks
