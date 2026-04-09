# Implementation Plan — PPM Clarity for Odoo 18

## 1. Strategy Reset

Refactor the delivery strategy from:
- "enhance the existing custom PPM addon"

To:
- "compose CE + OCA baseline, then shrink `ipai_finance_ppm` to delta-only scope"

## 2. Workstreams

### Workstream 1 — Baseline inventory and ownership reset

1. Confirm CE `project` baseline surface
2. Confirm OCA `project` and `timesheet` modules to adopt as canonical base
3. Classify every existing `ipai_finance_ppm` feature as:
   - Replace with CE
   - Replace with OCA
   - Keep as thin delta
   - Delete as deprecated residue

### Workstream 2 — Module decomposition

Refactor `ipai_finance_ppm` into:
- CE/OCA configuration + install-set composition
- Minimal custom models for finance-portfolio delta
- Removal of unrelated/deprecated event-bus or non-PPM glue

Specific removals:
- `project_task_integration.py` — Supabase webhook event emission (deprecated)
- `hr_expense.py` — Pulser AI draft binding (unrelated to PPM)
- `data/ir_cron_ppm_sync.xml` — cron referencing deprecated webhook
- `data/ir_config_parameter_powerbi.xml` — evaluate if still needed
- `static/src/js/okr_dashboard_action.js` — rewrite or remove empty shell

Specific additions (delta models):
- `ppm.budget.line` — budget/forecast/actual per project per period
- `ppm.portfolio.health` — RAG status + health scoring per project
- `ppm.risk` — risk register linked to projects
- `ppm.issue` — issue register linked to projects
- `ppm.scoring` — investment scoring / prioritization
- `ppm.gate.review` — phase-gate review records

### Workstream 3 — Parity and gap management

Document:
- What is now covered by CE/OCA
- What remains delta
- What remains a known gap

Known project-planning dependency gaps must be tracked explicitly and
not hidden under parity claims.

## 3. Target Implementation Shape

### CE / OCA base (install set)

| Module | Purpose |
|--------|---------|
| CE `project` | Core execution surface |
| `project_parent` | Portfolio hierarchy |
| `project_group` | Programme grouping |
| `project_department` | Department classification |
| `project_stakeholder` | Stakeholder registry |
| `project_reviewer` | Review gates |
| `project_role` | Role-based assignment |
| `project_timeline` + `web_timeline` | Timeline view |
| `project_pivot` | Pivot analytics |
| `project_milestone_status` | Milestone reporting |
| `project_template` | Project templates |
| `project_key` | Project shortcodes |
| `project_tag_hierarchy` | Tag classification |
| `project_task_ancestor` | Task hierarchy |
| `project_task_parent_completion_blocking` | Dependency enforcement |
| `project_task_stage_mgmt` | Stage management |
| `project_type` | Type classification |

### Thin custom delta (`ipai_finance_ppm` v18.0.2.0.0)

Only these families remain custom:
- Portfolio finance measures (budget/forecast/variance)
- Portfolio governance objects (gate reviews)
- Risk/issue/scoring
- Executive portfolio rollups (RAG dashboard)

### Manifest dependencies

```python
"depends": [
    "project",
    "account",
    "analytic",
    "project_parent",
    "project_milestone_status",
]
```

## 4. Proof Gates

The refactor is complete only when:
- No CE/OCA-covered capability remains custom without a documented reason
- `ipai_finance_ppm` no longer owns generic project shell features
- Deprecated integration residue is removed
- Known parity gaps are documented in SSOT and docs
- Module installs cleanly with `--test-enable`
