# PRD — PPM Clarity for Odoo 18

## 1. Product Name

**PPM Clarity for Odoo 18** (CE + OCA + thin delta)

## 2. Product Goal

Deliver a Clarity PPM-equivalent capability in Odoo 18 by composing:
- Odoo CE 18 `project`
- OCA `project` and `timesheet` modules
- A reduced `ipai_finance_ppm` delta addon

## 3. Reverse Benchmark

**Benchmark product**: Broadcom Clarity PPM

Clarity PPM provides portfolio management, demand management, financial
planning, resource management, and project execution. It is heavyweight,
expensive ($10-15K/year for small teams), and not Odoo-native.

The target is to achieve ≥80% Clarity PPM capability parity using Odoo CE
and OCA modules, with custom code only for finance-portfolio features.

## 4. Current State

### Current-state correction

The current implementation direction overweights `ipai_finance_ppm`.
Research shows:
- `ipai_finance_ppm` exists and is currently treated as a core addon
- OCA 18 project modules already cover much of the non-finance structure/workflow shell
- The current custom addon includes residue that should not define the target PPM architecture
- Project dependency/capacity-style parity still has explicit documented gaps

Therefore the product must be reframed as **CE/OCA-native first**, not
**custom-module first**.

### What `ipai_finance_ppm` carries today (v18.0.1.0.0)

| Feature | Assessment |
|---------|-----------|
| Budget field on `project.project` | Keep (delta) |
| Budget sync to analytic account | Keep (delta) |
| Cost center tracking | Keep (delta) |
| Import provenance (batch ID, source) | Keep (delta) |
| Pulser AI expense drafting | **Remove** (unrelated to PPM) |
| Task event emission to Supabase webhook | **Remove** (deprecated) |
| Overdue task cron via webhook | **Remove** (deprecated) |
| OKR dashboard JS action | **Rewrite** (empty shell) |

## 5. Baseline Capability Model

### Odoo CE 18 baseline

Treat Odoo CE 18 Project as the baseline for:
- Projects, tasks, milestones, updates/status
- Tags, stages, task recurrence
- Burn-down chart, analytic account linkage
- Project execution workflows

This is the native execution layer, not the full portfolio layer.

### OCA baseline

Treat OCA as the baseline for the following capability families already
present in the workspace:
- Hierarchy / parent-child project structure
- Stakeholder and reviewer assignment
- Role-based project assignment
- Timeline/pivot/project analytics
- Template and stage-management enhancements
- Task hierarchy / completion-blocking enhancements

These must be the default implementation path before any new custom PPM
code is approved.

## 6. Functional Scope

### Must be implemented via CE/OCA composition

| Capability | Source |
|-----------|--------|
| Project hierarchy / portfolio grouping | `project_parent` + `project_group` |
| Programme/department classification | `project_department` + `project_type` |
| Stakeholder registry | `project_stakeholder` |
| Reviewer assignment | `project_reviewer` |
| Template-based project creation | `project_template` |
| Timeline and pivot project analysis | `project_timeline` + `project_pivot` |
| Milestone/status structure | CE `project_milestone` + `project_milestone_status` |
| Task hierarchy / WBS | `project_task_ancestor` |
| Project governance shell / stage management | `project_task_stage_mgmt` |
| Project key/code | `project_key` |
| Tag-based categorization | `project_tag_hierarchy` |

### Must remain in thin custom delta (`ipai_finance_ppm`)

| Capability | Model |
|-----------|-------|
| Portfolio budget vs actual vs forecast | `ppm.budget.line` |
| Budget variance computation | Computed fields on budget lines |
| Portfolio health / RAG status | `ppm.portfolio.health` |
| Investment scoring / prioritization | `ppm.scoring` |
| Risk register | `ppm.risk` |
| Issue register | `ppm.issue` |
| Phase-gate / review objects | `ppm.gate.review` |
| Finance-portfolio dashboards | Pivot/graph views on delta models |

## 7. Explicit Non-Goals

- Rebuilding OCA project capabilities inside `ipai_finance_ppm`
- Treating `ipai_finance_ppm` as the monolithic Clarity replacement
- Claiming complete Clarity parity while known planning/dependency gaps remain
- Retaining deprecated external integration patterns inside the PPM core
- Full task dependency / CPM scheduling (known gap, `project_task_dependency` not ported)
- Interactive drag-and-drop Gantt (EE-only, no CE/OCA equivalent)

## 8. Success Metrics

- ≥80% Clarity PPM capability covered by CE + OCA + delta composition
- `ipai_finance_ppm` reduced to ≤6 custom models (budget, health, scoring, risk, issue, gate)
- Zero deprecated infrastructure code in PPM module
- All generic project-shell features served by CE/OCA, not custom code
- Known gaps documented in SSOT parity matrix
