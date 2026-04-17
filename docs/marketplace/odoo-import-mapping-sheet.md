# Odoo Import Mapping Sheet — Pulser for Odoo Seed Data

**Scope:** CSV seed data import for Pulser for Odoo demo and onboarding environments
**Target Odoo version:** 18.0 CE
**Date:** 2026-04-15

---

## Overview

This sheet maps 7 CSV seed files to their Odoo target models and fields. It defines the import order, required custom fields, lookup dependencies, stage configuration, and the minimum viable implementation path.

---

## File 1: people.csv

**Target model:** `res.users` (with linked `res.partner`)

### Field Mapping

| CSV Field | Target Model | Target Field | Required | Notes |
|-----------|-------------|--------------|----------|-------|
| `name` | `res.partner` | `name` | Yes | Full display name |
| `email` | `res.users` | `login` | Yes | Used as login; must be unique |
| `email` | `res.partner` | `email` | Yes | Same value as login |
| `role` | `res.users` | `x_role` | No | Custom field — see custom fields list |
| `department` | `res.partner` | `x_department` | No | Custom field — see custom fields list |
| `job_title` | `res.partner` | `job_position` | No | Maps to `job_position` on partner |
| `phone` | `res.partner` | `phone` | No | |
| `active` | `res.users` | `active` | No | Boolean; default `True` if omitted |
| `company_id` | `res.users` | `company_id` | Yes | Must match `res.company.name` or ID |
| `groups` | `res.groups` | (many2many) | No | Comma-separated group XML IDs; import manually or via script |

### Lookup Dependencies

- `company_id` → `res.company` must exist before import
- `groups` cannot be set via standard CSV import; use `ir.model.data` lookup or post-import script

---

## File 2: portfolios.csv

**Target model:** `project.project` (top-level portfolio records; `x_is_portfolio = True`)

### Field Mapping

| CSV Field | Target Model | Target Field | Required | Notes |
|-----------|-------------|--------------|----------|-------|
| `name` | `project.project` | `name` | Yes | Portfolio name |
| `code` | `project.project` | `x_portfolio_code` | No | Custom field — unique portfolio reference code |
| `owner_email` | `res.users` | `user_id` | Yes | Lookup by email → `res.users.id` |
| `description` | `project.project` | `description` | No | HTML or plain text |
| `start_date` | `project.project` | `date_start` | No | ISO 8601 date |
| `end_date` | `project.project` | `date` | No | ISO 8601 date; maps to `date` (planned end) |
| `active` | `project.project` | `active` | No | Boolean; default `True` |
| `company_id` | `project.project` | `company_id` | Yes | Must match `res.company` |
| `is_portfolio` | `project.project` | `x_is_portfolio` | No | Custom boolean — set `True` for portfolio rows |

### Lookup Dependencies

- `owner_email` → `res.users` (people.csv must be imported first)
- `company_id` → `res.company`

---

## File 3: programs.csv

**Target model:** `project.project` (mid-level program records; `x_is_program = True`, linked to portfolio via `x_portfolio_id`)

### Field Mapping

| CSV Field | Target Model | Target Field | Required | Notes |
|-----------|-------------|--------------|----------|-------|
| `name` | `project.project` | `name` | Yes | Program name |
| `code` | `project.project` | `x_program_code` | No | Custom field — unique program reference code |
| `portfolio_code` | `project.project` | `x_portfolio_id` | Yes | Lookup by `x_portfolio_code` → `project.project.id` |
| `owner_email` | `res.users` | `user_id` | Yes | Lookup by email |
| `description` | `project.project` | `description` | No | |
| `start_date` | `project.project` | `date_start` | No | |
| `end_date` | `project.project` | `date` | No | |
| `active` | `project.project` | `active` | No | |
| `company_id` | `project.project` | `company_id` | Yes | |
| `is_program` | `project.project` | `x_is_program` | No | Custom boolean — set `True` for program rows |

### Lookup Dependencies

- `portfolio_code` → `project.project` where `x_is_portfolio = True` (portfolios.csv must be imported first)
- `owner_email` → `res.users`

---

## File 4: projects.csv

**Target model:** `project.project` (leaf-level project records; linked to program via `x_program_id`)

### Field Mapping

| CSV Field | Target Model | Target Field | Required | Notes |
|-----------|-------------|--------------|----------|-------|
| `name` | `project.project` | `name` | Yes | Project name |
| `code` | `project.project` | `x_project_code` | No | Custom field — unique project reference code |
| `program_code` | `project.project` | `x_program_id` | Yes | Lookup by `x_program_code` → `project.project.id` |
| `manager_email` | `res.users` | `user_id` | Yes | Project manager; lookup by email |
| `description` | `project.project` | `description` | No | |
| `start_date` | `project.project` | `date_start` | No | |
| `end_date` | `project.project` | `date` | No | |
| `active` | `project.project` | `active` | No | |
| `company_id` | `project.project` | `company_id` | Yes | |
| `partner_id` | `res.partner` | `partner_id` | No | Customer; lookup by `res.partner.name` or ref |
| `analytic_account_id` | `account.analytic.account` | `analytic_account_id` | No | Lookup by analytic account name or code |
| `planned_hours` | `project.project` | `x_planned_hours` | No | Custom field — total planned hours for project |
| `budget` | `project.project` | `x_budget` | No | Custom field — approved budget (monetary) |
| `billing_type` | `project.project` | `x_billing_type` | No | Custom field — selection: `fixed_price`, `time_materials`, `retainer` |
| `status` | `project.project` | `x_project_status` | No | Custom field — selection: `pipeline`, `active`, `on_hold`, `closed` |
| `privacy_visibility` | `project.project` | `privacy_visibility` | No | `followers`, `employees`, `portal`; default `employees` |

### Lookup Dependencies

- `program_code` → `project.project` where `x_is_program = True` (programs.csv must be imported first)
- `manager_email` → `res.users`
- `partner_id` → `res.partner`
- `analytic_account_id` → `account.analytic.account`

---

## File 5: milestones.csv

**Target model:** `project.milestone`

### Field Mapping

| CSV Field | Target Model | Target Field | Required | Notes |
|-----------|-------------|--------------|----------|-------|
| `name` | `project.milestone` | `name` | Yes | Milestone name |
| `project_code` | `project.project` | `project_id` | Yes | Lookup by `x_project_code` → `project.project.id` |
| `deadline` | `project.milestone` | `deadline` | No | ISO 8601 date |
| `is_reached` | `project.milestone` | `is_reached` | No | Boolean; default `False` |
| `reached_date` | `project.milestone` | `reached_date` | No | ISO 8601 date; only set if `is_reached = True` |
| `description` | `project.milestone` | `x_milestone_description` | No | Custom field — milestone acceptance criteria or notes |
| `sequence` | `project.milestone` | `sequence` | No | Integer; controls display order |

### Lookup Dependencies

- `project_code` → `project.project` (projects.csv must be imported first)

---

## File 6: tasks.csv

**Target model:** `project.task`

### Field Mapping

| CSV Field | Target Model | Target Field | Required | Notes |
|-----------|-------------|--------------|----------|-------|
| `name` | `project.task` | `name` | Yes | Task name |
| `project_code` | `project.project` | `project_id` | Yes | Lookup by `x_project_code` |
| `milestone_name` | `project.milestone` | `milestone_id` | No | Lookup by milestone name within project |
| `assignee_email` | `res.users` | `user_ids` | No | Many2many; lookup by email; comma-separated for multiple |
| `stage` | `project.task.type` | `stage_id` | No | Lookup by stage name — see Stage Mapping section |
| `description` | `project.task` | `description` | No | HTML or plain text |
| `deadline` | `project.task` | `date_deadline` | No | ISO 8601 date |
| `planned_hours` | `project.task` | `planned_hours` | No | Float |
| `priority` | `project.task` | `priority` | No | `0` = normal, `1` = high |
| `tag_names` | `project.tags` | `tag_ids` | No | Comma-separated tag names; must exist or be created first |
| `parent_task_name` | `project.task` | `parent_id` | No | Lookup by task name within same project; import subtasks in second pass |
| `x_task_type` | `project.task` | `x_task_type` | No | Custom field — selection: `deliverable`, `milestone_task`, `internal`, `review` |
| `x_effort_points` | `project.task` | `x_effort_points` | No | Custom field — integer story points or effort estimate |
| `x_billable` | `project.task` | `x_billable` | No | Custom field — boolean; whether task is billable |
| `x_billing_milestone_id` | `project.milestone` | `x_billing_milestone_id` | No | Custom field — links task to billing milestone |
| `kanban_state` | `project.task` | `kanban_state` | No | `normal`, `done`, `blocked`; default `normal` |

### Lookup Dependencies

- `project_code` → `project.project` (projects.csv must be imported first)
- `milestone_name` → `project.milestone` scoped to project (milestones.csv must be imported first)
- `assignee_email` → `res.users` (people.csv must be imported first)
- `stage` → `project.task.type` (stages must exist — see Stage Mapping)
- `parent_task_name` → `project.task` (subtasks require a second-pass import after parent tasks exist)

---

## File 7: boards.csv

**Target model:** `project.task.type` (Kanban stage/board column definitions, scoped to projects)

### Field Mapping

| CSV Field | Target Model | Target Field | Required | Notes |
|-----------|-------------|--------------|----------|-------|
| `name` | `project.task.type` | `name` | Yes | Stage/column name (e.g., "Backlog", "In Progress", "Done") |
| `sequence` | `project.task.type` | `sequence` | No | Integer; controls left-to-right column order |
| `project_codes` | `project.project` | `project_ids` | No | Many2many; comma-separated `x_project_code` values; leave blank for global stages |
| `fold` | `project.task.type` | `fold` | No | Boolean; whether column is folded in Kanban by default |
| `description` | `project.task.type` | `description` | No | Stage description or definition of done |
| `rating_template_id` | `mail.template` | `rating_template_id` | No | Customer satisfaction template; lookup by template name |
| `auto_validation_kanban_state` | `project.task.type` | `auto_validation_kanban_state` | No | Boolean; auto-mark done when kanban state = done |

### Lookup Dependencies

- `project_codes` → `project.project` (projects.csv must be imported first if scoping stages to projects)

---

## Import Order (5 Phases)

### Phase 1 — Foundation

1. `boards.csv` → `project.task.type` (global stages first, unscoped)
2. `people.csv` → `res.users` + `res.partner`

*No lookup dependencies in this phase.*

### Phase 2 — Hierarchy Top

3. `portfolios.csv` → `project.project` (`x_is_portfolio = True`)

*Depends on: res.users (Phase 1)*

### Phase 3 — Hierarchy Mid

4. `programs.csv` → `project.project` (`x_is_program = True`)

*Depends on: portfolios (Phase 2), res.users (Phase 1)*

### Phase 4 — Hierarchy Leaf + Milestones

5. `projects.csv` → `project.project` (leaf projects)
6. `boards.csv` (second pass, scoped) → re-import or update `project_ids` on `project.task.type` to scope stages to projects
7. `milestones.csv` → `project.milestone`

*Depends on: programs (Phase 3), res.users (Phase 1), res.partner, account.analytic.account*

### Phase 5 — Tasks

8. `tasks.csv` → `project.task` (parent tasks first, then subtasks in a second pass)

*Depends on: projects, milestones, res.users, project.task.type (all prior phases)*

---

## Recommended Custom Fields

### On `project.project`

| Field Name | Type | Description |
|------------|------|-------------|
| `x_is_portfolio` | Boolean | Marks record as a portfolio (top-level) |
| `x_is_program` | Boolean | Marks record as a program (mid-level) |
| `x_portfolio_code` | Char | Unique portfolio reference code |
| `x_program_code` | Char | Unique program reference code |
| `x_project_code` | Char | Unique project reference code |
| `x_portfolio_id` | Many2one → `project.project` | Parent portfolio link |
| `x_program_id` | Many2one → `project.project` | Parent program link |
| `x_planned_hours` | Float | Total planned hours for project |
| `x_budget` | Monetary | Approved project budget |
| `x_billing_type` | Selection | `fixed_price` / `time_materials` / `retainer` |
| `x_project_status` | Selection | `pipeline` / `active` / `on_hold` / `closed` |

### On `project.task`

| Field Name | Type | Description |
|------------|------|-------------|
| `x_task_type` | Selection | `deliverable` / `milestone_task` / `internal` / `review` |
| `x_effort_points` | Integer | Story points or effort estimate |
| `x_billable` | Boolean | Whether task hours are billable |
| `x_billing_milestone_id` | Many2one → `project.milestone` | Links task to billing milestone |

### On `res.users`

| Field Name | Type | Description |
|------------|------|-------------|
| `x_role` | Char | Business role (e.g., "Analyst", "Senior Consultant") |
| `x_department` | Char | Department or practice area |

### On `project.milestone`

| Field Name | Type | Description |
|------------|------|-------------|
| `x_milestone_description` | Text | Acceptance criteria or milestone notes |

---

## Stage Mapping Suggestion

Define these stages in `project.task.type` before importing tasks. Sequence them in this order:

| Sequence | Stage Name | Fold | Notes |
|----------|-----------|------|-------|
| 10 | Backlog | No | Default for new tasks |
| 20 | To Do | No | Planned but not started |
| 30 | In Progress | No | Active work |
| 40 | In Review | No | Pending review or approval |
| 50 | Done | No | Completed |
| 60 | Cancelled | Yes | Folded by default |

---

## Minimum Viable Implementation Path

For a working demo environment with the least import risk:

1. **Create custom fields** on `project.project`, `project.task`, and `res.users` using Odoo Settings > Technical > Fields (or a migration script). Do not skip this step — CSV imports will silently drop unmapped columns.

2. **Import boards.csv** (global stages, no project scoping). Verify stages appear in project Kanban.

3. **Import people.csv.** Verify user logins are created and can log in. Do not set groups via CSV — set them manually or via a post-import script.

4. **Import portfolios.csv.** Verify portfolio records exist in `project.project` with `x_is_portfolio = True`.

5. **Import programs.csv.** Verify portfolio links (`x_portfolio_id`) are correctly resolved.

6. **Import projects.csv.** Verify program links, manager assignments, and analytic account bindings.

7. **Import milestones.csv.** Verify deadline dates and project links.

8. **Import tasks.csv (parent tasks only** — exclude rows where `parent_task_name` is populated). Verify stage assignments.

9. **Import tasks.csv (subtasks only** — rows where `parent_task_name` is populated). Verify parent links.

10. **Update boards.csv project scoping** — re-associate stages to specific projects where the demo requires per-project Kanban boards.

---

## Validation Checklist

Before marking the import complete, verify:

- [ ] All `res.users` records have valid logins and linked `res.partner` records
- [ ] No duplicate `x_portfolio_code`, `x_program_code`, or `x_project_code` values
- [ ] All `project.project` records have a valid `user_id` (project manager / portfolio owner)
- [ ] Portfolio → Program → Project hierarchy is intact (check `x_portfolio_id` and `x_program_id` on each record)
- [ ] All `project.milestone` records have a valid `project_id`
- [ ] All `project.task` records have a valid `project_id` and `stage_id`
- [ ] Subtasks have a valid `parent_id`
- [ ] No tasks are stuck in a non-existent stage (broken stage lookup returns `False`)
- [ ] `x_billing_type` selection values match the field's defined options exactly
- [ ] `x_project_status` selection values match the field's defined options exactly
- [ ] Analytic accounts linked to projects exist in `account.analytic.account`
- [ ] Power BI data model refreshes cleanly against the imported Odoo dataset
