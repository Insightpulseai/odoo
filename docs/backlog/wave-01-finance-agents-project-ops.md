# Wave 01 — D365 Benchmark Boards Population (Basic process)

> **Authoritative spec for ADO Boards population.**
> **Hierarchy:** `Epic → Issue → Task` (matches the Basic process configured on `insightpulseai/ipai-platform`).
> **Wave action:** Create 3 NEW dedicated benchmark Epics + 13 Issues + 75 Tasks.

## Scope doctrine (canonical, locked)

```
Current benchmark scope is limited to three Microsoft surfaces:
- D365 Finance
- Finance agents
- D365 Project Operations (Core + Integrated with ERP)

Supply Chain, manufacturing-heavy flows, Commerce, and hard-core HR
are NOT current parity targets.
```

Anything matching warehouse, transportation, MRP, payroll, benefits administration, POS, or commerce-channel-ops gets tagged `out-of-scope-current-wave`, not pulled into this pack.

## Why 3 NEW epics (not slot under existing #2/#3)

Latest user direction (2026-04-14): use 3 dedicated benchmark-focused **top-level Epics** for this wave. Process is **Basic** (Epics → Issues → Tasks) — no separate Feature layer. The 3 benchmark Epics give clean per-surface tracking; functional execution still routes through existing operating-model Epics (#2/#3/#4/#5/#6) via dependency links.

**Tags applied to all work items:** `pulser-odoo; benchmark; odoo-azure`
- Add `d365-finance` + `finance-parity` to Tree 1 items
- Add `finance-agents` to Tree 2 items
- Add `project-operations` to Tree 3 items

**Dependency links only — do NOT duplicate buckets/tasks under these:**
- `[OBJ-002]` ERP Enterprise Parity (#2)
- `[OBJ-003]` Foundry Agent Runtime & Copilot (#3)
- `[OBJ-004]` Data Intelligence & OLTP/OLAP Separation (#4)
- `[OBJ-005]` Developer Experience & Automation Consolidation (#5)
- `[OBJ-006]` Security, Compliance & BIR (#6)

---

## Tree 1 — Epic: D365 Finance Parity

### Issue: Finance Core Capabilities and Use Cases
- Task: Define Finance core-capability parity map
- Task: Define Finance use-case catalog
- Task: Define organization and legal-entity model
- Task: Define accounting currency and reporting currency model
- Task: Define Finance tax capability scope
- Task: Define cost-accounting concept parity

### Issue: General Ledger and Financial Foundation
- Task: Define general-ledger parity scope
- Task: Define chart-of-accounts and main-account model
- Task: Define fiscal-calendar model
- Task: Define financial-dimensions and dimension-set model
- Task: Define accounting-structure model
- Task: Define financial-journal model
- Task: Define periodic financial-process model

### Issue: Accounts Payable and Accounts Receivable
- Task: Define core accounts-payable parity scope
- Task: Define vendor payments, settlements, and three-way-matching model
- Task: Define core accounts-receivable parity scope
- Task: Define credit-management parity scope
- Task: Define collections-process parity scope
- Task: Define subscription-billing parity scope

### Issue: Expense, Cash, Fixed Assets, and Budgeting
- Task: Define cash-and-bank-management parity scope
- Task: Define expense-management parity scope
- Task: Define fixed-asset-management parity scope
- Task: Define budgeting parity scope

### Issue: Finance and Operations Common Capabilities
- Task: Define finance and operations apps equivalent for Odoo on Azure
- Task: Define ERP value proposition and use-case mapping
- Task: Define reporting and workspace equivalent
- Task: Define Power BI analysis options for Finance
- Task: Define Microsoft 365 integration equivalent
- Task: Define Power Platform integration substitution model
- Task: Define security capability baseline
- Task: Define workflow capability baseline
- Task: Define batch-job capability baseline

**Tree 1 totals:** 5 Issues + 34 Tasks

---

## Tree 2 — Epic: Finance Agents Parity

### Issue: Finance Agents Operating Model
- Task: Define Finance agents-to-Pulser equivalent map
- Task: Define Finance agents architecture and data-handling equivalent
- Task: Define admin-deployed vs business-user-deployed equivalent model
- Task: Define Finance agents governance and approval model
- Task: Define Finance agents channel strategy for Odoo, Outlook, Slack, and exports

### Issue: Financial Reconciliation Agent
- Task: Define Financial Reconciliation agent parity scope
- Task: Define reconciliation data sources and evidence model
- Task: Define reconciliation workflow, approval, and logging model
- Task: Define reconciliation UAT and release gating

### Issue: Collections in Outlook Equivalent
- Task: Define Collections in Outlook parity scope
- Task: Define Outlook/M365 bridge requirements
- Task: Define collections communication workflow and guardrails
- Task: Define collections evidence, traceability, and follow-up model

### Issue: Finance Agent Surfaces and Governance
- Task: Define Excel-surface substitution strategy
- Task: Define Outlook-surface substitution strategy
- Task: Define in-Odoo finance assistant UX
- Task: Define finance-agent telemetry, safety, and disablement model

**Tree 2 totals:** 4 Issues + 17 Tasks

---

## Tree 3 — Epic: D365 Project Operations Parity

### Issue: Project Operations Core Guidance
- Task: Define Project Operations Core-to-Odoo equivalent map
- Task: Define Project Operations Core security, compliance, and privacy model
- Task: Define Project Operations Core implementation guide equivalent
- Task: Define Project Operations Core implementation tools and samples baseline
- Task: Define Project Operations Core try/buy/deploy benchmark model
- Task: Define Project Operations Core admin and development baseline

### Issue: Project Operations Core Functional Parity
- Task: Define Project Operations Core sales process parity
- Task: Define Project Operations Core price-list parity
- Task: Define Project Operations Core project-management parity
- Task: Define Project Operations Core resource-management parity
- Task: Define Project Operations Core demo/configuration-data equivalent
- Task: Define Project Operations Core DSR/privacy-response equivalent

### Issue: Project Operations Integrated with ERP Guidance
- Task: Define Project Operations Integrated-with-ERP-to-Odoo equivalent map
- Task: Define Project Operations Integrated with ERP security, compliance, and privacy model
- Task: Define Project Operations Integrated with ERP implementation guide equivalent
- Task: Define Project Operations Integrated with ERP implementation tools and samples baseline
- Task: Define Project Operations Integrated with ERP try/buy/deploy benchmark model
- Task: Define Project Operations Integrated with ERP admin and development baseline

### Issue: Project Operations Integrated with ERP Functional Parity
- Task: Define project management and accounting parity
- Task: Define work breakdown structures parity
- Task: Define project resourcing parity
- Task: Define project schedule API and automation equivalent
- Task: Define Common Data Service / Dataverse dependency substitution model
- Task: Define Power Automate scheduling-entity equivalent
- Task: Define configuration-data and onboarding equivalent
- Task: Define DSR and privacy process equivalent

**Tree 3 totals:** 4 Issues + 26 Tasks

---

## Grand totals

- **3 NEW Epics** (D365 Finance Parity, Finance Agents Parity, D365 Project Operations Parity)
- **13 Issues**
- **77 Tasks**
- **93 work items total**

## Doctrine alignment

- **Plane A (ERP)** = Tree 1 + Tree 3 → `feedback_d365_two_plane_doctrine.md` + `feedback_d365_project_operations_services_erp.md`
- **Plane B (Copilot)** = Tree 2 → `feedback_d365_two_plane_doctrine.md`
- All Tasks inherit module-selection doctrine: CE → property fields → OCA same-domain → adjacent → compose → thin `ipai_*` last (`feedback_odoo_module_selection_doctrine.md`)
- Items map to `ssot/benchmarks/parity_matrix.yaml` rows where applicable

## Iteration targets

- **R1-Foundation-30d** (active 2026-04-14 → 2026-05-14): all P0 "Define X" tasks — definition work fits the foundation iteration
- **R2-Core-Execution-60d** (May 15 → Jul 14): functional-parity hardening + agent build
- **R3+**: production hardening + GA

## Process note

This wave uses **Basic process** hierarchy explicitly:

```
Epic
  → Issue
    → Task
```

NOT `Epic → Feature → Story → Task`. Adding a Feature backlog level requires Azure DevOps process customization, which is out of scope for this wave.

If a stricter portfolio hierarchy is desired later, customize the process and re-evaluate.
