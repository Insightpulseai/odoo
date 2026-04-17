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

# Plan — Pulser Record to Report

## 1. Goal

Implement a production-grade Record-to-Report capability on Odoo with Pulser as the governed finance-control, reconciliation, close, and reporting layer.

## 2. Architecture approach

### 2.1 System of action
Odoo accounting modules remain the transactional and evidence-linked system of action.

### 2.2 Pulser role
Pulser provides: finance-control surfaces, exception visibility, reconciliation assistance, close readiness, publishable reporting packs, tax evidence packaging, audit trail generation.

### 2.3 Runtime
Record-to-Report functionality runs across: Odoo runtime, Pulser agent/runtime, export/publishing services, audit vault, optional channel surfaces.

## 3. Workstreams

### W1 — GL/AP/AR control surfaces
Define finance-control visibility for general ledger, accounts payable, and accounts receivable.

### W2 — Reconciliation and exception surfaces
Define reconciliation completeness tracking and exception clustering.

### W3 — Budget and cost-control surfaces
Define budget vs actual, cost allocation, and overspend detection.

### W4 — Cash/bank support views
Define cash position, bank reconciliation, and cash flow forecast inputs.

### W5 — Close checklist and blocker model
Define close-readiness state, blocker kinds, and remediation flows.

### W6 — Publishable reporting packs
Define XLSX/DOCX/PPTX export contracts with evidence linkage.

### W7 — Tax/compliance evidence packaging
Define tax support package structure and filing-readiness signals.

### W8 — Audit trail and policy gating
Define mutation audit contract and policy engine integration points.

## 4. Domain decomposition

### 4.1 Control-surface domain
GL/AP/AR/budget/cash/bank/cost observability, exception clustering.

### 4.2 Close domain
close checklist state, blocker tracking, journal review, period lock readiness.

### 4.3 Reporting domain
pack generation, evidence linkage, template management, publishing gates.

### 4.4 Tax domain
filing deadlines, support packaging, remittance readiness, e-invoicing state.

### 4.5 Audit domain
mutation trail, approval chain, evidence vault, read-only access.

## 5. Data and model rules

- Odoo accounting truth is authoritative. Pulser never substitutes computed state for ledger state.
- Reconciliation state must be recomputable and idempotent.
- Accrual candidates must be derived, timestamped, and revocable.
- Reporting packs must regenerate deterministically from source state.
- Audit trail entries are append-only and immutable.

## 6. UX model

### 6.1 GL Control Cockpit
For: finance controller, finance head. Exception-first view of posting state, suspense accounts, intercompany readiness.

### 6.2 AP Cockpit
For: AP processor, AP manager. Unmatched bills, missing support, accrual candidates, batch payment preparation.

### 6.3 AR / Collections Cockpit
For: AR specialist, collections manager. Aging buckets, dunning candidates, payment application state.

### 6.4 Close Cockpit
For: finance controller, finance head. Checklist-driven close-readiness view with blocker tracking.

### 6.5 Cash / Bank Cockpit
For: treasury manager, controller. Bank reconciliation state, cash position, forecast inputs.

### 6.6 Tax Cockpit
For: tax lead. Filing deadlines, support completeness, remittance readiness, e-filing state.

### 6.7 Reporting Workbench
For: controller, finance head. Pack generation with evidence linkage and policy gates.

### 6.8 Audit Vault
For: audit viewer. Read-only mutation trail, approval chain, evidence access.

## 7. Channel strategy

- Odoo and Pulser web surfaces remain primary
- M365/Teams channel surfaces are optional and additive for approvers/viewers
- Microsoft 365 Agents Toolkit may accelerate Teams/M365 surface creation
- channel surfaces must consume canonical Pulser APIs and policy resolution

## 8. Validation and quality gates

### 8.1 Clarify gate
Required before detailed planning if: close checklist semantics are unclear, accrual rules are unclear, dunning policy is unclear, reconciliation thresholds are unclear, tax package structure is unclear.

### 8.2 Verify gate
Required before merge/release to confirm: PRD alignment, constitutional compliance, evidence linkage, audit trail completeness, Smart Success Criteria disposition, rollback/validation readiness.

## 9. Dependencies

- umbrella `pulser-odoo` bundle
- Odoo accounting core
- Odoo Documents
- Pulser policy engine
- Pulser publishing/export layer
- BIR compliance bundle
- close orchestration bundle
- optional Teams/M365 channel integration if chosen

## 10. Non-goals for this implementation phase

- full ERP replacement of Odoo accounting
- advanced cost-allocation parity with Dynamics Cost Accounting module
- replacement of tax engines or filing platforms
- deep treasury management platform features beyond bounded close needs

## 10. Document-ingestion workstream

### Goal
Use Azure Document Intelligence to normalize finance and tax-support documents into structured Pulser inputs.

### Model strategy

- use `prebuilt-invoice` for AP document extraction
- use `prebuilt-receipt` for expense and support extraction
- use `prebuilt-bankStatement` for reconciliation support
- use `prebuilt-check` where relevant
- use `prebuilt-layout` and `prebuilt-read` for semi-structured finance documents
- use custom classifier + custom extraction for BIR and local finance-support document families

### Design rules
- extraction output must be reviewable and evidence-linked
- extracted content must not bypass accounting, approval, or tax-support validation
- US tax models are optional and only for supported US tax forms
