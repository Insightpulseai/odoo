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
