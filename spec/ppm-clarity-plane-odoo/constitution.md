# Constitution — PPM Clarity for Odoo 18

## 1. Purpose

Deliver a Clarity PPM-equivalent project portfolio management capability
in Odoo 18 by composing CE + OCA + thin custom delta, not by building
a monolithic replacement module.

## 2. Architecture Doctrine

### 2.1 CE + OCA first for PPM

The Clarity PPM replacement strategy for Odoo 18 must use:

1. **Odoo CE 18 `project`** as the base project-execution surface
2. **OCA `project`** modules as the default extension path for hierarchy,
   roles, stakeholders, timeline, analytics, review, and governance
3. A **thin `ipai_finance_ppm` delta module** only for portfolio-finance
   features not already covered by CE/OCA

The implementation must not recreate in custom code any capability already
available in:
- Odoo CE `project`
- OCA `project`
- OCA `timesheet`

### 2.2 `ipai_finance_ppm` scope restriction

`ipai_finance_ppm` is not the primary PPM foundation.
It is a **delta-only addon**.

It may own only:
- portfolio budget / forecast / variance
- portfolio health / RAG
- stage-gate / phase review objects if not covered by OCA
- risk / issue register
- scoring / prioritization
- capacity-vs-demand or finance-portfolio controls not available in CE/OCA

It must not own:
- generic project hierarchy (→ `project_parent`)
- generic project roles (→ `project_role`)
- generic stakeholders (→ `project_stakeholder`)
- generic project timeline views (→ `project_timeline`)
- generic project pivot analytics (→ `project_pivot`)
- generic project templates (→ `project_template`)
- generic task hierarchy / WBS features (→ `project_task_ancestor`)
- deprecated external event-bus residue unrelated to current platform doctrine

### 2.3 Clarity equivalence rule

The target is not "clone Clarity in one custom module".
The target is:
- CE/OCA-native where possible
- thin delta where necessary
- explicit gap documentation where parity is not yet achievable

Known planning/dependency gaps (e.g. `project_task_dependency` not ported)
must be documented instead of hidden by parity claims.

## 3. Mandatory Guardrails

### 3.1 No capability duplication
If CE or OCA provides it, the delta module must not reimplement it.

### 3.2 No deprecated infrastructure
The PPM module must not contain Supabase webhook/event-bus code, n8n
workflow bindings, or other deprecated integration patterns. External
service integration follows current platform doctrine (Azure-native).

### 3.3 No unrelated coupling
The PPM module must not own HR expense AI drafting, copilot tool bindings,
or other features outside portfolio management scope.

### 3.4 Multi-company by default
All delta models must use `company_id` fields and respect multi-company
rules, consistent with CE/OCA project behavior.

## 4. OCA Baseline Modules (Odoo 18)

These OCA modules form the structural foundation and must be treated as
the primary implementation layer before any custom code is written:

| Module | Capability |
|--------|-----------|
| `project_parent` | Portfolio hierarchy (parent-child projects) |
| `project_group` | Programme grouping |
| `project_department` | Department-based project classification |
| `project_stakeholder` | Stakeholder registry |
| `project_role` | Role-based resource assignment |
| `project_timeline` | Timeline / Gantt view |
| `project_pivot` | Pivot analytics |
| `project_milestone_status` | Milestone status reporting |
| `project_template` | Repeatable project blueprints |
| `project_key` | Project identifier / shortcode |
| `project_tag_hierarchy` | Hierarchical categorization |
| `project_task_ancestor` | Task hierarchy / WBS |
| `project_task_parent_completion_blocking` | Dependency enforcement |
| `project_reviewer` | Review/approval gates |
| `project_task_stage_mgmt` | Advanced stage management |
| `project_type` | Project type classification |

## 5. Known Gaps

| Gap | Impact | Status |
|-----|--------|--------|
| `project_task_dependency` | Task dependency chains / CPM | Not ported to OCA 18.0 |
| Interactive drag-and-drop Gantt | Resource leveling | EE-only, no OCA equivalent |
| Portfolio-level resource capacity | Demand vs supply planning | Requires custom delta |
