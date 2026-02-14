# PRD — Odoo 18 CE Project Suite (Toggleable)

## Goal

Provide a production-grade Project Management system on Odoo 18 CE with optional advanced features via toggles: milestones, dependencies, budgeting, RACI, stage-gates, templates, and reporting views.

## Users & Roles

| Role | Description |
|------|-------------|
| Admin | Configure toggles, manage security |
| Project Manager | Own projects, plan tasks, approve gates |
| Contributor | Execute tasks, log time (if enabled) |
| Finance/Controller | Review budgets and actuals (if enabled) |
| Portal User | Limited visibility via project privacy (optional) |

## In Scope

### Core Enhancements (Always-On)

- Consistent project/task views
- Chatter + activities on core objects
- KPI reporting actions (basic)

### Toggle Features

#### 1. Timesheets (`enable_timesheets`)
- Link to analytic lines
- Compute `effective_hours` and cost if configured

#### 2. Dependencies (`enable_dependencies`)
- Define task dependencies with types (FS/SS/FF/SF) and lag
- Prevent invalid transitions optionally
- Circular dependency detection

#### 3. Milestones (`enable_milestones`)
- Milestone entity with target/actual dates
- Tasks optionally linked to milestones
- Progress rollups based on task completion

#### 4. Budgeting (`enable_budgeting`)
- Budget headers + lines
- Actuals computed from analytic/accounting
- Variance tracking and reporting

#### 5. RACI (`enable_raci`)
- Role assignments per project/task
- Responsible/Accountable/Consulted/Informed
- Enforce single Accountable per entity

#### 6. Stage Gates (`enable_stage_gates`)
- Approval gates per stage
- Required fields/checks before advancing
- Gate result tracking

#### 7. Templates (`enable_templates`)
- Project template with stages + default tasks + tags
- Apply template action

#### 8. Reporting Views (`enable_reporting_views`)
- SQL views for KPI dashboards
- By project, by assignee, overdue, burn

## Out of Scope

- Full Agile/Scrum boards (can be added later)
- Enterprise Gantt (CE-safe timeline can be added later)

## Data Model

### Canonical (Odoo core)
- `project.project`
- `project.task`
- `project.task.type`
- `project.tags`

### IPAI Additions
- `ipai.project.milestone`
- `ipai.project.task.dependency`
- `ipai.project.budget`
- `ipai.project.budget.line`
- `ipai.project.raci`
- `ipai.project.stage.gate`
- `ipai.project.stage.gate.result`
- `ipai.project.template`
- `ipai.project.template.task`

## Security

### Groups
- `group_ipai_project_manager` - Full access to IPAI features
- `group_ipai_project_finance` - Budget access
- `group_ipai_project_contributor` - Read + task updates

### Record Rules
- Company boundary
- Project privacy visibility
- Role-based write permissions

## Acceptance Criteria

1. All toggles configurable in Settings > Project
2. When toggle OFF: feature menus/tabs hidden; no functional side effects
3. When toggle ON: feature becomes usable without reinstall
4. Module upgrades do not break existing records
5. All models have access rules and ACLs
6. Basic KPI actions load under 1s for 10k tasks (index-backed)

## Import System

### Supported Imports
- Projects from CSV/XLSX
- Stages from CSV/XLSX
- Tasks (parent + child) from CSV/XLSX
- Calendar events from CSV/XLSX

### Import Flow
1. Generate CSVs from source workbook
2. Import via JSON-RPC API
3. External IDs tracked via ir.model.data
