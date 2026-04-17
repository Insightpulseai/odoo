# Screen-by-Screen Product Blueprint

> 9 screens mapped to purpose, reference, widgets, backing data, primary user, and surface.
> Design rule: Clarity for dashboards. SAP AFC for close cockpit. Joule for assistant. ADO for telemetry proof.

---

## Screen 1: Executive Control Tower

| Attribute | Value |
|-----------|-------|
| **Purpose** | Management overview of all finance, compliance, and delivery health |
| **Reference** | Clarity canvas + ADO overview dashboard |
| **Primary user** | Finance Director (CKVC), Senior Finance Manager (RIM) |
| **Surface** | Databricks One / SQL Dashboard |

**Widgets**

| Widget | Description |
|--------|-------------|
| KPI row (8 tiles) | Active projects, overdue tasks, filings at risk, evidence gaps, avg workload score, blockers count, milestones due this week, Pulser candidates |
| Risk heatmap | Project × risk dimension matrix (overdue, evidence gap, filing deadline) |
| Overdue list | Tasks past due date, sorted by days overdue, with owner and project columns |
| Bottleneck table | Approval stages with queue depth > threshold, assignee, and wait time |
| Workload bar chart | Per-person task count by status (open, in progress, blocked, done) |

**Backing data**

- `gold_ppm_project_health`
- `gold_ppm_task_workload`
- `gold_ppm_approval_bottlenecks`

---

## Screen 2: Close Cockpit

| Attribute | Value |
|-----------|-------|
| **Purpose** | March 2026 close phase plan with milestones, dependencies, and status |
| **Reference** | SAP Advanced Financial Closing |
| **Primary user** | Close Coordinator (JMSM), Finance Supervisor (BOM) |
| **Surface** | Databricks dashboard + Pulser summary |

**Widgets**

| Widget | Description |
|--------|-------------|
| Phase timeline | Horizontal strip showing Pre-Close, Active Close, Review, and Sign-Off phases with current phase highlighted |
| Milestone checklist | Ordered list of milestones with status badge (complete / in progress / blocked / not started) and due date |
| Task list by stage | Filterable table of tasks grouped by close stage, with owner, status, and evidence status columns |
| Blocker highlights | Inline highlight rows for tasks flagged as blocked, with blocker description and escalation path |
| Evidence status | Per-task column showing evidence attached / partial / missing with deadline proximity flag |

**Backing data**

- `gold_ppm_milestone_status` (filtered to PRJ-001)
- `bronze.ppm_tasks` (filtered to PRJ-001)

---

## Screen 3: Filing Readiness Board

| Attribute | Value |
|-----------|-------|
| **Purpose** | BIR Q1 + Annual filing status with deadline chains |
| **Reference** | SAP Tax Compliance + Odoo 19 tax return |
| **Primary user** | Tax Compliance Staff (JLI), Finance Director (CKVC) |
| **Surface** | Databricks dashboard |

**Widgets**

| Widget | Description |
|--------|-------------|
| Filing rows (2550Q, 1601-EQ, 1702) | One row per BIR form: form number, period, statutory deadline, readiness %, owner, evidence status, blocker flag |
| Readiness % gauge | Per-filing readiness score with threshold bands (green ≥ 80%, amber 50–79%, red < 50%) |
| Blockers column | Inline cell showing blocking condition for each filing row (missing attachment, pending approval, unreconciled variance) |
| Owner column | Assigned staff member per filing with status badge |
| Evidence status column | Count of attached vs required supporting documents per filing |

**Backing data**

- `gold_ppm_milestone_status` (filtered to PRJ-002, PRJ-003)
- `gold_ppm_evidence_gap_analysis`

---

## Screen 4: Workload & Bottleneck Dashboard

| Attribute | Value |
|-----------|-------|
| **Purpose** | Who has the most work, where are bottlenecks |
| **Reference** | Clarity canvas widgets + Databricks control tower |
| **Primary user** | Daily monitor (JPAL), Finance Director (CKVC) |
| **Surface** | Databricks One |

**Widgets**

| Widget | Description |
|--------|-------------|
| Workload by person (bar) | Horizontal bar chart showing total open task count per team member, color-coded by status |
| Stage distribution (stacked bar) | Stacked bar showing task volume by close/compliance stage across all active projects |
| Bottleneck score | Table of approval stages ranked by bottleneck score (queue depth × wait time), with assignee and project columns |
| Overdue list | Tasks past SLA by person, with project, due date, and days overdue columns |

**Backing data**

- `gold_ppm_task_workload`
- `gold_ppm_approval_bottlenecks`

---

## Screen 5: Evidence & Issue Review Board

| Attribute | Value |
|-----------|-------|
| **Purpose** | Track missing evidence, partial documentation, and exception queue |
| **Reference** | Clarity table widget + SAP compliance feel |
| **Primary user** | Reviewers (RMQB, JRMO), Tax Compliance (JLI) |
| **Surface** | Databricks dashboard |

**Widgets**

| Widget | Description |
|--------|-------------|
| Evidence gap table | Sortable table of all evidence gaps: task name, project, owner, gap type (missing / partial), deadline, deadline risk flag |
| Missing count by person | Bar chart showing number of missing evidence items per owner, sorted descending |
| Partial vs missing pie | Donut chart showing proportion of partial vs fully missing evidence items across all active projects |

**Backing data**

- `gold_ppm_evidence_gap_analysis`

---

## Screen 6: Automation Candidates Board

| Attribute | Value |
|-----------|-------|
| **Purpose** | Which tasks should Pulser automate first |
| **Reference** | Notion 3.0 agent workspace + control tower |
| **Primary user** | Analytics Lead (CKVC), Finance Supervisor (BOM) |
| **Surface** | Databricks dashboard |

**Widgets**

| Widget | Description |
|--------|-------------|
| Candidate ranked list | Table of tasks ranked by automation priority score, with task name, project, category, and Pulser-ready flag |
| Task category grouping | Group-by panel collapsing candidate tasks into categories (reconciliation, evidence collection, filing preparation, approval routing) |
| Pulser-ready flag filter | Toggle filter showing only tasks flagged as Pulser-ready (data complete, rule deterministic, low blast radius) |

**Backing data**

- `gold_ppm_pulser_candidate_tasks`

---

## Screen 7: Genie — Finance Operations

| Attribute | Value |
|-----------|-------|
| **Purpose** | Natural language Q&A over finance workload and control data |
| **Reference** | Notion 3.0 domain search + Databricks Genie |
| **Primary user** | JPAL (daily monitor), CKVC (on demand) |
| **Surface** | Databricks One Chat / Genie Space |

**Example questions**

- "What filings are at risk?"
- "Who has the most work?"
- "What evidence is missing?"
- "Which tasks are overdue in the close project?"
- "Show me the bottleneck summary for this week."

**Backing data**

- `gold_ppm_project_health`
- `gold_ppm_task_workload`
- `gold_ppm_approval_bottlenecks`
- `gold_ppm_evidence_gap_analysis`

---

## Screen 8: Genie — Compliance & Tax

| Attribute | Value |
|-----------|-------|
| **Purpose** | Natural language Q&A over compliance milestones and filing readiness |
| **Reference** | Notion 3.0 domain search + Databricks Genie |
| **Primary user** | JLI (Tax Compliance), CKVC |
| **Surface** | Databricks One Chat / Genie Space |

**Example questions**

- "What milestones are overdue?"
- "Which tasks are Pulser candidates?"
- "Show filing readiness for Q1."
- "What evidence is still missing for the 2550Q?"
- "Which filings have no owner assigned?"

**Backing data**

- `gold_ppm_milestone_status`
- `gold_ppm_evidence_gap_analysis`
- `gold_ppm_pulser_candidate_tasks`

---

## Screen 9: Pulser Assistant Panel

| Attribute | Value |
|-----------|-------|
| **Purpose** | Guided actions inside Odoo — summaries, evidence requests, blocker explanations |
| **Reference** | SAP Joule |
| **Primary user** | All finance staff, especially JMSM (Close Coordinator) and JLI (Tax Compliance) |
| **Surface** | Odoo systray / Pulser chat widget |

**Interactions**

| Trigger | Pulser response |
|---------|----------------|
| "Show March close blockers" | Structured card listing blocked milestones with owner, blocker description, and suggested next action |
| "Draft evidence request for missing VAT support" | Pre-populated draft message to task owner requesting specific missing attachment, with deadline context |
| "Summarize for FD" | Executive-format summary of current close and filing status, suitable for Finance Director briefing |
| "What is overdue in compliance?" | Table of overdue compliance tasks with owner, days overdue, and escalation recommendation |
| "Which tasks can Pulser handle?" | Ranked list of Pulser-candidate tasks from active projects with readiness flag and category |

**Backing data**

- Odoo `project.task` (live record access via Odoo ORM)
- `gold_ppm_project_health`, `gold_ppm_task_workload`, `gold_ppm_approval_bottlenecks`, `gold_ppm_evidence_gap_analysis` via `ipai-odoo-mcp`

---

## Design Rule

> Clarity for dashboards. SAP AFC for close cockpit. Joule for assistant behavior. ADO for live telemetry proof.

Every screen inherits exactly one reference for its primary interaction pattern.
Mixing reference patterns within a single screen is not permitted.
Reference borrowing applies to layout and interaction grammar only — visual styling follows IPAI design tokens, not the reference product's brand.

---

*SSOT: `docs/product/screen-by-screen-blueprint.md`*
*Last updated: 2026-04-15*
