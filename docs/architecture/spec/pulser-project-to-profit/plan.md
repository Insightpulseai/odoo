# <center>InsightPulseAI</center>
# <center>Pulser · Odoo on Azure Agentic ERP</center>

## <center>Platform Engineering Specification</center>
### <center>Version 0.6 · April 2026 · CONFIDENTIAL</center>

| Metadata | Value |
| :--- | :--- |
| **Product** | Pulser — Philippine SMB Agentic ERP |
| **Platform** | Odoo 18 CE on Azure Container Apps (SEA) |
| **ERP Domains** | Finance (R2R) · Project Operations (P2P) · Operations (S2P/O2C) |
| **Agent Framework** | Microsoft Agent Framework + Microsoft Foundry (ipai-copilot) |
| **Document type** | Platform Engineering Specification (Execution Plan) |
| **Owner** | Jake Tolentino — CTO, InsightPulseAI |
| **Azure Subscription** | Dev: eba824fb · Sponsored: eba824fb · Prod: see §10 |
| **ADO Org** | dev.azure.com/insightpulseai · Project: ipai-platform |
| **GitHub** | InsightPulseAI/odoo · Repo: github.com/InsightPulseAI/odoo |
| **Contact** | +63 968 269 9265 · business@insightpulseai.com |

---

# Plan — Pulser Project to Profit

## 1. Goal

Implement a production-grade Project-to-Profit capability on Odoo with Pulser as the governed planning, execution-analysis, profitability, and publishing layer.

## 2. Architecture approach

### 2.1 System of action
Odoo CE/OCA 18 remains the transactional and evidence-linked system of action.

### 2.2 Pulser role
Pulser provides: guided setup, planning quality checks, execution summarization, profitability and readiness analysis, policy-gated action recommendations, publishable outputs.

### 2.3 Runtime
Project-to-Profit functionality runs across: Odoo runtime, Pulser agent/runtime, export/publishing services, optional channel surfaces.

## 3. Workstreams

### W1 — Commercial handoff and contract model
Define how quote/proposal/contract context enters the project shell.

### W2 — WBS and milestone model
Define hierarchy, assignment, dependency, readiness, and milestone semantics.

### W3 — Forecast and budget separation
Define distinct objects, update rules, ownership, and reporting treatment.

### W4 — Execution signal layer
Derive actionable signals from tasks, timesheets, expenses, vendor cost, and blocker state.

### W5 — Billing-readiness model
Define how contract, milestone, evidence, and completeness become billing-readiness signals.

### W6 — Profitability and variance model
Define project-level and portfolio-level variance, margin, and profitability views.

### W7 — Publishing and evidence linkage
Define XLSX/DOCX/PPTX exports with retained source/evidence linkage.

## 4. Domain decomposition

### 4.1 Initiate domain
project shell, client/engagement metadata, contract references, commercial assumptions, WBS starter, budget/forecast baseline, evidence pack.

### 4.2 Execute domain
task status, milestone status, owner accountability, time/expense/cost completeness, blocker state, change signal state.

### 4.3 Analyze domain
forecast variance, budget variance, margin variance, portfolio aggregation, billing readiness, executive reporting.

## 5. Data and model rules

- Forecasts must remain editable planning artifacts.
- Budgets must remain control-oriented baselines.
- Actuals must be grounded in Odoo transactional records.
- Billing-readiness signals must be recomputable and auditable.
- Health snapshots must be derived and timestamped, not hand-waved narrative only.

## 6. UX model

### 6.1 Project Setup Workbench
For: scope handoff, contract/billing model, WBS setup, budget/forecast baseline.

### 6.2 Delivery Cockpit
For: PMs, team leads, project owners.

### 6.3 Project Finance Cockpit
For: project finance controller, finance controller.

### 6.4 Portfolio / Executive Cockpit
For: finance head, executive viewers, portfolio owners.

## 7. Channel strategy

- Odoo and Pulser web surfaces remain primary
- M365/Teams channel packaging is optional and additive
- Microsoft 365 Agents Toolkit may accelerate Teams/M365 custom-engine surface creation
- channel surfaces must consume canonical Pulser APIs and policy resolution, not custom ad hoc behavior

## 8. Validation and quality gates

### 8.1 Clarify gate
Required before detailed planning if: contract and billing semantics are unclear, margin formulas are unclear, baseline ownership is unclear, publish/readiness semantics are unclear.

### 8.2 Verify gate
Required before merge/release to confirm: PRD alignment, constitutional compliance, evidence linkage, Smart Success Criteria disposition, rollback/validation notes where applicable.

## 9. Dependencies

- umbrella `pulser-odoo` bundle
- Odoo project/task foundation
- Odoo accounting and billing surfaces
- Odoo Documents
- Pulser policy engine
- Pulser publishing/export layer
- optional Teams/M365 channel integration if chosen

## 10. Non-goals for this implementation phase

- full resource-management parity with Microsoft
- advanced workforce scheduling productization beyond bounded project needs
- replacement of core Odoo accounting objects
- deep CRM replacement

## 11. Document-ingestion workstream

### Goal
Use Azure Document Intelligence to normalize project and commercial documents into structured Pulser inputs.

### Model strategy
- use `prebuilt-contract` for agreements where it fits
- use `prebuilt-invoice` for invoice extraction
- use `prebuilt-receipt` for expense/support extraction
- use `prebuilt-layout` and `prebuilt-read` for semi-structured project documents
- use custom classifier + custom extraction for project-specific document families

### Design rules
- extraction output must be reviewable
- extracted fields must remain evidence-linked
- extracted content must not be treated as authoritative without Pulser validation where the workflow is sensitive
