# Surface Blueprint — UI Pattern Matrix + Product Synthesis

> Canonical reference for product surface design decisions.
> Maps each product surface to its reference source, borrow list, ignore list, and stack placement.

---

## 9 Product Surfaces

### Surface 1: Executive Control Tower

| Attribute | Value |
|-----------|-------|
| **Purpose** | Management overview of all finance, compliance, and delivery health |
| **Reference** | Clarity canvas (Microsoft Project) + ADO overview dashboard |
| **Borrow** | KPI tile row, risk heatmap, overdue list, bottleneck table, workload bar chart |
| **Ignore** | Project plan Gantt view, resource allocation grid, sprint burn-down |
| **Stack placement** | Databricks One / SQL Dashboard (gold views) |

---

### Surface 2: Delivery Telemetry

| Attribute | Value |
|-----------|-------|
| **Purpose** | Real-time task throughput, velocity, and milestone progress across all active projects |
| **Reference** | ADO sprint board + delivery metrics dashboard |
| **Borrow** | Velocity chart, cumulative flow diagram, milestone burn-up, cycle time histogram |
| **Ignore** | Backlog grooming panel, story point poker, release train calendar |
| **Stack placement** | Databricks One / SQL Dashboard (gold_ppm_task_workload + milestone_status) |

---

### Surface 3: Close Cockpit

| Attribute | Value |
|-----------|-------|
| **Purpose** | Period close phase management with milestones, dependencies, and status tracking |
| **Reference** | SAP Advanced Financial Closing (SAP AFC) |
| **Borrow** | Phase timeline strip, milestone checklist, task list by stage, blocker highlights, evidence status column |
| **Ignore** | SAP S/4HANA ledger reconciliation widgets, FI module drill-down, ABAP task detail pane |
| **Stack placement** | Databricks dashboard + Pulser summary (gold_ppm_milestone_status + bronze.ppm_tasks) |

---

### Surface 4: Compliance / Filing Board

| Attribute | Value |
|-----------|-------|
| **Purpose** | BIR filing readiness with deadline chains, readiness percentage, and blocker tracking |
| **Reference** | SAP Tax Compliance + Odoo 19 tax return flow |
| **Borrow** | Filing row table (form number, deadline, readiness %, owner, evidence status), deadline countdown, blocker flag |
| **Ignore** | SAP GTS global trade widgets, Odoo EE tax audit report, country-specific non-PH compliance screens |
| **Stack placement** | Databricks dashboard (gold_ppm_milestone_status + gold_ppm_evidence_gap_analysis) |

---

### Surface 5: Project / Program Dashboard

| Attribute | Value |
|-----------|-------|
| **Purpose** | Per-project health, task distribution, and workload view across active programs |
| **Reference** | Clarity canvas widgets + Microsoft Project home page |
| **Borrow** | Project health card grid, status badge (on track / at risk / blocked), task count by stage, owner assignment list |
| **Ignore** | Clarity timeline editor, resource leveling tool, budget vs actuals module |
| **Stack placement** | Databricks One (gold_ppm_project_health + gold_ppm_task_workload) |

---

### Surface 6: Assistant Panel

| Attribute | Value |
|-----------|-------|
| **Purpose** | Guided finance operations inside Odoo — summaries, evidence requests, blocker explanations |
| **Reference** | SAP Joule (assistant panel behavior and interaction patterns) |
| **Borrow** | Systray chat widget, contextual action cards, structured response format, "Draft for me" trigger, FD summary export |
| **Ignore** | Joule SAP BTP dependency, SAP Launchpad shell integration, ABAP backend call patterns |
| **Stack placement** | Odoo systray / Pulser chat widget (Odoo project.task + gold views via ipai-odoo-mcp) |

---

### Surface 7: Workspace Search

| Attribute | Value |
|-----------|-------|
| **Purpose** | Natural language Q&A over finance workload, compliance status, and control data |
| **Reference** | Notion 3.0 domain search + Databricks Genie |
| **Borrow** | NL query bar, suggested questions, tabular answer format, filter-by-domain chip row |
| **Ignore** | Notion page graph, wiki-style sidebar navigation, block-based editor |
| **Stack placement** | Databricks One Chat / Genie Space (4 gold views) |

---

### Surface 8: Evidence / Issue Board

| Attribute | Value |
|-----------|-------|
| **Purpose** | Track missing evidence, partial documentation, and exception queue |
| **Reference** | Clarity table widget + SAP compliance feel |
| **Borrow** | Evidence gap table (sortable by deadline risk), missing count by person, partial vs missing breakdown, owner column |
| **Ignore** | SAP audit trail deep-link, Clarity issue resolution workflow, JIRA-style issue lifecycle |
| **Stack placement** | Databricks dashboard (gold_ppm_evidence_gap_analysis) |

---

### Surface 9: Action / Execution Workspace

| Attribute | Value |
|-----------|-------|
| **Purpose** | Automation candidate review and Pulser-ready task queue management |
| **Reference** | Notion 3.0 agent workspace + control tower |
| **Borrow** | Ranked candidate list, task category grouping, Pulser-ready flag filter, one-click trigger affordance |
| **Ignore** | Notion database view editor, formula columns, full Notion block editor surface |
| **Stack placement** | Databricks dashboard (gold_ppm_pulser_candidate_tasks) |

---

## 4 Synthesis Rules

| Rule | Application |
|------|-------------|
| **Clarity for dashboards** | All overview, telemetry, and workload surfaces follow Microsoft Clarity canvas layout conventions: KPI tile row at top, charts in center, list/table below. No Gantt, no timeline editor. |
| **SAP AFC for close** | Close Cockpit borrows SAP Advanced Financial Closing phase strip and milestone checklist directly. Evidence status column is a first-class field. Blockers surface as inline highlight rows, not modal popups. |
| **Joule for assistant** | Pulser assistant panel follows SAP Joule interaction grammar: systray entry, contextual card response, structured draft output, FD-ready summary format. No free-form chat wall. |
| **ADO for telemetry proof** | All delivery telemetry surfaces (velocity, cycle time, milestone burn-up) use ADO-style chart types and labeling. Live data from Databricks gold views. No synthetic metrics. |

---

## Design Rule

> Clarity for dashboards. SAP AFC for close cockpit. Joule for assistant behavior. ADO for live telemetry proof.

Every screen inherits exactly one reference for its primary interaction pattern.
Mixing reference patterns within a single screen is not permitted.
Reference borrowing applies to layout and interaction grammar only — visual styling follows IPAI design tokens, not the reference product's brand.

---

*SSOT: `docs/product/surface-blueprint.md`*
*Last updated: 2026-04-15*
