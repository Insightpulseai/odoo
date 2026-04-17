# Capability Matrix v1 — Pulser for Odoo Finance Control Tower

> Benchmarked against SAP AFC, SAP Joule, SAP Tax Compliance, AvaTax, Notion 3.0, Odoo 19 native capabilities.
> Key principle: compete on visibility, intelligence, and guided assistance — not raw ERP feature count.

---

## Key Principle

Do not compete with Odoo 19 on raw native feature count. Compete on:

- **Better workflow visibility** — real-time close cockpit, filing readiness board, payment state tracking
- **Better control-tower intelligence** — deadline risk scoring, automation candidate scoring, bottleneck analytics
- **Better guided assistance** — Pulser plain-language summaries, role-aware next-best-action, blocker explanations
- **Better finance/compliance operating experience** — evidence completeness tracking, payment-to-filing dependency mapping

---

## Full Capability Matrix (36 rows)

| # | Capability | Source Inspiration | Owner Layer | v1 | v1.1 | Later |
|---|---|---|---|---|---|---|
| 1 | Close calendar / phase plan | SAP AFC + Broadcom Clarity | Odoo + Databricks | must | — | — |
| 2 | Milestones, task, to-do model | SAP AFC + Clarity + Odoo | Odoo | must | — | — |
| 3 | Approval queue | SAP Finance Workflow | Odoo + Pulser | must | — | — |
| 4 | Approval bottleneck analytics | Databricks Control Tower | Databricks | must | — | — |
| 5 | Evidence completeness tracking | SAP Compliance | Odoo + Databricks | must | — | — |
| 6 | Evidence request drafting | SAP Joule + Notion 3.0 | Pulser | must | — | — |
| 7 | Blocker explanation | SAP Joule | Pulser | must | — | — |
| 8 | Close readiness summary | SAP AFC + Joule | Pulser + Databricks | must | — | — |
| 9 | Filing readiness board | Odoo 19 Tax Return | Databricks + Pulser | must | — | — |
| 10 | Tax obligation registry | Odoo 19 Tax Return | Databricks | must | — | — |
| 11 | Prep → review → approval deadline chain | Workbook + SAP | Databricks | must | — | — |
| 12 | Deadline risk scoring | Databricks Control Tower | Databricks | must | — | — |
| 13 | Recurring task burden analysis | Databricks + Notion | Databricks | must | — | — |
| 14 | Automation candidate scoring | Notion + Control Tower | Databricks | must | — | — |
| 15 | Pulser manager / FD summary | SAP Joule | Pulser | must | — | — |
| 16 | Payment approval queue | Odoo 19 Payment | Odoo + Pulser | must | — | — |
| 17 | Payment readiness state | Odoo 19 Payment | Databricks + Pulser | must | — | — |
| 18 | Withholding-on-payment review | Odoo 19 PH Localization | Odoo + Pulser | must | — | — |
| 19 | Payment evidence status | Compliance pattern | Odoo + Databricks | must | — | — |
| 20 | Payment-to-filing dependency | Compliance + Control Tower | Databricks | must | — | — |
| 21 | Bank / payment reconciliation visibility | Odoo Accounting | Odoo + Databricks | must | — | — |
| 22 | Genie domain spaces | Notion + Databricks | Databricks | must | — | — |
| 23 | Conversational analytics on Gold | Databricks + Notion | Databricks | must | — | — |
| 24 | Role-aware next-best-action | SAP Joule + Notion | Pulser | — | should | — |
| 25 | What changed since last review | SAP Joule | Pulser | — | should | — |
| 26 | Return validation checks | Odoo 19 Tax Return | Databricks + Pulser | — | should | — |
| 27 | Tax exception queue triage | SAP Tax Compliance | Databricks + Pulser | — | should | — |
| 28 | Official format export readiness | Odoo 19 PH Localization | Databricks | — | should | — |
| 29 | Pulser action handoff to Odoo | Architecture split | Pulser + Odoo | — | should | — |
| 30 | Workspace memory / cross-surface context | Notion 3.0 | Pulser + Databricks | — | should | — |
| 31 | DAT export automation | Odoo 19 PH | Odoo Bridge | — | — | defer |
| 32 | Full PH statutory pack automation | Odoo 19 PH | Odoo Bridge + Databricks | — | — | defer |
| 33 | Advanced ISO 20022 breadth | Odoo 19 Payment | Odoo Payment | — | — | defer |
| 34 | Broader payment provider sophistication | Odoo 19 Payment | Odoo Provider | — | — | defer |
| 35 | Native AI authoring inside ERP | Odoo 19 AI | Odoo + Pulser Bridge | — | — | defer |
| 36 | Multi-agent workspace orchestration | Notion + SAP Joule | Pulser + Databricks | — | — | defer |

---

## v1 Release Scope

### Must-Have (23 capabilities — ship with v1)

Close cockpit and orchestration:
- Close calendar / phase plan (#1)
- Milestones, task, to-do model (#2)
- Approval queue (#3)
- Approval bottleneck analytics (#4)
- Close readiness summary (#8)

Evidence and compliance:
- Evidence completeness tracking (#5)
- Evidence request drafting (#6)
- Blocker explanation (#7)

Filing readiness:
- Filing readiness board (#9)
- Tax obligation registry (#10)
- Prep → review → approval deadline chain (#11)
- Deadline risk scoring (#12)

Operational intelligence:
- Recurring task burden analysis (#13)
- Automation candidate scoring (#14)
- Pulser manager / FD summary (#15)

Payment control:
- Payment approval queue (#16)
- Payment readiness state (#17)
- Withholding-on-payment review (#18)
- Payment evidence status (#19)
- Payment-to-filing dependency (#20)
- Bank / payment reconciliation visibility (#21)

Analytics surface:
- Genie domain spaces (#22)
- Conversational analytics on Gold (#23)

### Should-Have (7 capabilities — target v1.1)

- Role-aware next-best-action (#24)
- What changed since last review (#25)
- Return validation checks (#26)
- Tax exception queue triage (#27)
- Official format export readiness (#28)
- Pulser action handoff to Odoo (#29)
- Workspace memory / cross-surface context (#30)

### Defer (6 capabilities — later releases)

- DAT export automation (#31)
- Full PH statutory pack automation (#32)
- Advanced ISO 20022 breadth (#33)
- Broader payment provider sophistication (#34)
- Native AI authoring inside ERP (#35)
- Multi-agent workspace orchestration (#36)

---

## Product Framing per Version

### v1 — Finance Control Tower

**Tagline**: Pulser gives your finance team a real-time control tower for close, compliance, and payments.

**What it does**: Orchestrates the monthly/quarterly close with a calendarized phase plan, tracks evidence completeness, surfaces approval bottlenecks, scores deadline risk, and provides plain-language summaries for managers and FDs. Payment approval and filing readiness boards are included.

**Benchmark positioning**: Comparable to SAP AFC + Joule in workflow orchestration; comparable to Databricks Control Tower in operational intelligence. Delivered on Odoo CE + OCA + Pulser — no ERP license premium.

### v1.1 — Guided Assistance Layer

**What it adds**: Role-aware next-best-action guidance so each persona (FD, AP clerk, tax analyst) sees what to do next and why. Return validation checks and tax exception queue triage reduce manual review loops. Pulser action handoff closes the loop between chat guidance and Odoo record mutation.

**Benchmark positioning**: Closes the gap to SAP Joule's guided finance experience and Notion 3.0 workspace intelligence.

### Later — Automation and Orchestration Depth

**What it adds**: PH statutory pack automation (DAT export, BIR eFiling feeds), full ISO 20022 payment breadth, multi-agent workspace orchestration, and native AI authoring inside the ERP surface.

**Gate**: These are deferred until v1 close cockpit and v1.1 guided assistance are in production and validated. They do not unblock go-live.

---

## Source Inspirations

| Code | Full reference |
|---|---|
| `sap_afc` | SAP Advanced Financial Closing — calendarized close orchestration, phase/milestone model, approval chains |
| `sap_tax_compliance` | SAP Tax Compliance — rule/check cockpit, exception triage, compliance scoring |
| `joule` | SAP Joule — plain-language finance guidance, role-aware next-best-action, plain-English blocker explanations |
| `odoo19_tax_return` | Odoo 19 tax return + PH localization — filing readiness, tax obligation registry, BIR format improvements |
| `odoo19_payment` | Odoo 19 payment flow enhancements — approval queues, readiness state, ISO 20022 improvements |
| `odoo19_ph_localization` | Odoo 19 PH BIR format/export improvements — DAT, eFiling, withholding certificates |
| `avatax` | Avalara AvaTax — compliance/tax-control expectations, audit trail, exception management |
| `notion` | Notion 3.0 — workspace/agent/search patterns, Genie spaces, cross-surface context memory |
| `clarity` | Broadcom Clarity PPM — phases/milestones/OKR, capacity planning, resource burn |
| `databricks_control_tower` | Databricks operational intelligence pattern — deadline risk scoring, automation candidate detection |

---

*Generated: 2026-04-15 | Branch: docs/capability-matrix-v1 | SSOT: ssot/product/capability-matrix.yaml*

---

## Addendum: D365 Finance + Project Ops + Business Central capabilities for demo

> Added 2026-04-17. Maps D365 feature marketing claims to demo-ready IPAI equivalents.

### From D365 Finance ($210-300/user/month)

| D365 Finance capability | IPAI demo equivalent | Show in module |
|---|---|---|
| Account Reconciliation Agent | Genie: "which accounts are unreconciled?" | Module 4 |
| Invoice capture automation | `ipai_doc_intel` + DocAI prebuilt-invoice (tested) | Module 2 |
| Customer payment prediction | gold_finance_ar_aging + deadline risk scoring | Module 3 |
| Cash flow forecasting | gold_finance_cash_position (planned) | Module 4 |
| Expedited financial close | Close cockpit with phase/milestone/dependency tracking | Module 1 |
| Anomaly exposure in close | Evidence gap analysis + blocker detection | Module 2 |
| Copilot summaries | Pulser: "generate close summary for FD" | Module 5 |
| Tax compliance (multi-jurisdiction) | BIR compliance control tower (PH-first) | Module 3 |
| Configurable tax formula | EWT 2%/10% + VAT 12% auto-classification | Module 2 |
| Audit trail documentation | Odoo chatter + platform.ops.run_events | Module 2 |
| ESG/sustainability tracking | Deferred | — |
| Electronic invoicing | BIR .dat export readiness tracking | Module 3 |
| Subscription billing / MRR | Deferred | — |

### From D365 Project Operations

| D365 Project Ops capability | IPAI demo equivalent | Show in module |
|---|---|---|
| Time Entry Agent | Pulser: task lookup by person + time tracking | Module 5 |
| Expense Agent | DocAI extraction of CA form + Expense Report | Module 2 |
| Activity Approvals Agent | Approval bottleneck dashboard + queue | Module 4 |
| Budget tracking (labor/expense) | gold_ppm_project_health + budget variance | Module 1 |
| Revenue recognition (IFRS) | Deferred (OCA account_asset_management) | — |
| Real-time utilization KPIs | gold_ppm_task_workload + workload heatmap | Module 4 |
| Copilot status reports | Pulser: "generate close-blocker summary" | Module 5 |
| Copilot risk identification | Genie: "which iterations are at risk?" | Module 4 |
| Resource skill matching | dim_finance_person + role-based assignment | Module 1 |
| Fixed-price / T&M contracts | Odoo CE sale.order + project.project | Odoo native |
| Forecasting snapshots | gold_ppm_milestone_status trend | Module 1 |

### From D365 Business Central (SMB competitor)

| D365 BC capability | IPAI demo equivalent | Show in module |
|---|---|---|
| Payables Agent | DocAI + Pulser: "draft evidence request for vendor" | Module 5 |
| Sales Order Agent | Deferred (not finance wedge) | — |
| Bank reconciliation automation | OCA account_reconcile_oca + Genie Q&A | Module 4 |
| Cash flow AI projections | gold_finance_cash_position (planned) | Module 4 |
| Project costing + timesheets | Odoo CE project + hr_timesheet | Odoo native |
| Inventory forecasting | Deferred (not finance wedge) | — |
| Copilot ad-hoc analysis | Genie: any NL question over gold marts | Module 4 |
| Power BI integration | Databricks dashboards + Genie (equivalent) | Module 4 |

### Updated demo KPIs (expanded from 8 to 12)

| # | KPI | Source | D365 equivalent |
|---|---|---|---|
| 1 | Filings due in next 7 days | fact_bir_deadline_control | Tax compliance dashboard |
| 2 | Filings with unresolved blockers | Tax exception cockpit | Anomaly exposure |
| 3 | Close tasks overdue | fact_close_step_status | Close management |
| 4 | Reviewer bottleneck score | fact_finance_workload_snapshot | Activity Approvals Agent |
| 5 | Approval bottleneck score | fact_finance_workload_snapshot | Activity Approvals Agent |
| 6 | Evidence completeness % | Evidence registry | Audit readiness |
| 7 | Recurring task volume | fact_finance_task_schedule | Copilot planning |
| 8 | Automation candidate score | fact_finance_task_schedule | Copilot automation |
| 9 | **Unreconciled accounts** | gold_finance_ar_aging | Account Reconciliation Agent |
| 10 | **Cash advance unliquidated > 30d** | fact_expense_liquidation | Expense Agent |
| 11 | **Invoice extraction accuracy** | ipai_doc_intel confidence | Invoice capture automation |
| 12 | **Budget variance by project** | gold_ppm_project_health | Budget tracking |

### From Odoo 19 release notes (what we achieve on CE 18 + OCA)

| Odoo 19 feature | CE 18 + OCA equivalent | Demo module |
|---|---|---|
| Tax return module (fiscal obligations + deadlines) | `ipai_bir_tax_compliance` + BIR deadline control tower | Module 3 |
| Tax return validation checks | fact_bir_deadline_control + evidence gap analysis | Module 2 |
| Payment withholding support | EWT 2%/10% auto-classification in `ipai_doc_intel` | Module 2 |
| Improved PH localization (2550Q, SLSP, QAP, SAWT) | `ipai_bir_2307` + filing readiness board | Module 3 |
| Official BIR format / .dat export | .dat export readiness tracking (v1.1) | Module 3 |
| Improved payment flow UX | Payment approval queue + payment readiness state | Module 1 |
| AI-powered Discuss features | Pulser chat widget + Llama 4 / Qwen3 inference | Module 5 |
| Improved project UX | OCA `project_timeline` + `project_task_default_stage` | Odoo native |
| Spreadsheet improvements | Databricks gold views + Genie (better for analytics) | Module 4 |
| Improved accounting reports | OCA `account_financial_report` + Databricks dashboards | Module 4 |

### From Notion 3.0 (what we achieve without Notion)

| Notion 3.0 feature | IPAI equivalent | Where |
|---|---|---|
| AI agents (create, search, execute multi-step) | Pulser (guided finance ops) + 6 MAF agents | Odoo + ACA |
| Workspace search across tools | Genie spaces (NL over gold marts) + Odoo global search | Databricks One |
| Projects / tasks / databases | Odoo `project.project` + `project.task` + kanban | Odoo native |
| Connected apps / integrations | MCP topology (12 servers, 3 phases) | MCP |
| Multi-step workflow orchestration | Odoo approval chains + OCA `base_tier_validation` | Odoo + OCA |
| Templates for repeatable work | `spec/_templates/` (4 types, 15 files) | Repo |
| Custom databases (tables) | Odoo models + property fields (CE 18) | Odoo native |
| Real-time collaboration | Odoo bus + chatter + live editing | Odoo native |
| AI writing / summarization | Pulser summaries + Databricks serving (Llama 4) | Module 5 |
| Domain-organized content | Genie spaces per domain (Finance Ops + Compliance) | Databricks One |
| Kanban + calendar + timeline | Odoo kanban + calendar + OCA `project_timeline` | Odoo native |
| API access | Odoo JSON-RPC + MCP + OData entity map | All layers |

### From SAP Joule / AFC / Tax Compliance

| SAP capability | IPAI equivalent | Demo module |
|---|---|---|
| Joule plain-language explanations | Pulser: "why is this blocked?" + summaries | Module 5 |
| Joule document processing | DocAI prebuilt-invoice + custom TBWA models | Module 2 |
| Joule dispute/root-cause help | Pulser: evidence request drafting + exception triage | Module 5 |
| AFC close calendar orchestration | Close cockpit with phases/milestones/dependencies | Module 1 |
| AFC critical path analysis | Deadline risk scoring + compression detection | Module 1 |
| AFC real-time close status | gold_ppm_milestone_status + gold_close_step_status | Module 1 |
| AFC task dependency governance | Milestone sequence_no + approval_stage chain | Module 1 |
| Tax Compliance rule-based checks | Tax exception cockpit (blocker/warning/info) | Module 2 |
| Tax Compliance filing readiness | BIR filing readiness board (2550Q, 1601-EQ, 1702) | Module 3 |
| Tax Compliance issue severity | deadline_risk + evidence_status classification | Module 2 |

### From AvaTax (Avalara) — compliance benchmark

| AvaTax capability | IPAI equivalent | Demo module |
|---|---|---|
| Automated tax determination | EWT 2%/10% + VAT 12% auto-classification | Module 2 |
| Use-tax control | Withholding-on-payment review | Module 1 |
| Filing/payment handling | BIR filing readiness + payment approval queue | Module 3 |
| Compliance automation | fact_bir_deadline_control + control tower | Module 3 |
| Tax calendar management | Tax obligation registry (data-driven, not hardcoded) | Module 3 |
| Jurisdiction-aware rates | PH BIR ATC codes (WI010, WC010, etc.) | Module 2 |

### Doctrine statement

> We do not need Odoo 19, Notion, or D365 agents.
> CE 18 + OCA + Pulser + Databricks achieves the same outcomes at a fraction of the cost.
> Odoo 19 validates our direction; SAP validates our close/compliance patterns;
> Notion 3.0 validates our workspace/agent patterns; AvaTax validates our tax posture.
> D365 Finance + Project Ops = $510/user/month. IPAI = open-source ERP + pay-per-query analytics.
