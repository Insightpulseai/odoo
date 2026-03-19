# OCA Project Data Model - Odoo CE 18.0
> Complete field reference for project management with OCA + IPAI extensions

---

## Model Overview

| Model | Technical Name | Purpose | OCA Modules |
|-------|---------------|---------|-------------|
| Project | `project.project` | Container for tasks | project_type, project_template |
| Task | `project.task` | Work items | project_task_code, project_task_dependency |
| Stage | `project.task.type` | Kanban workflow stages | project_task_stage_mgmt, project_task_stage_state |
| Tag | `project.tags` | Categorization labels | (CE native) |
| Milestone | `project.milestone` | Project milestones | project_task_milestone |

---

## 1. project.project (Project)

### Core Fields (Odoo CE 18.0)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | Integer | Auto | Primary key |
| `name` | Char | ✓ | Project name |
| `active` | Boolean | - | Archive flag (default: True) |
| `sequence` | Integer | - | Display order |
| `partner_id` | Many2one → res.partner | - | Customer/Partner |
| `company_id` | Many2one → res.company | - | Company |
| `user_id` | Many2one → res.users | - | Project Manager |
| `date_start` | Date | - | Start date |
| `date` | Date | - | End date |
| `description` | Html | - | Project description |
| `color` | Integer | - | Kanban color index |
| `privacy_visibility` | Selection | - | Visibility (portal/employees/followers) |
| `allow_timesheets` | Boolean | - | Enable timesheets |
| `allow_milestones` | Boolean | - | Enable milestones |
| `task_count` | Integer | Computed | Number of tasks |

### OCA Extension Fields

| Field | Type | Module | Description |
|-------|------|--------|-------------|
| `project_type_id` | Many2one → project.type | project_type | Project classification |
| `is_template` | Boolean | project_template | Mark as template |
| `template_id` | Many2one → project.project | project_template | Source template |
| `version` | Char | project_version | Version number |

### IPAI Extension Fields (ipai_project_program)

| Field | Type | Description |
|-------|------|-------------|
| `is_program` | Boolean | Is this a program (parent container)? |
| `program_code` | Char | Program code (e.g., PRJ-2025-002) |
| `program_type` | Selection | Type: standard/hybrid/agile |
| `parent_id` | Many2one → project.project | Parent program |
| `child_ids` | One2many → project.project | Implementation Modules (IMs) |
| `im_code` | Char | IM code (e.g., IM1, IM2) |

### Key Relationships

```
project.project
    ├── task_ids (One2many → project.task)
    ├── type_ids (Many2many → project.task.type)  # Stages
    ├── tag_ids (Many2many → project.tags)
    ├── milestone_ids (One2many → project.milestone)
    ├── parent_id (Many2one → project.project)    # IPAI: Program hierarchy
    └── child_ids (One2many → project.project)    # IPAI: IMs
```

---

## 2. project.task (Task)

### Core Fields (Odoo CE 18.0)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | Integer | Auto | Primary key |
| `name` | Char | ✓ | Task title |
| `active` | Boolean | - | Archive flag |
| `sequence` | Integer | - | Display order |
| `priority` | Selection | - | Priority: 0 (Normal), 1 (High) |
| `stage_id` | Many2one → project.task.type | - | Current stage |
| `project_id` | Many2one → project.project | - | Parent project |
| `user_ids` | Many2many → res.users | - | Assignees |
| `partner_id` | Many2one → res.partner | - | Customer |
| `date_deadline` | Datetime | - | Deadline |
| `date_assign` | Datetime | - | Assignment date |
| `date_end` | Datetime | - | Completion date |
| `planned_hours` | Float | - | Initially planned hours |
| `remaining_hours` | Float | Computed | Remaining hours |
| `effective_hours` | Float | Computed | Time spent |
| `progress` | Float | Computed | % complete |
| `description` | Html | - | Task description |
| `kanban_state` | Selection | - | Kanban state (normal/done/blocked) |
| `color` | Integer | - | Kanban color |
| `parent_id` | Many2one → project.task | - | Parent task (subtasks) |
| `child_ids` | One2many → project.task | - | Subtasks |
| `tag_ids` | Many2many → project.tags | - | Tags |
| `milestone_id` | Many2one → project.milestone | - | Associated milestone |

### OCA Extension Fields

| Field | Type | Module | Description |
|-------|------|--------|-------------|
| `code` | Char | project_task_code | Task reference code |
| `depend_on_ids` | Many2many → project.task | project_task_dependency | Predecessor tasks |
| `depending_ids` | Many2many → project.task | project_task_dependency | Successor tasks |
| `dependency_type` | Selection | project_task_dependency | FS/SS/FF/SF |
| `lag_days` | Integer | project_task_dependency | Lag in days |
| `is_template` | Boolean | project_task_template | Mark as template |
| `recurring` | Boolean | project_task_recurring | Is recurring task |
| `repeat_interval` | Integer | project_task_recurring | Repeat interval |
| `repeat_unit` | Selection | project_task_recurring | Repeat unit (day/week/month) |

### IPAI Extension Fields

| Field | Type | Module | Description |
|-------|------|--------|-------------|
| `directory_person_id` | Many2one → ipai.directory.person | ipai_project_program | Assigned from directory |
| `finance_category` | Selection | ipai_finance_ppm | Category: foundation_corp, vat_tax, etc. |
| `close_day` | Integer | ipai_finance_ppm | Relative close day (-3, -1, 0, +3) |

### Key Relationships

```
project.task
    ├── stage_id (Many2one → project.task.type)
    ├── project_id (Many2one → project.project)
    ├── user_ids (Many2many → res.users)
    ├── parent_id (Many2one → project.task)      # Subtasks
    ├── child_ids (One2many → project.task)
    ├── depend_on_ids (Many2many → project.task) # OCA: Dependencies
    ├── depending_ids (Many2many → project.task)
    └── milestone_id (Many2one → project.milestone)
```

---

## 3. project.task.type (Stage)

### Core Fields (Odoo CE 18.0)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | Integer | Auto | Primary key |
| `name` | Char | ✓ | Stage name |
| `sequence` | Integer | - | Display order |
| `fold` | Boolean | - | Folded in Kanban (closing stage) |
| `description` | Text | - | Stage description |
| `project_ids` | Many2many → project.project | - | Projects using this stage |
| `mail_template_id` | Many2one → mail.template | - | Auto-send email on stage change |

### OCA Extension Fields

| Field | Type | Module | Description |
|-------|------|--------|-------------|
| `state` | Selection | project_task_stage_state | Broad state: draft/open/pending/done/cancelled |
| `is_closed` | Boolean | project_stage_closed | Mark as closed stage |
| `closed` | Boolean | project_stage_closed | Lock stage editing |

### Canonical Finance PPM Stages

| XML ID | Name | Sequence | Fold | State | Description |
|--------|------|----------|------|-------|-------------|
| `stage_todo` | To Do | 10 | False | draft | Tasks not yet started |
| `stage_in_preparation` | In Preparation | 20 | False | open | Data gathering, initial work |
| `stage_under_review` | Under Review | 30 | False | open | Supervisor review |
| `stage_pending_approval` | Pending Approval | 40 | False | pending | Awaiting FD sign-off |
| `stage_done` | Done | 50 | True | done | Completed (closing stage) |
| `stage_cancelled` | Cancelled | 60 | True | cancelled | Cancelled tasks |

---

## 4. Supporting Models

### project.type (OCA: project_type)

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Primary key |
| `name` | Char | Type name (e.g., "Finance PPM") |
| `description` | Text | Type description |
| `project_ids` | One2many → project.project | Projects of this type |

### project.milestone (CE Native)

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Primary key |
| `name` | Char | Milestone name |
| `project_id` | Many2one → project.project | Parent project |
| `deadline` | Date | Target date |
| `is_reached` | Boolean | Reached flag |
| `reached_date` | Date | Actual completion date |

### project.tags (CE Native)

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Primary key |
| `name` | Char | Tag name |
| `color` | Integer | Color index |

### ipai.directory.person (IPAI)

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Primary key |
| `code` | Char | Person code (e.g., CKVC, RIM, BOM) |
| `name` | Char | Full name |
| `email` | Char | Email address |
| `role` | Char | Role (Finance Director, Senior Finance Manager, etc.) |
| `user_id` | Many2one → res.users | Linked Odoo user (optional) |

---

## 5. Logframe to Data Model Mapping

| Logframe Column | Odoo Model | Field | Notes |
|-----------------|------------|-------|-------|
| `program` | project.project | `name` | Where `is_program=True` |
| `project` | project.project | `name` | IM projects (child of program) |
| `objective` | project.milestone | `name` | Key milestones |
| `task_code` | project.task | `code` | OCA: project_task_code |
| `task_name` | project.task | `name` | Task title |
| `assignee` | ipai.directory.person | `code` | Linked via `directory_person_id` |
| `company` | res.company | `name` | Via `project.company_id` |
| `deadline` | project.task | `date_deadline` | Task deadline |
| `frequency` | project.task | `repeat_unit` | OCA: project_task_recurring |
| `active` | project.task | `active` | Archive flag |
| `stage` | project.task.type | `name` | Current stage |

---

## 6. Entity-Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          OCA PROJECT DATA MODEL                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────┐         ┌─────────────────┐                            │
│  │ project.type    │         │ res.company     │                            │
│  │ (OCA)           │         │                 │                            │
│  └────────┬────────┘         └────────┬────────┘                            │
│           │                           │                                      │
│           │ project_type_id           │ company_id                          │
│           ▼                           ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐            │
│  │                    project.project                           │            │
│  │  - is_program (IPAI)                                         │            │
│  │  - program_code (IPAI)                                       │            │
│  │  - parent_id → self                                          │            │
│  └──────────┬───────────────────────────────────────┬───────────┘            │
│             │ project_id                            │ type_ids (M2M)        │
│             ▼                                       ▼                        │
│  ┌─────────────────────────────────┐    ┌─────────────────────────┐         │
│  │         project.task            │    │  project.task.type      │         │
│  │  - code (OCA)                   │    │  - state (OCA)          │         │
│  │  - depend_on_ids (OCA)          │    │  - fold                 │         │
│  │  - directory_person_id (IPAI)   │    │  - is_closed (OCA)      │         │
│  └──────────┬───────────────────┬──┘    └─────────────────────────┘         │
│             │ stage_id          │                                            │
│             └───────────────────┘                                            │
│                                                                              │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────────┐      │
│  │ project.tags    │    │project.milestone│    │ipai.directory.person│      │
│  │ (M2M via task)  │    │ (milestone_id)  │    │ (IPAI)              │      │
│  └─────────────────┘    └─────────────────┘    └─────────────────────┘      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 7. OCA Modules Reference (18.0)

| Module | Version | Category | Finance PPM |
|--------|---------|----------|-------------|
| project_stage_closed | 18.0.1.0.0 | Stage Management | ✓ |
| project_task_stage_mgmt | 18.0.1.0.0 | Stage Management | ✓ |
| project_task_stage_state | 18.0.1.0.0 | Stage Management | ✓ |
| project_task_default_stage | 18.0.1.0.0 | Stage Management | ✓ |
| project_template | 18.0.1.0.0 | Templates | ✓ |
| project_task_template | 18.0.1.0.0 | Templates | ✓ |
| project_timeline | 18.0.1.0.0 | Views | ✓ |
| project_timeline_hr_timesheet | 18.0.1.0.0 | Views | ✓ |
| project_timesheet_time_control | 18.0.1.0.5 | Timesheet | ✓ |
| project_type | 18.0.1.0.0 | Classification | ✓ |
| project_task_code | 18.0.1.0.0 | Task Fields | ✓ |
| project_task_dependency | 18.0.1.0.0 | Dependencies | ✓ |
| project_task_recurring | 18.0.1.0.0 | Recurring | ✓ |
| project_task_milestone | 18.0.1.0.0 | Planning | ✓ |
| project_version | 18.0.1.0.0 | Versioning | - |
| project_task_add_very_high | 18.0.1.0.0 | Priority | - |

---

## 8. Installation Order

```bash
# Tier 1: Core Stage Management (Install First)
docker compose exec odoo-core odoo -d odoo_core -i \
  project_task_stage_mgmt,project_task_stage_state,project_stage_closed,project_task_default_stage \
  --stop-after-init

# Tier 2: Templates & Views
docker compose exec odoo-core odoo -d odoo_core -i \
  project_template,project_task_template,project_timeline,project_timeline_hr_timesheet \
  --stop-after-init

# Tier 3: Task Extensions
docker compose exec odoo-core odoo -d odoo_core -i \
  project_task_code,project_task_dependency,project_task_recurring,project_task_milestone \
  --stop-after-init

# Tier 4: IPAI Finance PPM
docker compose exec odoo-core odoo -d odoo_core -i \
  ipai_project_program,ipai_finance_ppm \
  --stop-after-init
```

---

## 9. Verification Queries

```python
# Verify stages with state attribute
Stage = env['project.task.type']
for s in Stage.search([], order='sequence'):
    print(f"{s.sequence}: {s.name} | fold={s.fold} | state={getattr(s, 'state', 'N/A')}")

# Verify Finance PPM project
Project = env['project.project']
ppm = Project.search([('name', 'ilike', 'Finance PPM')])
print(f"Finance PPM Projects: {ppm.mapped('name')}")

# Verify task codes
Task = env['project.task']
tasks = Task.search([('code', '!=', False)], limit=10)
for t in tasks:
    print(f"{t.code}: {t.name} | Stage: {t.stage_id.name}")
```

---

*Generated: 2026-01-21*
*Branch: claude/configure-oca-project-modules-HNhYI*
*Commit: 7b37f4a*
