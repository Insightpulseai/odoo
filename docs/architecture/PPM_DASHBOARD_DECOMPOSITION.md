# PPM OKR Dashboard — CE + OCA + Delta Decomposition

> Replaces the monolithic 52KB HTML dashboard with native Odoo CE 18 views,
> OCA modules, and a thin ipai_finance_ppm delta.
>
> Principle: Config -> OCA -> Delta.

---

## Current state (before)

One standalone HTML file (`okr_dashboard.html`, 595 lines, 52KB) with:
- Hardcoded static data (all values at 0%)
- ECharts loaded from Cloudflare CDN
- Google Fonts loaded externally
- Raw `fetch()` to Odoo RPC (no CSRF)
- References to deprecated Supabase, n8n, Odoo 19.0
- No OWL component bridge — `ir.actions.client` action has no matching JS handler
- Not aligned with `enterprise_okrs.yaml` SSOT

## Target state (after)

Native Odoo views + OCA modules + thin OKR model delta.

---

## Decomposition matrix

### What CE 18 already provides (use as-is)

| Dashboard section | CE feature | How to use |
|---|---|---|
| Task execution | `project.task` kanban/list/form | Group by stage, filter by project |
| Task burndown | `project.task` graph view | Bar/line by create_date, grouped by stage |
| Team workload | `project.task` pivot view | Rows: assignee, Columns: stage, Values: count |
| Milestones | `project.milestone` (CE 18 core) | Milestone list per project |
| Task dependencies | `project.task` depends_on | Native dependency tracking |
| Recurring tasks | `project.task` recurring | Monthly close / tax cadence |
| Scheduled activities | `mail.activity` | Review/approval follow-ups |
| Task logs | `project.task` timesheet | Effort/timing evidence |
| Stage distribution | `project.task` graph view (pie) | Pie chart by stage_id |
| Calendar | `project.task` calendar view | Due date visualization |

### What OCA 18 provides (adopt)

| Dashboard section | OCA module | Repo | What it adds |
|---|---|---|---|
| KPI / financial metrics | `mis_builder` | OCA/mis-builder | KPI report builder, period comparison, budget overlay |
| Budget vs actual comparison | `mis_builder_budget` | OCA/mis-builder | Budget lines integrated into MIS reports |
| Project pivot | `project_pivot` | OCA/project | Pivot view on `project.project` |
| Project timeline | `project_timeline` | OCA/project | Timeline/Gantt-like view |
| Task stage states | `project_task_stage_state` | OCA/project | Map stages to states (draft/open/done/cancelled) |
| GL / Trial Balance | `account_financial_report` | OCA/account-financial-reporting | Standard financial reports |
| Computed pivot measures | `web_pivot_computed_measure` | OCA/web | Derived measures in pivot views |

### What ipai_finance_ppm delta provides (keep + extend)

| Model | Purpose | Status |
|---|---|---|
| `ppm.budget.line` | Budget vs forecast vs actual per project per period | Keep |
| `ppm.portfolio.health` | RAG status and health scoring | Keep |
| `ppm.risk` | Risk register (probability x impact) | Keep |
| `ppm.issue` | Issue register with priority/state | Keep |
| `ppm.scoring` | Investment scoring / prioritization | Keep |
| `ppm.gate.review` | Phase-gate review governance | Keep |
| **`ppm.okr.objective`** | **OKR objective with computed health** | **New** |
| **`ppm.okr.key_result`** | **Key result with target/actual/score/RAG** | **New** |

---

## New OKR models (thin delta)

### `ppm.okr.objective`

```
Fields:
  name            Char        "O1 — Faster finance execution"
  code            Char        "O1" (unique)
  description     Text
  project_id      Many2one    project.project
  owner_id        Many2one    res.users
  review_cadence  Selection   weekly / biweekly / monthly
  key_result_ids  One2many    ppm.okr.key_result
  status          Selection   on_track / at_risk / off_track / blocked (computed)
  score           Float       0.0-1.0 (computed: avg of KR scores)
  period_start    Date
  period_end      Date
```

### `ppm.okr.key_result`

```
Fields:
  name            Char        "Median upload-to-draft-ready < 3 min"
  code            Char        "KR1" (unique per objective)
  objective_id    Many2one    ppm.okr.objective
  owner_id        Many2one    res.users
  metric_source   Char        "SC-PH-03" (cross-ref to SMART criteria)
  unit            Char        "minutes" / "%" / "count" / "currency"
  baseline        Float
  target          Float
  current         Float
  score           Float       0.0-1.0 (computed)
  status          Selection   on_track / at_risk / off_track / blocked (computed)
  trend           Selection   improving / stable / declining
  last_measured   Datetime
  escalation_path Text
  notes           Text
```

---

## View replacement map

| Old HTML section | Replacement |
|---|---|
| Overall progress ring | `ppm.okr.objective` kanban view (RAG cards) |
| Objective donuts (O1-O5) | `ppm.okr.objective` kanban with progress widget |
| KR table | `ppm.okr.key_result` list view with inline progress bars |
| Team rings | `project.task` pivot (assignee x stage) — CE native |
| Burndown chart | `project.task` graph view (line, by date) — CE native |
| Velocity chart | `project.task` graph view (bar + line) — CE native |
| Stage pie | `project.task` graph view (pie, by stage) — CE native |
| Quarterly KPIs | `mis_builder` report — OCA |
| Logframe | `ppm.okr.objective` + `ppm.okr.key_result` hierarchy — delta |
| WBS / Gantt | `project_timeline` — OCA |
| Team workload | `project.task` pivot (assignee x stage) — CE native |
| Tax filing | Separate `ppm.okr.objective` for O4 (PH tax) — delta |
| Issues | `ppm.issue` list/kanban — existing delta |
| Milestones | `project.milestone` — CE native |

---

## Files to remove

| File | Reason |
|---|---|
| `static/src/html/okr_dashboard.html` | Replaced by native views |
| `views/okr_dashboard_action.xml` | No longer needed (was bridge to HTML) |

---

## Dependencies to add

```python
"depends": [
    "project",
    "account",
    "analytic",
    "mail",
    "board",           # CE: "My Dashboard" portlets
    # OCA (add when hydrated in addons-path):
    # "mis_builder",
    # "project_timeline",
    # "project_task_stage_state",
]
```

---

## Menu structure (updated)

```
Finance PPM (root)
├── OKR Dashboard        → ppm.okr.objective kanban (executive view)
├── Key Results           → ppm.okr.key_result list
├── Objectives            → ppm.okr.objective list/form
├── Budget Lines          → ppm.budget.line (existing)
├── Portfolio Health      → ppm.portfolio.health (existing)
├── Risk Register         → ppm.risk (existing)
├── Issue Tracker         → ppm.issue (existing)
├── Investment Scoring    → ppm.scoring (existing)
├── Gate Reviews          → ppm.gate.review (existing)
└── Configuration
    └── Import Wizard     → ppm.import.wizard (existing)
```

---

## OKR set for dashboard (O1-O6)

| Code | Objective | SC-PH Coverage |
|---|---|---|
| O1 | Faster finance execution | SC-PH-01, SC-PH-02, SC-PH-03 |
| O2 | Stronger control and correctness | SC-PH-04, SC-PH-05, SC-PH-13 |
| O3 | Cash advance discipline | SC-PH-08, SC-PH-09 |
| O4 | PH tax and BIR readiness | SC-PH-10, SC-PH-11, SC-PH-23, SC-PH-24 |
| O5 | Faster and safer close | SC-PH-12 |
| O6 | AI financial discipline | SC-PH-14, SC-PH-15, SC-PH-16, SC-PH-17, SC-PH-18 |

---

## Documents integration (thin delta)

Documents integration is thin-delta, not a new document system.

Use existing Odoo Documents as the retained-copy substrate.
The delta should only add:
- linkage fields / metadata conventions
- evidence completeness computation
- missing-evidence status computation
- dashboard widgets that read retained-copy presence

### Required dashboard widgets

| Widget | Source | Purpose |
|--------|--------|---------|
| Evidence Completeness | % of KR/milestone-linked workflows with retained copies in Documents | Launch blocker |
| Document Grounding Coverage | % of finance-critical Pulser answers backed by Documents artifacts | Grounding quality |
| Missing Evidence Queue | Tasks/milestones blocked by absent retained copies | Operational blocker |

### Canonical Documents directory tree

```
Documents/
  Finance PPM/
    00-Executive-OKRs/
    01-AP/
    02-AR/
    03-Expenses/
    04-Cash-Advance/
    05-PH-Tax/
    06-BIR-Ready/
    07-Close/
    08-Approvals/
    09-External-Confirmations/
    99-Archive/
```

Each lane retains copies by year and fiscal period:
```
Finance PPM/01-AP/2026/2026-04/
Finance PPM/04-Cash-Advance/2026/2026-04/
```

---

## Office Artifact Pipeline

### Architecture

The Professional Office Skills layer sits between the Finance PPM dashboard and the Documents vault. It generates publishable artifacts (PPTX, DOCX, XLSX) from Odoo data, retains copies in Documents, and feeds grounding context back to Pulser.

```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│  Finance PPM        │    │  Office Studios      │    │  Odoo Documents     │
│  Dashboard          │───▸│  (PPT/Word/Excel)    │───▸│  Vault              │
│                     │    │                      │    │                     │
│  - OKR scores       │    │  1. Inputs (records,  │    │  - Source files      │
│  - KR metrics       │    │     PPM, Documents)   │    │  - Derivative pubs   │
│  - Evidence status  │    │  2. Grounding         │    │  - Retained copies   │
│  - Blocker queue    │    │  3. Studio generation  │    │  - Trace links       │
│                     │    │  4. QA & review        │    │                     │
│                     │◂───│  5. Publish + retain   │◂───│  - Pulser retrieval  │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
```

### Studios

| Studio | Inputs | Outputs | Quality gates |
|--------|--------|---------|---------------|
| PowerPoint Studio | PPM OKRs, metrics, retained visuals | PPTX / PDF deck | Story flow, no overflow, render QA |
| Word Studio | Documents, policies, approvals | DOCX / PDF document | Page hierarchy, citations, signoff |
| Excel Studio | Record metrics, OKRs, formulas | XLSX workbook | Formula integrity, recalc, render QA |

### Publish gate

No finance office artifact is considered complete without passing all four gates:

1. Content is grounded in Odoo / Documents / approved knowledge.
2. Artifact renders cleanly with no overflow, overlap, or broken layout.
3. Reviewer notes are resolved and retained copies are stored in Odoo Documents.
4. Final output is ready to circulate externally without reformatting.

### Documents directory extension

Office artifacts are retained in the existing Documents tree under a dedicated lane:

```
Documents/
  Finance PPM/
    00-Executive-OKRs/
      publishable/          ← generated decks, workbooks, docs
    01-AP/
    ...
    10-Office-Artifacts/    ← cross-lane publishable outputs
      2026/
        2026-04/
          exec-deck-*.pptx
          close-pack-*.docx
          okr-dashboard-*.xlsx
```

---

*Last updated: 2026-04-11*
