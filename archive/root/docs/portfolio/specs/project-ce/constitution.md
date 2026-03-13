# Constitution — Project CE Suite (Toggleable)

## Purpose

Deliver a CE-compatible Project Management suite for Odoo 18 with toggleable "enterprise-like" capabilities while keeping canonical data in Odoo core models.

## Non-Negotiables

1. **CE-first**: No Enterprise-only dependencies.
2. **Canonical ownership**:
   - Projects live in `project.project`
   - Tasks live in `project.task`
   - Stages live in `project.task.type`
3. **Toggles are runtime**: Settings stored in `ir.config_parameter` via `res.config.settings`.
4. **Feature flags are deterministic**: No silent behavior changes; everything is gated via explicit flags.
5. **Upgrade-safe**: Migrations must be additive; avoid destructive field changes.
6. **Security & RLS-equivalent**: Odoo access rules (`ir.rule`) and groups enforce privacy by company and role.
7. **Auditability**: Business-critical actions emit chatter messages and/or `mail.activity` where relevant.

## Supported Feature Flags

| Flag | Purpose |
|------|---------|
| `ipai.project.enable_timesheets` | Enable timesheet tracking |
| `ipai.project.enable_dependencies` | Enable task dependencies |
| `ipai.project.enable_milestones` | Enable project milestones |
| `ipai.project.enable_budgeting` | Enable budget management |
| `ipai.project.enable_raci` | Enable RACI role assignments |
| `ipai.project.enable_stage_gates` | Enable approval gates |
| `ipai.project.enable_templates` | Enable project templates |
| `ipai.project.enable_reporting_views` | Enable advanced reporting |

## Data Contracts

- Any "new feature" must extend core with:
  - Lightweight link fields on `project.project` / `project.task`
  - Separate models in `ipai.*` namespace for feature-specific entities

## Performance Rules

- No N+1 in list views (use `read_group`, computed fields must be stored when expensive).
- Reporting must use SQL views or stored computed values where appropriate.

## Module Namespace

All custom models use the `ipai.project.*` prefix:
- `ipai.project.milestone`
- `ipai.project.task.dependency`
- `ipai.project.budget`
- `ipai.project.budget.line`
- `ipai.project.raci`
- `ipai.project.stage.gate`
- `ipai.project.template`
