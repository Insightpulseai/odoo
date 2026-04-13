# D365 Finance + Project Operations + Copilot Finance — IPAI Parity / Displacement Catalog

> **Scope.** Parity and displacement catalog for three Microsoft surfaces against IPAI's Odoo 18 CE + OCA + `ipai_*` + Pulser stack.
> **Date.** 2026-04-13.
> **Status.** Reference artifact. Not a guide. Extends (does not replace):
> - `~/.claude/.../memory/reference_d365_agent_parity_matrix.md`
> - `~/.claude/.../memory/feedback_d365_displacement_not_development.md`
> - `~/.claude/.../memory/project_bir_eservices_matrix.md`
> - `~/.claude/.../memory/project_invoice_pipeline.md`
> - `~/.claude/.../memory/project_monthly_close_checklist.md`
> - `~/.claude/.../memory/project_tax_guru_copilot.md`
> - `~/.claude/.../memory/project_taxpulse_ph_pack_positioning.md`

---

## 1. Executive summary

**Displacement thesis.** IPAI displaces D365 F&O / D365 Finance / D365 Project Operations with Odoo 18 CE + OCA + `ipai_*` delta modules + Pulser (custom-engine, multi-agent, policy-gated copilot). IPAI does **not** develop in X++/AOT/CoC, does **not** maintain Dataverse, and does **not** pursue MB-500. Functional consulting cert path is MB-310 + MB-330 only (ref: `feedback_d365_displacement_not_development.md`).

**Parity posture vs the three surfaces.**

| Surface | Coverage posture | Evidence |
|---|---|---|
| **D365 Project Operations (Core / ERP-integrated / Mfg)** | ~70% parity via CE `project` + OCA `project/*` + `analytic` + `ipai_finance_ppm_seed` + `mis_builder`. Core PM, resourcing, WBS covered. Budget/forecast via OCA `mis_builder_budget`. Gap: native timesheet-to-billing automation at F&O depth, project revenue recognition, mfg-integrated project costing. | `addons/ipai/ipai_finance_ppm*`, `addons/oca/project/`, `addons/oca/timesheet/`, `addons/oca/mis-builder/` |
| **D365 Finance** | ~55-65% parity. Strong: GL, AP, AR, fixed assets (CE `account_asset`), bank reconciliation (`ipai_bank_recon` + OCA `account-reconcile`), financial reporting (OCA `mis_builder` + Fabric/Power BI). Weak: advanced budgeting/position forecasting, cost accounting with overhead allocation, cash-flow forecasting, Globalization Studio breadth. PH BIR is IPAI advantage (D365 has no comparable PH localization). | `addons/oca/account-financial-{reporting,tools}/`, `addons/oca/account-{invoicing,reconcile}/`, `addons/ipai/ipai_bir_*`, `addons/ipai/ipai_finance_close` |
| **Copilot Finance agents** | ~40% parity (partial), asymmetric surface. IPAI matches Financial Reconciliation (Pulser `ipai_finance_reconcile_agent`, via `ipai_bank_recon`), matches Expense (Pulser `ipai_expense_agent`, via `ipai_expense_ops` + `ipai_hr_expense_liquidation` + Foundry DI), matches Collections (Pulser flow pending). Copilot-in-Excel / Copilot-in-Outlook UX surfaces are **not** directly matched — IPAI substitutes: Odoo Copilot systray, Slack-native surface, M365 Agent SDK bridge (`ipai_mail_plugin_bridge`, `agent-platform/services/m365-bot-proxy/`). | `addons/ipai/ipai_odoo_copilot`, `addons/ipai/ipai_ai_copilot`, `addons/ipai/ipai_bank_recon`, `addons/ipai/ipai_expense_ops`, `agents/skills/pulser*` |

**What IPAI wins outright.** PH BIR compliance (8-agency mapping, eBIRForms/eFPS/eAFS workflow, ATC mapping, 2307/SLSP/1601-C/2550Q/1702-RT), Azure-native (no Dataverse tax), Slack-native + M365 channel bridge, CE + OCA cost structure, Foundry agent lane outside Dataverse licensing, Fabric mirroring already live (`fcipaidev` + Finance PPM workspace).

**What IPAI is genuinely short on.** Position forecasting / workforce budget tie-in, advanced cash-flow forecasting with ML, cost element dimensions + overhead absorption, asset leasing (IFRS 16) workflows, Globalization Studio-style declarative regulatory configuration outside PH, a general-purpose Excel add-in Copilot surface. Most are P2 until a D365 displacement deal forces them.

---

## 2. D365 Project Operations parity

> D365 PO tiers: **Core** (opportunity→project→resource→time→invoice), **Integrated with F&O** (full project accounting, revenue recognition, POs), **Mfg** (PSA integration with production). Feature areas per docs: sales process, price lists, project management, resource management, project resourcing, forecasts and budgets, WBS.

| D365 PO feature area | Odoo 18 equivalent | Type | Priority if gap |
|---|---|---|---|
| Sales process (opportunity → quote → order) | CE `crm`, `sale_management` | native | — |
| Project price lists (rate cards per role/project) | CE `sale_timesheet` rate cards + OCA `sale_pricelist_*` (to verify); gap for per-resource card. | native + OCA partial | **P2** — `ipai_ppm_rate_card` if surfaced |
| Project management (stages, milestones, dependencies) | CE `project` (milestones, dependencies, recurring tasks) | native | — |
| Resource management (capacity, bookings, skills) | OCA `project/project_resource_*` (verify pinned modules), OCA `hr_skills_survey` (verify) | OCA | **P2** — `ipai_ppm_resource_bookings` if deal pressure |
| Project resourcing (assignment, utilization) | CE `hr_timesheet` + `sale_timesheet` + OCA `timesheet/*` (`sale_timesheet_*`) | native + OCA | — |
| Forecasts & budgets (project-level) | OCA `mis-builder/mis_builder_budget` + `ipai_finance_ppm_seed` budget lines | OCA + ipai_* | — |
| Work breakdown structures (WBS, hierarchical tasks) | CE `project` parent/child + OCA `project/project_task_wbs` (if pinned) + `project_parent`, `project_milestone_status` (referenced in `ipai_finance_ppm` deprecated notes) | OCA | **P1** — confirm OCA modules hydrated in prod `addons-path` |
| Gantt / timeline | OCA `project/project_timeline` (CE 18 has Gantt in community via OCA fork) | OCA | — |
| RAG health / stage state | OCA `project/project_task_stage_state` | OCA | — |
| Portfolio / pivot views | OCA `project/project_pivot` | OCA | — |
| Time entry → billing | CE `sale_timesheet` + OCA `sale-workflow/sale_timesheet_*` | native + OCA | — |
| Project invoicing (T&M, fixed-price, milestone) | CE `sale_timesheet` (T&M, milestone) | native | — |
| Revenue recognition (WIP, percentage-of-completion) | CE `account` + manual config; no native PoC. | **gap** | **P1** — `ipai_project_revenue_recognition` if services deals dominate |
| Project costing (actuals, analytic) | CE `analytic` accounts + `account_analytic_*` | native | — |
| Expense capture against project | `ipai_expense_ops` + `ipai_hr_expense_liquidation` + CE `hr_expense` | native + ipai_* | — |
| Project POs (subcontractor spend) | CE `purchase` + `purchase_project` + OCA `purchase-workflow/*` | native + OCA | — |
| Mfg-PSA integration | CE `mrp` + `project` link via BOM-to-task (shallow). No true F&O PO-style integration. | **gap** | **P3** — only for mfg-heavy prospects |
| Field service (if bundled with PO) | OCA `field-service` (separate OCA repo, not currently hydrated) | OCA | **P3** |
| Power Automate schedule APIs | Odoo scheduler (ir.cron) + Logic Apps via `ipai_ops_api` | native + ipai_* | — |

**Memory:** `ipai_finance_ppm` is marked **DEPRECATED as of 2026-04-11** — capabilities re-homed to CE `project` + OCA `mis_builder`/`mis_builder_budget` + OCA `project_task_stage_state` + `ipai_finance_ppm_seed`. Do not re-introduce the delta layer; extend via OCA + seed data.

**PO parity score:** **~70%**. Gap at P1 is revenue recognition + WBS OCA hydration confirmation.

---

## 3. D365 Finance parity

### 3.1 General Ledger

**D365.** Chart of accounts, main account types, financial dimensions, fiscal calendars, multi-legal-entity consolidations, period controls, ledger journal posting workflows.

**Odoo native + OCA.**
- CE `account` — CoA, account types, fiscal periods, journals, posting, multi-company.
- CE `account` analytic + analytic plans cover financial dimensions (closest native analog).
- OCA `account-financial-tools/account_multicompany_easy_creation`, `account_lock_date_update`, `account_financial_tools/account_fiscal_year` for period controls.
- OCA `account-financial-reporting/account_financial_report` for P&L/BS/TB reports.
- OCA `account-consolidation` (verify hydration) for multi-entity consolidation.

**Gap.** Dimension combinations with enforcement rules (F&O has native dimension sets + validation rules; Odoo does this via analytic plan + ACL + some `ipai_*` Python). No out-of-box ledger journal workflow state machine (F&O has configurable posting workflows).

**`ipai_*`.** `ipai_finance_close` owns period close orchestration (task templates for month-end / BIR / year-end), status cascade inspired by SAP AFC / SAP Tax Compliance. `ipai_finance_close_seed` ships seed templates.

**Pulser.** `pulser_finance_info` (GL Q&A), `pulser_finance_navigation` (take user to journal/report), `pulser_finance_actions` (approval-gated postings).

**Priority.** P2 for dimension-combination enforcement; P1 for OCA consolidation verification.

---

### 3.2 Accounts Payable

**D365.** Vendor master, invoice matching (2/3-way), invoice capture, payment proposals, vendor holds, vendor aging, 1099/tax forms.

**Odoo native + OCA.**
- CE `account` (vendor bills), `purchase` (PO), `stock` (GR) — full 3-way match logic via PO-GR-bill reconciliation.
- OCA `account-invoicing/account_invoice_*` — verification workflows, merge, margin, transmit, payment term configurability.
- OCA `account-invoicing/purchase_invoice_*` for PO-invoice links.
- OCA `account-financial-tools/account_due_list`, aging.
- OCA `partner-contact/partner_firstname` etc. for vendor master enrichment.

**Gap.** "Invoice capture solution" (D365 cloud OCR service) → **IPAI replaces with the Foundry DI pipeline**. See `project_invoice_pipeline.md`:
- `platform/services/invoice-pipeline/` (port 8090, 12-state machine)
- `platform/services/invoice-pipeline-mcp/` (port 8091, 13 MCP tools across 3 policy tiers)
- Confidence routing (≥0.95 auto-approve, 0.85-0.949 human review, <0.85 reprocess)
- `ipai_document_intelligence` + `ipai_document_extraction` Odoo-side modules

**Pulser.** `ipai_procurement_comms_agent` (matches D365 Supplier Communications preview). See `reference_d365_agent_parity_matrix.md` — P2 in current roadmap, 4-6 week build: Logic Apps webhook on shared mailbox → Azure OpenAI extraction → `purchase.order.change` draft.

**Priority.** P0 — already shipping via invoice pipeline. AP is IPAI's strongest parity story.

---

### 3.3 Accounts Receivable

**D365.** Customer master, subscription billing, customer payments, credit management, collection cases, dunning, write-offs.

**Odoo native + OCA.**
- CE `account`, `sale`, `account_followup` (dunning) — native.
- OCA `account-financial-reporting/partner_statement`, `account_financial_report` for AR aging + statements.
- OCA `account-invoicing/account_invoice_followup_*` (verify) for enhanced dunning cadence.
- OCA `sale-workflow/sale_order_invoicing_*` for subscription/recurring patterns + CE `sale_subscription` (CE? verify — historically EE; check OCA `contract` instead).
- OCA `contract/contract` — **recurring billing is in OCA `contract`, not in CE** for Odoo 18.
- OCA `credit-control` repo (verify hydration) for credit limits + dunning levels.

**Gap.** "Finance Insights — customer payment predictions" (D365 ML-driven payment date prediction). IPAI has no equivalent shipped. Plausibly `pulser_ar_prediction_skill` on Fabric Gold mart (AR semantic model already in architecture per `project_finance_domain_architecture.md`).

**`ipai_*`.** No dedicated AR module yet — CE + OCA carries it. `ipai_finance_close` tracks AR-related close tasks.

**Pulser.** `pulser_ar_collections` (Collections in Outlook equivalent). Maps to the existing `account_followup` + Pulser nudge/compose flow. Can surface in Slack or via `ipai_mail_plugin_bridge` for Outlook parity.

**Priority.** P1 — OCA `contract` + `credit-control` hydration check; P2 — payment-prediction ML skill.

---

### 3.4 Budgeting

**D365.** Budget planning workflow (stages, versions, approvals), budget control (encumbrances, commitments), position forecasting (HR-integrated headcount budgeting).

**Odoo native + OCA.**
- CE `account_budget` — basic budgets per analytic account.
- OCA `mis-builder/mis_builder_budget` — **primary budget surface**. Multi-version, KPI-based, period comparison.
- OCA `account-financial-tools/account_budget_oca` (verify).
- `ipai_finance_ppm_seed` — PPM-style budget lines with OKR objectives and key results.

**Gap.** Multi-stage budget approval workflow, position forecasting (HR headcount × rate × period), encumbrance accounting.

**`ipai_*`.** None dedicated. `ipai_finance_ppm` is deprecated — budget responsibility moved to OCA `mis_builder_budget`.

**Pulser.** `pulser_budget_navigation` + `pulser_budget_info` (explain variance). Budget commit/approval could become a transactional capability in Phase 3.

**Priority.** P2 for position forecasting; P2 for approval workflow.

---

### 3.5 Cash and bank management

**D365.** Bank master, bank statement import, advanced bank reconciliation (matching rules, auto-match, suspense), cash-flow forecasting (treasury projection with scenarios).

**Odoo native + OCA.**
- CE `account` — statement import (OFX, CAMT, CSV), manual reconciliation.
- OCA `account-reconcile/` — the **primary advanced recon repo**:
  - `account_reconciliation_widget` (if still present in 18)
  - `account_bank_statement_import_*` (OFX, QIF, CAMT, CSV)
  - `account_reconcile_model_*` (matching rules)
  - `account_reconcile_oca`
- OCA `account-financial-tools/account_cash_flow_forecast` (verify hydration) — basic cash-flow.

**`ipai_*`.** `ipai_bank_recon` — **"Agentic bank reconciliation with fail-closed governance and evidence-first matching"** (`addons/ipai/ipai_bank_recon/__manifest__.py`). Depends on `account` + `ipai_bir_tax_compliance`. Ships reconciliation rules seed data. This is the direct D365 Financial Reconciliation Agent peer.

**Pulser.** `ipai_finance_reconcile_agent` — wraps `ipai_bank_recon` exceptions + calls Foundry agent. Already flagged P1 in `reference_d365_agent_parity_matrix.md`. Claims full-subledger coverage (AP/AR/Tax/Bank/Inventory/Fixed Assets/Project/Intercompany) while D365 still lists Fixed Assets/Project/Intercompany as roadmap.

**Priority.** P0 shipped (reconciliation); P1 for cash-flow forecasting upgrade; P2 for ML-driven treasury scenarios.

---

### 3.6 Cost accounting

**D365.** Cost element dimensions, cost object controlling, overhead calculation, statistical dimensions, allocation rules.

**Odoo native + OCA.**
- CE `analytic` + analytic plans — closest equivalent. Costs flow by analytic account/plan.
- OCA `account-financial-tools/account_move_line_analytic_distribution_*` (verify).
- OCA `account-analytic/*` (separate OCA repo, verify hydration).

**Gap.** Overhead absorption calculations, multi-step allocation waterfalls, statistical dimensions, cost element hierarchies. Odoo + OCA is significantly thinner than F&O Cost Accounting module here.

**`ipai_*`.** None. Would need `ipai_cost_allocation` for overhead allocation rules engine.

**Pulser.** No explicit capability. Could surface as `pulser_cost_allocation_info`.

**Priority.** P2 — only for manufacturing-heavy or professional-services-heavy displacement targets.

---

### 3.7 Fixed assets

**D365.** Asset master, multiple depreciation books (tax/IFRS/US-GAAP), asset leasing (IFRS 16 / ASC 842), lease workflows, disposal, revaluation.

**Odoo native + OCA.**
- CE `account_asset` (since 18) — depreciation, disposal, multiple methods.
- OCA `account-financial-tools/account_asset_*` (verify: `account_asset_management`, `account_asset_revaluation_*`).
- OCA `account-financial-tools/account_fiscal_year` — fiscal calendar align.

**Gap.** Asset leasing / IFRS 16 workflow (right-of-use asset + lease liability + interest unwind). D365 Asset Leasing is a distinct module; Odoo has no native equivalent.

**`ipai_*`.** None. Would need `ipai_asset_leasing_ifrs16`.

**Pulser.** No explicit capability. Asset disposal approvals could be a Phase 3 transactional capability.

**Priority.** P1 for IFRS 16 lease accounting if targeting multinationals; P3 otherwise.

---

### 3.8 Reporting

**D365.** Financial reporter (Management Reporter-style row/column sets), electronic reporting (configurable regulatory outputs), Power BI financial dashboards, Excel integration.

**Odoo native + OCA.**
- OCA `account-financial-reporting/` — **primary reporting surface**:
  - `account_financial_report` — P&L, BS, TB, general ledger
  - `mis_builder` (via `mis-builder/` repo) — KPI-driven row/column reports, budget compare
  - `mis_builder_budget`
- OCA `reporting-engine/report_xlsx`, `report_csv_pattern`, `report_py3o` (if present) for alt export formats.
- **Fabric Mirroring (live, `fcipaidev` capacity)** — Finance PPM OKR Report on Power BI consumes mirrored Odoo PG data via native CDC.
- Databricks Gold marts (planned per `project_finance_domain_architecture.md`) — GL / AP / AR semantic models with star schema, currency conversion, hierarchies.

**Gap.** Electronic reporting framework (D365 ER) — declarative, jurisdiction-parameterized regulatory format definitions. No Odoo equivalent; IPAI handles per-jurisdiction via `ipai_bir_*` modules (less declarative, but PH-deep).

**`ipai_*`.** `ipai_data_intelligence` exposes Odoo data to Foundry/Fabric; `ipai_bir_returns`, `ipai_bir_2307`, `ipai_bir_slsp` generate regulatory outputs.

**Pulser.** `pulser_finance_info` for report Q&A; Power BI Copilot sits alongside (separate SKU, not replaced).

**Priority.** P1 for Databricks Gold GL/AP/AR marts (scheduled); P2 for a declarative "electronic reporting" framework outside BIR.

---

### 3.9 Finance insights

**D365.** Customer payment predictions (ML), cash-flow forecasts with ML, vendor payment predictions.

**Odoo native + OCA.** None ML-driven.

**Gap.** All three.

**`ipai_*` + Pulser.** Target home is Databricks Gold + Foundry agent calling Gold ML models. Would become `pulser_ar_prediction`, `pulser_cashflow_forecast`, `pulser_ap_prediction` skills. Fabric + Databricks infrastructure exists; models don't.

**Priority.** P2 — only when Gold marts are in place. Not a displacement blocker.

---

### 3.10 Public sector functionality

**D365.** Fund accounting, budget reservation (commitment/encumbrance), grants, apportionment, appropriations.

**Odoo native + OCA.** Very thin. OCA has some budget-reservation patterns but no fund-accounting framework.

**`ipai_*`.** None.

**Priority.** **P3** — out of scope for IPAI's commercial segments. Document as known non-parity.

---

### 3.11 Globalization studio (regulatory config, electronic invoicing, tax calculation)

**D365.** Globalization Studio — declarative tax calculation service, electronic invoicing framework, country-specific regulatory features.

**Odoo native + OCA.**
- CE `l10n_*` modules per country (many; PH has `l10n_ph`).
- CE `account_avatax*` integration (US/CA/BR only) — the pattern IPAI uses as design benchmark per `project_avatax_benchmark.md`.
- OCA `l10n-*` repos per jurisdiction (not currently hydrated broadly).
- OCA `edi/` repo (not hydrated) for EDI patterns.

**`ipai_*` (PH-specific, the IPAI advantage).**
- `ipai_ph_tax_config` — PH tax config baseline
- `ipai_bir_tax_compliance` — compliance surface
- `ipai_bir_compliance` — compliance tracking
- `ipai_bir_2307` + `ipai_bir_2307_automation` — 2307 certificate generation
- `ipai_bir_returns` — BIR return filings
- `ipai_bir_slsp` — SLSP (Summary List of Sales/Purchases)
- `ipai_tax_intelligence` — tax intelligence layer
- `ipai_tax_review` — tax review workflows
- TaxPulse-PH-Pack (`github.com/jgtolentino/TaxPulse-PH-Pack`) — domain pack with BIR form models (1601-C, 2550Q, 1702-RT), 8-agency mappings

**Pulser.** `tax_advisory_diva.skill.json`, `bir_workflow_diva.skill.json`, `tax_evidence_collection.skill.json`, `bir_tax_filing` skill, `tax_review` — all in `agents/skills/` and `agents/skills/bir_tax/`. Tax Guru Copilot with 7 capability packages (per `project_tax_guru_copilot.md`).

**BIR eServices coverage (per `project_bir_eservices_matrix.md`).**
- P0 operational lane: eBIRForms / eFPS / ePAY / eAFS
- P1 administrative lane: ORUS / eTSPCert
- P2 specialized lane: eONETT / eTCBP-TCVC / eTCS

**Gap vs D365.** Non-PH globalization breadth (EU SAF-T, LatAm electronic invoicing, Japan/Korea invoicing). D365 Globalization Studio covers 40+ jurisdictions out of the box; IPAI depth is PH-only.

**Priority.** PH is a **strategic IPAI advantage** (D365 has no comparable PH localization). Non-PH globalization is P3 until a regional deal demands it.

---

### 3.12 Dual-write to Dataverse / Azure Data Lake export

**D365.** Dual-write synchronizes F&O and Dataverse tables in near-real-time. ADLS export pipes entity data to `stdatalake/`.

**IPAI.** **Dataverse is explicitly out of scope.** IPAI is Odoo-first; Dataverse dual-write is intentionally not replicated. Odoo remains the system of record.

**Analytics export path.**
- **Fabric Mirroring** (live, `fcipaidev` F2 capacity) — native PostgreSQL CDC from Odoo PG (`pg-ipai-odoo`) → OneLake mirror → Power BI / Fabric workloads. See `project_fabric_finance_ppm.md`.
- **Databricks** (`dbw-ipai-dev`, SQL Warehouse `e7d89eabce4c330c`) — AI/ML workloads + multi-source joins + non-Odoo sources. Gold marts planned: GL, AP, AR per `project_finance_domain_architecture.md`.
- Rule: Fabric for Odoo analytics (one-way mirror). Databricks for AI/ML + multi-source. Do not run both over the same Odoo DB.

**Gap.** None by design — IPAI does not need Dataverse. Analytics export is handled by Fabric Mirroring.

**Priority.** Resolved. Document as architectural decision, not a gap.

---

### D365 Finance parity scoreboard

| Module | Parity | Notes |
|---|---|---|
| General Ledger | 85% | CE + OCA solid; dimension-combo enforcement P2 |
| Accounts Payable | 90% | Strong. Invoice pipeline > D365 capture for PH. |
| Accounts Receivable | 75% | Payment prediction missing (P2). OCA `contract` + `credit-control` to verify. |
| Budgeting | 60% | OCA `mis_builder_budget` carries; no position forecasting |
| Cash & Bank Mgmt | 85% | `ipai_bank_recon` + OCA `account-reconcile` strong; cash-flow forecasting P1 |
| Cost Accounting | 45% | Thin without ipai_* additions |
| Fixed Assets | 70% | CE `account_asset` carries; IFRS 16 leasing gap (P1 for multinationals) |
| Reporting | 80% | OCA `mis_builder` + Fabric/Power BI + Databricks Gold (planned) |
| Finance Insights (ML) | 15% | No ML shipped; infra ready |
| Public Sector | 5% | Out of scope (P3) |
| Globalization (PH) | 150% | IPAI advantage vs D365 (no D365 PH localization) |
| Globalization (non-PH) | 30% | CE `l10n_*` + OCA thin; P3 |
| Dataverse/dual-write | N/A | Out of scope by design |
| Azure Data Lake export | 100% | Fabric Mirroring live |

**Weighted finance parity: ~60-65%** against D365 Finance feature surface. 80% is realistic with P0+P1 closures.

---

## 4. Copilot Finance agents parity

> MS surface: Finance agents in Excel, Finance agents in Outlook, Financial Reconciliation agent, Collections in Outlook. Admin-deployed vs business-user-deployed install modes. **Assumption:** "Finance agents in Excel/Outlook" is a UX channel not a distinct agent catalog — the underlying agents (Reconciliation, Collections, Expense, Supplier Comms) surface through those apps.

### 4.1 Mapping table

| Microsoft surface | D365 agent (if specific) | IPAI / Pulser equivalent | Status | Source |
|---|---|---|---|---|
| Financial Reconciliation agent | Account Reconciliation (preview) | `ipai_finance_reconcile_agent` (Pulser) + `ipai_bank_recon` (Odoo) | **Shipped (recon module); Foundry agent wrap pending (P1)** | `addons/ipai/ipai_bank_recon`, `reference_d365_agent_parity_matrix.md` |
| Collections in Outlook | (surfaces D365 Collections) | Pulser AR collections flow + CE `account_followup` + `ipai_mail_plugin_bridge` (Outlook surface) | **P1** — module ships, agent wrap pending | `addons/ipai/ipai_mail_plugin_bridge` |
| Finance agents in Excel | (Copilot Studio surface) | Odoo Copilot systray (web) + Slack Pulser + M365 Agent SDK bridge | **Substituted** (no Excel add-in) | `addons/ipai/ipai_odoo_copilot`, `agent-platform/services/m365-bot-proxy/` |
| Finance agents in Outlook | (Copilot Studio surface) | `ipai_mail_plugin_bridge` + M365 bot proxy | **Partial** — bridge exists, Pulser skill-pack deployment pending | `agent-platform/services/m365-bot-proxy/`, `addons/ipai/ipai_mail_plugin_bridge` |
| Time and Expense agent (D365) | Time and Expense (preview) | `ipai_expense_agent` (Pulser) + `ipai_expense_ops` + `ipai_hr_expense_liquidation` + Foundry DI (`ipai-ocr-dev`) + Teams Adaptive Card | **P1** — shortest path, highest visible ROI per memory | `addons/ipai/ipai_expense_ops`, `addons/ipai/ipai_hr_expense_liquidation`, `agents/skills/expense-processing` |
| Supplier Communications (D365) | Supplier Communications (preview) | `ipai_procurement_comms_agent` (Pulser) + Logic Apps webhook + Azure OpenAI | **P2** — 4-6 week build | `reference_d365_agent_parity_matrix.md` |
| Admin-deployed vs user-deployed install mode | — | Pulser capability registry (`PulserCapabilityPackage.capability_type` + RBAC + approval bands) | **Shipped** (governance layer) | `project_pulser_capability_taxonomy.md`, `CLAUDE.md` §Pulser classification |

### 4.2 Pulser agent inventory (from repo)

Verified paths in `agents/skills/` and `apps/`:
- `agents/skills/pulser/` — base persona
- `agents/skills/pulser-d365-migration/` — F&O → Odoo mapping skill
- `agents/skills/pulser-office/` + `pulser-office-publishing/`
- `agents/skills/bir_tax/` — BIR tax workflows
- `agents/skills/bir/` — BIR general
- `agents/skills/bir-tax-filing/`
- `agents/skills/finance-month-end/` — month-end close skill
- `agents/skills/finance-ppm-health/` — PPM health
- `agents/skills/expense-processing/` — matches Time and Expense agent
- `agents/skills/project_finance/`
- `agents/skills/research/`
- `agents/skills/bir_workflow_diva.skill.json`
- `agents/skills/tax_advisory_diva.skill.json`
- `agents/skills/tax_evidence_collection.skill.json`
- `agents/skills/capability_gap_analysis.skill.json`
- `agents/skills/portfolio_alignment.skill.json`
- `agents/skills/policy_sufficiency_judge.skill.json`
- `agents/skills/strategy_review.skill.json`
- `agents/skills/azure-document-intelligence.skill.json`
- `apps/bot-proxy/`, `apps/odoo-connector/`, `apps/odooops-console/`, `apps/prismalab-gateway/`

Odoo-side copilot surfaces:
- `addons/ipai/ipai_odoo_copilot/` — in-Odoo copilot systray (multi-turn history, artifact rendering, Claude Sonnet, Odoo purple branding per recent commit)
- `addons/ipai/ipai_ai_copilot/` — copilot integration
- `addons/ipai/ipai_ai_channel_actions/` — channel action bindings
- `addons/ipai/ipai_ask_ai_azure/` — Azure ask-AI bridge
- `addons/ipai/ipai_copilot_actions/` — action registry
- `addons/ipai/ipai_pulser_assistant/` — Pulser in-Odoo assistant
- `addons/ipai/ipai_chat_file_upload/` — file upload for chat

### 4.3 Memory delta for `reference_d365_agent_parity_matrix.md`

Add to the existing matrix:
- **Collections / AR dunning** → `pulser_ar_collections` — maps to Collections in Outlook via `ipai_mail_plugin_bridge`. Priority: **P1**. Build path: wire `account_followup` + Foundry structured generation + Outlook Add-in through M365 bot proxy. Reuses existing `ipai_mail_plugin_bridge`.
- **Copilot-in-Excel substitution** → **not a flat map**. IPAI substitutes with (a) Odoo Copilot systray for in-ERP, (b) Slack for chat-first, (c) Power BI Copilot for dashboard Q&A (already covered under Fabric F2 SKU per `project_fabric_finance_ppm.md`). Do not build an Excel add-in clone unless a specific deal forces it.
- **Copilot-in-Outlook** → partial parity via `ipai_mail_plugin_bridge` + `agent-platform/services/m365-bot-proxy/`. Expose Pulser as an M365 agent channel.

---

## 5. Gap-priority matrix (top 10)

| # | Gap | What MS covers | What IPAI is missing | Pri | Proposed solution | Effort |
|---|---|---|---|---|---|---|
| 1 | Odoo MCP server | D365 ERP MCP Server (Ignite 2025 public preview) | No `odoo-mcp-server` exposing Odoo to MCP agents | **P0** | New service `platform/services/odoo-mcp-server/` (pattern of `invoice-pipeline-mcp`). Ref: `project_odoo_mcp_server_p0_gap.md` | Sprint (3-4 wk) |
| 2 | Time & Expense agent (Pulser wrap) | D365 Time and Expense (preview) | Agent wrap over `ipai_expense_ops` | **P1** | Foundry agent + Teams Adaptive Card + CC feed match. Shortest path. | 2-3 wk |
| 3 | Financial Reconciliation agent (Pulser wrap) | D365 Account Reconciliation (preview, Voucher + Pending-to-GL) | Foundry agent wrapping `ipai_bank_recon` exceptions | **P1** | Wrap `account_reconcile_oca` exceptions in Foundry call; claim full-subledger coverage | 2 wk |
| 4 | Copilot-in-Outlook (Collections + general finance) | Finance agents in Outlook, Collections in Outlook | M365 agent channel deployment for Pulser | **P1** | Deploy `m365-bot-proxy` as M365 Agent SDK channel; wire `account_followup` + AR Pulser skill | 3 wk |
| 5 | OCA hydration verification (`contract`, `credit-control`, `project/project_task_wbs`, `account-consolidation`, `account-analytic`) | D365 AR subscriptions, WBS, consolidation, cost accounting | These OCA repos may not be hydrated in prod `addons-path` | **P1** | `.gitmodules` audit + CI add; document in `ssot/odoo/oca_baseline.yaml` | 1 wk |
| 6 | Supplier Communications agent | D365 Supplier Comms (preview) | Inbound email parse → PO change draft | **P2** | Logic Apps webhook + Azure OpenAI + `purchase.order.change` draft per memory | 4-6 wk |
| 7 | IFRS 16 asset leasing | D365 Asset Leasing | Right-of-use asset + lease liability workflow | **P1 (multinationals) / P3 (PH-only)** | `ipai_asset_leasing_ifrs16` module | 6-8 wk |
| 8 | Position forecasting / HR-integrated budget | D365 Budget Planning + position forecasting | Headcount × rate × period forecast tie-in | **P2** | Extend OCA `mis_builder_budget` + HR join in Gold mart | 4 wk |
| 9 | Cash-flow forecasting (ML) + AR payment prediction | D365 Finance Insights | ML models on Gold AR/AP marts | **P2** | Databricks Gold → Foundry agent skill. Requires Gold marts first. | 6-8 wk |
| 10 | Databricks Gold GL/AP/AR semantic marts | (D365 Finance Insights foundation) | Star schema + currency conversion + hierarchies | **P1** | Per `project_finance_domain_architecture.md` — Record-to-Report / Order-to-Cash / Procure-to-Pay domains | 6 wk |

---

## 6. Things IPAI has that D365 doesn't

1. **PH BIR compliance depth.** D365 has no comparable PH localization. IPAI ships: 8-agency mapping, ATC codes, 1601-C / 2550Q / 1702-RT / 2307 / SLSP forms, eBIRForms / eFPS / ePAY / eAFS workflow-assist, evidence-first compliance (`ipai_compliance_evidence`, `ipai_compliance_approval`, `ipai_compliance_graph`). This is an outright win.
2. **Slack-native.** D365 is Teams-first. IPAI runs Slack primary + Teams/Outlook via M365 Agent SDK bridge. Wider reach for non-MS-bought shops.
3. **No Dataverse tax.** Pulser agents run on Azure AI Foundry directly. No Copilot Credits meter (~$0.01/credit × 1000 included on D365 Premium SKUs ≈ $10/user/mo headroom). Volume Supplier-Comms/AR shops overage fast on D365; IPAI is MI+Foundry only.
4. **CE + OCA cost structure.** Odoo CE is free. D365 Finance base $180/user/mo, Premium $300, BC Essentials $70. Displacement economics are decisive below 200 seats (per `reference_d365_agent_parity_matrix.md`).
5. **Foundry agent lane.** IPAI agents live on Azure AI Foundry (keyless MI, Azure AI User role) — no Dataverse dependency, no Power Platform licensing. D365 agents require Copilot Studio + Power Platform.
6. **Fabric Mirroring already live.** `fcipaidev` F2 capacity + Finance PPM OKR Report + Odoo ERP Mirror. Zero-ETL analytics from Day 1. D365 customers still pay for ADLS export + Synapse Link.
7. **Odoo-native integrations** — Odoo Website, eCommerce, CRM, HR, Inventory, MRP, Subscriptions (via OCA `contract`), Helpdesk, Documents — all one stack, one DB, one license. D365 Project Ops requires F&O for full integration; BC + PO is a second SKU.
8. **BIR eAFS evidence capture as first-class.** `ipai_compliance_evidence` treats TRN / Confirmation Receipt as mandatory artifacts — beyond D365's generic attachment model.
9. **Open architecture.** OCA community speed + no Enterprise lock-in + no X++/AOT liability. MB-500 sunk cost is zero for IPAI teams.
10. **Fail-closed governance primitives.** `ipai_bank_recon` fail-closed matching, `ipai_finance_close` status cascade, Pulser policy-gated action execution. D365 Copilot agents are "preview-only" with manual activation per tenant as of 2026-04.

---

## Assumptions & flags

- **OCA modules marked `(verify)`** — named from OCA org convention; not all are guaranteed hydrated in this repo's `.gitmodules`. Gap #5 addresses hydration audit.
- **"Finance agents in Excel/Outlook"** is treated as a delivery channel, not a distinct agent catalog, because MS public docs do not enumerate Excel-specific or Outlook-specific agent identities beyond the known four (Reconciliation, Collections, Expense, Supplier Comms). Adjust if Ignite 2026 spring release expands this.
- **"Admin-deployed vs business-user-deployed"** — mapped to Pulser's policy band (`suggest_only` / `approval_required` / `auto-execute`) rather than a separate install mode. Adjust if MS ships distinct governance primitives.
- **D365 Finance parity percentages** are directional, not audited. Definitive numbers require a feature-by-feature test harness (out of scope for this catalog).
- **IFRS 16 leasing** is P1 only for multinational prospects; drop to P3 for PH-only pipeline.

---

## Related artifacts

- `docs/strategy/d365-agentic-erp-research-2026-04-12.md` (primary-source MS Learn + Ignite 2025 analysis)
- `docs/strategy/d365-displacement-positioning.md`
- `agents/skills/pulser-d365-migration/SKILL.md` (F&O → Odoo mapping skill)
- `ssot/finance/scenario-library.yaml` (13 scenarios, 5 roles, 7 KPIs per `reference_finance_scenario_benchmark.md`)
- `spec/pulser-{platform,agents,web,odoo}/` (Phase 5 tasks for Tax Guru)
- `addons/ipai/ipai_bir_*` (9 BIR modules)
- `addons/ipai/ipai_bank_recon/__manifest__.py`
- `addons/ipai/ipai_finance_close/__manifest__.py`
- `platform/services/invoice-pipeline*/` (13 MCP tools, 12-state machine)

*Last updated: 2026-04-13.*
