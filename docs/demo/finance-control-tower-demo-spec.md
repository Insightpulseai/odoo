# Finance Control Tower Demo Spec — March 2026 Close + Q1/Annual BIR Filing

> **Locked:** 2026-04-17
> **Demo headline:** From Close to Filing: March 2026 Finance Control Tower
> **Benchmarks:** SAP Advanced Financial Closing, SAP Tax Compliance, Broadcom Clarity PPM
> **Operating period:** March 2026 month-end close
> **Compliance period:** Q1 2026 filings + Annual 2025 income tax filing
> **Stack:** Odoo/Pulser (do the work) + Databricks/Genie (understand the work)

---

## Demo promise

Show that the solution can:
- Orchestrate the close like SAP Advanced Financial Closing
- Validate tax/compliance readiness like SAP Tax Compliance
- Visualize phases, milestones, and dashboards like Clarity PPM
- Let users act through Pulser
- Let management understand through Databricks / Genie

**Do NOT demo this as "an ERP doing accounting."**
**Demo it as: Finance Operations Control Tower for March 2026 Close and April 2026 BIR Readiness.**

---

## The 5 demo modules

### Module 1 — Close Calendar / Phase Plan (AFC + Clarity equivalent)

**Close phases:**
1. Pre-close
2. Transaction cutoff
3. Reconciliations
4. Accruals / amortization
5. Tax pack prep
6. Review
7. Approval
8. Filing readiness

**Milestones:**
- "March books soft closed"
- "VAT reconciliation complete"
- "Q1 tax pack approved"
- "Annual return ready for signoff"

**Tasks and to-dos** by person / role / date — per `fact_finance_task_schedule`

### Module 2 — Tax Compliance Check Cockpit (SAP Tax Compliance equivalent)

**Rule checks:**
- Missing VAT mappings
- EWT inconsistencies
- Missing supporting schedules
- Unreconciled tax-sensitive accounts
- Late approval paths

**Issue severity levels:**
- Blocker
- Warning
- Informational

**Pulser should say things like:**
- "Q1 VAT return is blocked because two zero-rated transactions lack support"
- "Annual 1702 pack is missing tax adjustment workpaper"
- "Three EWT lines are posted but not linked to the expected withholding schedule"

### Module 3 — BIR Filing Readiness Board

**Rows (forms):**

| BIR Form | Description | Period |
|---|---|---|
| 2550Q | Quarterly VAT Return | Q1 2026 |
| 1601-EQ | Quarterly Expanded Withholding Tax | Q1 2026 |
| 1702 | Annual Corporate Income Tax | FY 2025 |
| 1604-CF | Annual Info Return (Compensation + Final) | FY 2025 |
| QAP/SAWT | Quarterly Alphalist of Payees | Q1 2026 |

**Columns:**

| Column | Purpose |
|---|---|
| Filing deadline | BIR regulatory deadline |
| Prep due | Internal preparation target |
| Review due | Internal review target |
| Approval due | Internal approval target |
| Current readiness % | Completion indicator |
| Blockers | Unresolved issues count |
| Owner | Assigned person code |
| Evidence complete? | Supporting docs status |
| Payment approval complete? | Finance director sign-off |

**Important:** Deadlines must be **data-driven** (from `fact_bir_deadline_control`), not hardcoded. BIR circulars can change filing treatment for a given year.

### Module 4 — Workload / Bottleneck Dashboard (Databricks control tower)

**Visualizations:**
- Workload by employee (bar chart)
- Workload by stage: Preparation / Review / Approval (stacked bar)
- Bottleneck map by reviewer / approver (heatmap)
- Close compression risk (timeline with today marker)
- Overdue / at-risk tasks (flagged list)
- Automation candidate score (ranked bar)

**Source:** `fact_finance_workload_snapshot` + `fact_close_step_status`

**This proves:** Databricks = understand the business

### Module 5 — Pulser Guided Actions

**Demo prompts:**
- "Show me all March close blockers"
- "Who still owes support for Q1 VAT?"
- "Draft the evidence request for unresolved EWT items"
- "Open the reviewer queue for annual income tax pack"
- "Generate the close summary for the finance director"

**Pulser rules in demo:**
- Pulser does NOT file directly
- Pulser explains, routes, requests evidence, summarizes, prepares handoffs, stages outputs
- Human approval is always required for filing actions

---

## Demo storyboard

### Scene 1 — Executive overview (30 seconds)

Open the Finance Control Tower dashboard:
- 3 filing obligations (2550Q, 1601-EQ, 1702)
- 2 blocked, 1 at risk
- 4 high-risk bottlenecks
- Busiest approver = [name from dim_finance_person]
- Biggest recurring task category = [from dim_task_category]

### Scene 2 — March close phase view (60 seconds)

Open the close plan:
- 8 phases with milestones
- Tasks by assignee with due dates
- Status indicators (not started → in progress → review → approved → completed)
- Click into a blocked task → see the dependency chain

### Scene 3 — Tax exception review (60 seconds)

Open the tax compliance cockpit:
- Unresolved VAT mismatch (blocker)
- EWT exception (warning)
- Missing annual return workpaper (blocker)
- Evidence gap summary
- Click "Request evidence" → Pulser drafts the email

### Scene 4 — Databricks / Genie question (45 seconds)

Ask in Genie (Databricks One Chat):
- "What filings are most at risk this month?"
- "Which reviewer is overloaded?"
- "Which recurring tasks should be automated first?"

Show the NL→SQL response grounded in gold marts.

### Scene 5 — Pulser action (45 seconds)

Ask Pulser in Odoo:
- "Generate a close-blocker summary for the FD"
- "Draft the evidence request email for missing VAT support"
- "Show me all tasks assigned to CKVC before filing approval"

Show Pulser staging the output for human review — not auto-executing.

**Total demo time: ~4 minutes**

---

## Source tables

| Table | Status | Source |
|---|---|---|
| `finance_directory` | Active — 10 team members seeded | Finance workbook |
| `monthly_task_schedule` | Active — 9 categories, 3 stages | Finance workbook |
| `bir_deadlines` | Active — contract defined | BIR calendar + circulars |
| `tax_exceptions` | Planned | Odoo tax account analysis |
| `evidence_registry` | Planned | Document management / attachments |
| `close_status` | Planned | Close step tracking |
| `approval_events` | Planned | Odoo approval workflow log |

---

## Gold marts

| Mart | Source facts | Demo module |
|---|---|---|
| `gold_finance_bir_deadline_control` | `fact_bir_deadline_control` | Module 3 (Filing Readiness) |
| `gold_finance_close_workload` | `fact_finance_task_schedule` + `fact_finance_workload_snapshot` | Module 4 (Workload) |
| `gold_finance_role_bottlenecks` | `fact_finance_workload_snapshot` | Module 4 (Bottleneck) |
| `gold_finance_compliance_control_tower` | `fact_bir_deadline_control` + `fact_close_step_status` | Module 1 + 3 |
| `gold_finance_automation_candidates` | `fact_finance_task_schedule` | Module 4 (Automation) |

---

## Genie spaces

| Space | Domain | Demo module | Example questions |
|---|---|---|---|
| Finance Operations | finance_ops | Module 4 | "Who has the most approval tasks?" / "Which categories consume most effort?" |
| Compliance & Tax | tax_compliance | Module 3 | "What filings are at risk?" / "Which forms have tightest internal lead time?" |

---

## Demo KPIs (8)

| # | KPI | Source | Demo module |
|---|---|---|---|
| 1 | Filings due in next 7 days | `fact_bir_deadline_control` | Module 3 |
| 2 | Filings with unresolved blockers | Tax exception cockpit | Module 2 |
| 3 | Close tasks overdue | `fact_close_step_status` | Module 1 |
| 4 | Reviewer bottleneck score | `fact_finance_workload_snapshot` | Module 4 |
| 5 | Approval bottleneck score | `fact_finance_workload_snapshot` | Module 4 |
| 6 | Evidence completeness % | Evidence registry | Module 2 |
| 7 | Recurring task volume | `fact_finance_task_schedule` | Module 4 |
| 8 | Automation candidate score | `fact_finance_task_schedule` | Module 4 |

---

## OKR framing (Clarity-style)

**Objective:**
Complete March 2026 close and statutory filing preparation on time with no unresolved critical exceptions.

| Key Result | Metric | Target |
|---|---|---|
| KR1 | Critical March close tasks completed by internal target date | 100% |
| KR2 | Q1 filing packs review-ready before approval cutoff | 100% |
| KR3 | Unresolved blocker-level tax exceptions at filing submission | 0 |
| KR4 | Reviewer bottleneck concentration | Below threshold |

---

## What to borrow from each benchmark

| Benchmark | Borrow | Do NOT borrow |
|---|---|---|
| **SAP Advanced Financial Closing** | Calendarized close orchestration, task dependency mindset, close cockpit feel | SAP's specific ABAP/Fiori tech stack |
| **SAP Tax Compliance** | Issue/check cockpit, rule-based exception detection, filing-readiness validation | SAP's Dataverse/CDS dependency |
| **Clarity PPM** | Phases, milestones, tasks/to-dos, dashboard canvas, OKR framing | Clarity's project-centric data model (we use Odoo project.*) |
| **IPAI stack** | Databricks for marts/dashboards/Genie, Pulser for guided action, Odoo as business runtime | Nothing — this is our stack |

---

## Pulser demo scripts

### Script 1 — Close blocker summary
```
User: "Generate a close-blocker summary for the finance director"
Pulser: "March 2026 Close — Blocker Summary (generated 2026-04-17)

3 blockers identified:
1. Q1 VAT reconciliation — 2 zero-rated transactions lack supporting documentation
   Owner: JAP (Jinky Paladin) | Due: 2026-04-10 | Status: BLOCKED
   Action needed: Evidence request to vendor for invoice classification

2. Annual 1702 tax adjustment — workpaper not uploaded
   Owner: CKVC (Khalil Vera Cruz) | Due: 2026-04-12 | Status: BLOCKED
   Action needed: Complete tax adjustment computation and upload

3. EWT Q1 schedule — 3 lines posted without withholding linkage
   Owner: LAS (Amor Lasaga) | Due: 2026-04-08 | Status: OVERDUE
   Action needed: Match EWT lines to 2307 certificates

Shall I draft evidence request emails for items 1 and 3?"
```

### Script 2 — Evidence request draft
```
User: "Draft the evidence request for the missing VAT support"
Pulser: "Subject: Evidence Request — Q1 2026 VAT Zero-Rated Support

To: [Vendor contact]
From: JAP (Jinky Paladin), Finance Operations

Dear [Vendor],

We are preparing our Q1 2026 VAT return (BIR Form 2550Q) and require
supporting documentation for the following zero-rated transactions:

- Invoice #[XXX] dated 2026-02-15 — PHP [amount]
- Invoice #[XXX] dated 2026-03-22 — PHP [amount]

Please provide the export declaration or proof of zero-rating eligibility
by 2026-04-08 to ensure timely filing.

---
This is a staged draft. Shall I send it or open it in your email client?"
```

### Script 3 — Task lookup by person
```
User: "Show me all tasks assigned to CKVC before filing approval"
Pulser: "Tasks assigned to CKVC (Khalil Vera Cruz) before filing approval:

| Task | Category | Stage | Due | Status |
|---|---|---|---|---|
| Annual tax adjustment workpaper | Tax & provisions | Preparation | 2026-04-12 | BLOCKED |
| 1702 supporting schedules | Tax & provisions | Preparation | 2026-04-13 | Not started |
| Q1 EWT reconciliation review | Tax & provisions | Review | 2026-04-15 | Not started |
| March amortization entries | Amortization | Preparation | 2026-04-05 | Completed |

2 of 4 pending tasks are on the critical path for filing approval.
Shall I flag these as high-priority in the close dashboard?"
```

---

## Success criteria

The demo succeeds if the audience can answer YES to all of these:

- [ ] Can I see which filings are at risk right now? (Module 3)
- [ ] Can I see who is the bottleneck? (Module 4)
- [ ] Can I understand the close timeline and what's overdue? (Module 1)
- [ ] Can I ask a business question in natural language and get a grounded answer? (Module 4 — Genie)
- [ ] Can the system draft an action for me that I can approve? (Module 5 — Pulser)
- [ ] Is the system safer than a spreadsheet? (OKR + evidence + approval chain visible)
- [ ] Could this be deployed for my team? (Repeatable, not custom-coded per demo)

---

## What this is NOT

- NOT a full ERP demo (Odoo is backstage)
- NOT a model/AI capability demo (models are tools, not the product)
- NOT a dashboard-only demo (Pulser actions are the differentiator)
- NOT a synthetic scenario (use real team names, real BIR forms, real deadlines)

---

## Pre-demo checklist

- [ ] Gold marts populated in `ipai_dev.gold.*` (DLT pipeline run)
- [ ] Genie Space "Finance Operations" created on gold tables
- [ ] Genie Space "Compliance & Tax" created on gold tables
- [ ] Databricks One Chat enabled (Beta preview toggle)
- [ ] Dashboard published with 8 KPIs
- [ ] Pulser responding on Odoo with finance-ops behavior profile
- [ ] BIR deadline calendar loaded with March/April 2026 dates
- [ ] Tax exception seed data loaded (3 blockers for demo)
- [ ] Evidence registry scaffolded (at least 3 evidence items)
- [ ] Finance directory populated (10 team members confirmed)

---

*Last updated: 2026-04-17*
