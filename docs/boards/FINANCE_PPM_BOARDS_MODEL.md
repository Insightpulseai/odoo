# Finance PPM — Azure Boards Operating Model

> Maps the Finance PPM domain into Azure Boards Basic-process work items
> for project `ipai-platform`. Reconciles spec bundles, SSOT files,
> Odoo modules, handbook entries, and OKR targets into a single planning hierarchy.

---

## 1. Planning-vs-Transaction Boundary Table

| Concern | System of Record | Justification |
|---------|-----------------|---------------|
| **Portfolio planning** (epics, milestones, capacity) | Azure Boards | Planning truth — not transactional |
| **Sprint/cycle task tracking** (who does what by when) | Azure Boards | Work assignment and progress |
| **Module development tasks** (code changes, tests) | Azure Boards | Engineering work items |
| **Journal entries, posted moves** | Odoo (`account.move`) | Transactional SoR — never duplicated in Boards |
| **Tax filing records** | Odoo (`ipai.bir.form.schedule`) | Compliance SoR — Boards tracks readiness, not filings |
| **Expense liquidations** | Odoo (`hr.expense.liquidation`) | Transactional SoR |
| **Payroll computations** | Odoo (`hr.payslip`) | Transactional SoR |
| **Seed data definitions** | Repo (`ipai_finance_close_seed/data/`) | Code SSOT — Boards tracks seed validation tasks |
| **Module contracts & architecture** | Repo (`spec/finance-unified/`, `ssot/finance/`) | Spec/SSOT — Boards references, never duplicates |
| **BIR calendar & deadlines** | Repo (`docs/handbook/compliance/bir/calendar.md`) | Reference doc — Boards tracks compliance readiness cycles |
| **Month-end checklist template** | Repo (`docs/handbook/finance/month-end/checklist.md`) | SOP — Boards tracks cycle instances |
| **OKR targets** | Repo (`ssot/governance/enterprise_okrs.yaml`) | Strategy SSOT — Boards links to KR metrics |
| **Filing evidence & audit trail** | `docs/evidence/` + Odoo chatter | Runtime proof — not planning |
| **Spending policies** | Repo (`docs/handbook/finance/policies/`) | Policy doc — Boards tracks policy implementation tasks |

### Boundary Rules

1. Azure Boards holds **planning state** (what will be done, who owns it, when it is due)
2. Odoo holds **transaction state** (posted accounting records, filed returns, approved expenses)
3. Repo holds **definition state** (specs, SSOT YAML, seed data, architecture docs)
4. `docs/evidence/` holds **proof state** (logs, screenshots, test output)
5. No posted journal entry, tax filing, or expense record is ever duplicated as a Boards work item
6. Boards work items link to Odoo records via description URLs (e.g., `erp.insightpulseai.com/web#id=...`)

---

## 2. Proposed Finance PPM Hierarchy

### Epic 1: Finance Unified System — Module Maturity

> Bring the 5 active + 2 planned finance modules to production readiness with tests, version alignment, and documentation.

| Issue | Tasks |
|-------|-------|
| **1.1 Module Version Alignment** | Bump `ipai_bir_tax_compliance` 18.0 → 19.0; Add DEPRECATED banner to `ipai_finance_workflow` manifest; Add derivation note to `ipai_finance_closing_seed.json` |
| **1.2 Seed Integrity Validation** | Create `test_seed_integrity.py` (stages, tags, team, projects, milestones, tasks); Create `test_bir_schedules.py` (monthly/quarterly/annual coverage); Create `test_ppm_smoke.py` (install, extensions, wizard, dashboard) |
| **1.3 Contract Tests & CI** | Create `test_finance_system.py` (deprecated modules gated, version aligned, docs exist); Add finance contract tests to CI workflow |
| **1.4 Satellite Module Activation** | Validate `ipai_bir_notifications` mail templates + cron; Validate `ipai_bir_plane_sync` API connectivity; Set `installable: True` after validation; Add satellite module tests |
| **1.5 Documentation Consolidation** | Verify module doc stubs vs unified doc; Cross-reference technical guide to unified doc; Resolve seed canonical map conflicts |

### Epic 2: BIR Tax Compliance Operations

> Achieve 100% on-time BIR filing rate (KPI kpi_005) through structured compliance cycles.

| Issue | Tasks |
|-------|-------|
| **2.1 Monthly BIR Filing Cycle (Template)** | Export data from Odoo (days 1-5); Reconcile and prepare forms (days 6-7); Manager review (day 8); File via eFPS (days 9-10); Post filing evidence |
| **2.2 Quarterly BIR Filing Cycle (Template)** | Export quarterly data (week 1); Prepare returns + supporting schedules (week 2); Manager + Director review (week 3); File via eFPS (week 4) |
| **2.3 Annual BIR Filing Cycle** | 1604-CF Alphalist (Jan 31); 2316 Certificates to employees (Jan 31); 1604-E EWT Alphalist (Mar 1); 1702 Annual ITR series (Apr 15) |
| **2.4 Tax Pulse Agent Integration** | Implement `bir_compliance_search` tool; Implement `check_overdue_filings` tool; Implement approval-gated compute tools; Implement filing artifact generation (eFPS XML, PDF, Alphalist) |
| **2.5 Compliance Check Automation** | Implement 12 AFC compliance checks (CI-001 through CI-012); Configure compliance scenario scheduling; Build hit investigation workflow |

### Epic 3: Month-End Close Operations

> Achieve monthly close cycle < 10 business days (KPI kpi_003).

| Issue | Tasks |
|-------|-------|
| **3.1 Monthly Close Cycle (Template)** | Phase I Pre-Close (days 1-3): cut-off, sub-ledger freeze, trial balance; Phase II Transaction Close (days 3-8): revenue, accruals, payroll, intercompany; Phase III Reconciliation (days 8-12): bank, AP/AR, fixed assets, inventory; Phase IV Reporting (days 12-15): financials, management reports, variance; Phase V Post-Close (days 15-20): audit adj, period lock, archive |
| **3.2 Close Automation** | Bank statement import automation (n8n daily 6 AM); Depreciation runner automation (n8n monthly day 4); Deadline reminder automation (n8n days 1, 4, 6); Slack channel integration (replace Mattermost refs) |
| **3.3 Close Analytics** | 11 Superset SQL views for finance BI; Close cycle time tracking dashboard; Phase completion rate metrics |

### Epic 4: Finance PPM / Clarity Parity

> Achieve budget management parity score >= 80% (currently 40%).

| Issue | Tasks |
|-------|-------|
| **4.1 OKR Dashboard Enhancement** | Validate OKR dashboard JavaScript action; Connect dashboard to enterprise OKR targets (obj_D, obj_E); Add close cycle time KPI widget; Add BIR filing rate KPI widget |
| **4.2 Budget vs. Actual Analysis** | Extend analytic account budget/forecast fields; Build variance analysis views; Connect to Superset BI layer |
| **4.3 PPM Import Wizard** | Validate bulk data loading wizard; Add WBS hierarchy import (5 levels: goal → outcome → objective → workstream → task); Add resource plan import |
| **4.4 EE Parity: Accounting Modules** | Adopt `account_reconcile_oca` (bank reconciliation — P0); Adopt `account_financial_report` (financial reports — P0); Adopt `account_asset_management` (asset management — P1); Plan `ipai_finance_consolidation` (consolidation — P2) |

### Epic 5: Expense & Cash Advance Management

> Achieve expense processing P50 < 48h (KPI kpi_002).

| Issue | Tasks |
|-------|-------|
| **5.1 Expense Liquidation Module Hardening** | Validate 8-state approval workflow end-to-end; Test accounting entry idempotency; Validate policy engine rules; Test Copilot tool integration (4 tools) |
| **5.2 SAP Concur Integration (Future)** | Employee mapping (Concur → Odoo); Vendor mapping; Cost center → analytic account mapping; Draft-first posting with dedup keys |
| **5.3 Spending Policy Enforcement** | Implement approval threshold rules (₱5K/₱25K/₱100K tiers); Receipt requirement validation; Overdue advance monitoring (daily cron) |

### Epic 6: Payroll & HR Compliance

> Support BIR withholding tax forms driven by payroll data.

| Issue | Tasks |
|-------|-------|
| **6.1 PH Payroll Module** | Implement TRAIN law income tax brackets; Implement SSS/PhilHealth/Pag-IBIG contribution tables; Generate 1601-C data from payroll; Generate 2316 certificates |
| **6.2 Payroll-to-BIR Integration** | Connect payroll output to BIR filing cycle; Validate withholding tax computation accuracy; Generate Alphalist from payroll records |

### Epic 7: Finance Data Platform

> Medallion pipeline coverage for all finance data.

| Issue | Tasks |
|-------|-------|
| **7.1 ETL/Reverse-ETL Pipeline** | Odoo finance data → Bronze layer (raw extract); Bronze → Silver (cleaned, deduplicated); Silver → Gold (business aggregates); Gold → Platinum (KPI-ready) |
| **7.2 Superset BI Views** | 11 SQL views from technical guide; Close cycle analytics; BIR compliance dashboard; Budget variance dashboard |

---

## 3. Recurring Cycle Model

### 3.1 Month-End Close (Monthly)

| Recurrence | Azure Boards Mechanism | Trigger |
|------------|----------------------|---------|
| Monthly | Create child Issues under Epic 3 per period (e.g., "2026-04 Month-End Close") | 1st business day of month |
| Each Issue gets 5 phase Tasks | Copy from template Issue 3.1 | Auto or manual clone |
| Evidence | Link to `docs/evidence/YYYYMMDD-HHMM/month-end/` | Post-close |

**Template fields for recurring Issue:**
- Title: `YYYY-MM Month-End Close`
- Tags: `month-end-close`, `finance-ppm`, `recurring`
- Description: Links to checklist, team assignments, Odoo period

### 3.2 BIR Monthly Filings (Monthly)

| Recurrence | Azure Boards Mechanism | Trigger |
|------------|----------------------|---------|
| Monthly | Create child Issue under Epic 2 per filing period | ~1st of month (for prior month) |
| Tasks per form: 1601-C, 0619-E/1601-E, SSS, PhilHealth, Pag-IBIG | 5 Tasks per monthly Issue | Per form |
| Deadline tracking | Due date = regulatory deadline (10th, 15th, 20th) | Per form |

**Template fields for recurring Issue:**
- Title: `YYYY-MM BIR Monthly Filing (for YYYY-MM-1)`
- Tags: `bir-compliance`, `finance-ppm`, `recurring`
- Description: Links to BIR calendar, form guides, Odoo filing records

### 3.3 BIR Quarterly Filings (Quarterly)

| Recurrence | Azure Boards Mechanism | Trigger |
|------------|----------------------|---------|
| Quarterly | Create child Issue under Epic 2 per quarter | ~1st month after quarter end |
| Tasks: 2550Q, 1601-EQ | 2 Tasks per quarterly Issue | Per form |
| Deadline: 25th after quarter end | Due dates set per BIR calendar | Per form |

**Template fields:**
- Title: `YYYY-QN BIR Quarterly Filing`
- Tags: `bir-compliance`, `finance-ppm`, `recurring`, `quarterly`

### 3.4 BIR Annual Filings (Annual)

| Recurrence | Azure Boards Mechanism | Trigger |
|------------|----------------------|---------|
| Annual | Create Issues under Epic 2 in January | Start of fiscal year |
| Tasks: 1604-CF (Jan 31), 2316 (Jan 31), 1604-E (Mar 1), 1702 series (Apr 15), Alphalist | 5+ Tasks | Per form |

**Template fields:**
- Title: `YYYY BIR Annual Filing`
- Tags: `bir-compliance`, `finance-ppm`, `recurring`, `annual`

### 3.5 Budgeting Cycle (Annual with Quarterly Reviews)

| Recurrence | Azure Boards Mechanism | Trigger |
|------------|----------------------|---------|
| Annual budget preparation | Issue under Epic 4 | Q4 of prior year |
| Quarterly budget review | Issue under Epic 4 per quarter | 1st month of quarter |
| Variance analysis | Task per review | Post month-end close |

### 3.6 Forecasting Cycle (Quarterly)

| Recurrence | Azure Boards Mechanism | Trigger |
|------------|----------------------|---------|
| Quarterly forecast update | Issue under Epic 4 per quarter | Post quarterly close |
| Tasks: data collection, model update, review, publish | 4 Tasks per cycle | Sequential |

---

## 4. Traceability Map

| Board Work Item | Repo Artifact | Odoo Runtime |
|-----------------|---------------|--------------|
| Epic 1 (Module Maturity) | `spec/finance-unified/tasks.md` | Module install state (`ir.module.module`) |
| Epic 2 (BIR Compliance) | `docs/handbook/compliance/bir/calendar.md`, `spec/tax-pulse-sub-agent/` | `ipai.bir.form.schedule`, `project.task` (BIR project) |
| Epic 3 (Month-End Close) | `docs/handbook/finance/month-end/checklist.md`, `ipai_finance_close_seed/data/` | `project.task` (Close project), `account.move` (entries) |
| Epic 4 (PPM/Clarity) | `ssot/governance/enterprise_okrs.yaml` (obj_D, obj_E), `ssot/finance/unified-system.yaml` | `project.project` (PPM), `account.analytic.account` |
| Epic 5 (Expense) | `docs/handbook/finance/policies/spending.md`, `spec/sap-joule-concur-odoo-azure/` | `hr.expense.liquidation` |
| Epic 6 (Payroll) | `ssot/governance/platform-capabilities-unified.yaml` (hr_payroll section) | `hr.payslip`, BIR withholding records |
| Epic 7 (Data Platform) | `spec/adls-etl-reverse-etl/` | Databricks marts, Superset views |

---

## 5. Gap Report

### Missing Artifacts

| Gap | Severity | Recommendation |
|-----|----------|----------------|
| `ipai_bir_tax_compliance` module not found at expected path (`addons/ipai/ipai_bir_tax_compliance/`) | HIGH | Module referenced in spec/ssot but not present in `addons/ipai/`. May be at `addons/` root or unported. Locate and reconcile. |
| `ipai_bir_notifications` module not found | MEDIUM | Referenced as planned/satellite. Scaffold or confirm location. |
| `ipai_bir_plane_sync` module not found | MEDIUM | Referenced as planned/satellite. Scaffold or confirm location. |
| `ipai_finance_workflow` module not found at `addons/ipai/` | LOW | Deprecated module — may be at `addons/` root. Confirm `installable: False`. |
| `ipai_hr_payroll_ph` module not found | HIGH | Referenced in platform capabilities at 70% parity but not found in `addons/ipai/`. |
| No tests exist for any finance module | HIGH | All 5 active modules have `tests: false` in SSOT. Spec Phase 3 is unstarted. |
| Tax Pulse sub-agent tools not implemented | MEDIUM | Spec exists (`spec/tax-pulse-sub-agent/`) but no tool implementations found. |
| Compliance check catalog missing | MEDIUM | Referenced at `infra/ssot/tax/compliance_check_catalog.yaml` but not verified present. |

### Stale Artifacts

| Artifact | Issue | Recommendation |
|----------|-------|----------------|
| `docs/handbook/finance/month-end/checklist.md` references Mattermost | LOW | Update to Slack (Mattermost deprecated 2026-01-28) |
| `ssot/migration/seed_canonical_map.yaml` marks `ipai_finance_workflow` as canonical for stages/projects | HIGH | Conflicts with `spec/finance-unified/constitution.md` Rule 3 which marks it deprecated. Reconcile — `close_seed` should be canonical per spec. |
| `ipai_bir_tax_compliance` version still `18.0.1.0.0` in SSOT | MEDIUM | Spec task T1.5 (version bump) is unstarted. |

### Duplicates / Conflicts

| Conflict | Sources | Resolution |
|----------|---------|------------|
| Seed canonical authority | `spec/finance-unified/` says `close_seed` is canonical; `ssot/migration/seed_canonical_map.yaml` says `finance_workflow` is canonical for stages/projects | Reconcile to single authority. Spec constitution Rule 2 should govern. |
| Month-end task counts | `close_seed` manifest says 39 tasks; seed canonical map says `finance_workflow` has 20 canonical tasks | Clarify which set is authoritative post-reconciliation. |
| BIR task counts | Spec says 50 tasks; seed canonical map says 33 canonical + 27 deprecated | Reconcile actual XML file record counts. |

---

## 6. KPI Alignment

| KPI | Target | Epic Owner | Measurement Source |
|-----|--------|------------|-------------------|
| kpi_002: Expense processing P50 | < 48h | Epic 5 | Odoo `hr.expense.liquidation` state timestamps |
| kpi_003: Monthly close cycle | < 10 business days | Epic 3 | Odoo `project.task` completion dates (Close project) |
| kpi_004: Approval backlog | < 20 items | Epic 5 | Odoo pending approval count |
| kpi_005: BIR filing on-time rate | 100% | Epic 2 | Odoo `ipai.bir.form.schedule` filed-on-time flag |
| kpi_006: Tax reconciliation variance | < 0.1% | Epic 2 | Odoo tax account reconciliation |

---

## 7. Import CSV

The import-ready CSV is at: `docs/boards/finance-ppm-backlog-import.csv`

Columns: `Work Item Type, Title, Parent Title, Tags, Description, Acceptance Criteria`

Import procedure:
1. Navigate to Azure DevOps > ipai-platform > Boards
2. Use "Import Work Items" from CSV
3. The CSV uses Basic process: Epic > Issue > Task
4. Parent-child relationships are established via the `Parent Title` column
5. After import, set up recurring cycle cloning per Section 3

---

*Generated from: spec/finance-unified/, ssot/finance/unified-system.yaml, ssot/governance/enterprise_okrs.yaml, addons/ipai/ipai_finance_*/,  addons/ipai/ipai_hr_expense_liquidation/, docs/handbook/finance/, docs/handbook/compliance/bir/*
*Last updated: 2026-03-18*
