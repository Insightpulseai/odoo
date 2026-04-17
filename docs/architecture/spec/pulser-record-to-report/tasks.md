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
| **Document type** | Platform Engineering Specification (Tasks) |
| **Owner** | Jake Tolentino — CTO, InsightPulseAI |
| **Azure Subscription** | Dev: eba824fb · Sponsored: eba824fb · Prod: see §10 |
| **ADO Org** | dev.azure.com/insightpulseai · Project: ipai-platform |
| **GitHub** | InsightPulseAI/odoo · Repo: github.com/InsightPulseAI/odoo |
| **Contact** | +63 968 269 9265 · business@insightpulseai.com |

---

# Tasks — Pulser Record to Report

## Roadmap Phase 1 — Seed (Foundation & Objects)
## Phase 1 — Domain and object contract
- [x] Define `journal_entry` / `move` contract and required fields (via `account` core)
- [x] Define `vendor_bill` contract (via `account` core)
- [x] Define `customer_invoice` contract (via `account` core)
- [x] Define `payment` contract (via `account_payment` core)
- [/] Define `bank_statement` and `reconciliation_state` (ipai_bank_recon spec in progress)
- [x] Define `budget` contract (via `mis_builder_budget`)
- [ ] Define `accrual_candidate` contract
- [ ] Define `close_checklist_item` contract
- [ ] Define `tax_support_package` contract
- [ ] Define `reporting_pack` contract
- [ ] Define `evidence_document` linkage contract
- [ ] Define `audit_trail_entry` contract

## Phase 2 — GL/AP/AR control surfaces
- [ ] Implement GL posting state and suspense visibility
- [ ] Implement AP unmatched-bill + missing-support dashboards
- [ ] Implement AP accrual candidate generation
- [ ] Implement AR aging and payment application visibility
- [ ] Implement AR dunning candidate generation
- [ ] Implement intercompany readiness check

## Phase 3 — Reconciliation and exception
- [ ] Implement bank reconciliation state computation
- [ ] Implement cross-account reconciliation completeness
- [ ] Implement exception clustering by kind and entity
- [ ] Implement reconciliation blocker tracking

## Phase 4 — Budget and cost control
- [ ] Implement budget vs actual by cost center / analytic
- [ ] Implement overspend candidate detection
- [ ] Implement budget transfer approval chain visibility
- [ ] Implement cost allocation state visibility

## Phase 5 — Cash/bank
- [ ] Implement cash position by bank account
- [ ] Implement bank statement import state
- [ ] Implement cash flow forecast inputs

## Phase 6 — Close
- [x] Implement continuous close-readiness computation
- [ ] Implement Multi-company Close Consensus logic
- [ ] Implement Intercompany gap detection and reconciliation chasers

## Phase 7 — Reporting
- [ ] Implement trial balance pack generation
- [ ] Implement management reporting pack generation
- [ ] Implement executive summary pack generation
- [ ] Implement consolidated Close Pack generation (Trial Balance, Accrual Aging, Compliance Score)
- [ ] Implement statutory/regulatory pack hooks where scoped
- [ ] Preserve evidence linkage in all reporting packs

## Roadmap Phase 2 — Scale (Operational Automation)
## Phase 8 — Tax
- [ ] Implement withholding remittance readiness
- [ ] Implement BIR compliance linkage where applicable
- [ ] Implement BIR 2307 Automated Chaser for withholding compliance

## Phase 9 — Audit and policy
- [ ] Implement audit trail entry generation for material mutations
- [ ] Implement approval chain capture in audit trail
- [ ] Implement audit vault read-only access surface
- [ ] Integrate policy engine with close/tax/reporting mutation paths
- [ ] Implement Agentic Self-Correction loop (Stop-and-Think protocol) for finance mutations
- [ ] Enforce mutation-scope RBAC across AP/AR/controller/tax/treasury/finance-head/audit/admin

## Phase 10 — UX and role surfaces
- [ ] Implement GL Control Cockpit
- [ ] Implement AP Cockpit
- [ ] Implement AR / Collections Cockpit
- [ ] Implement Close Cockpit
- [ ] Implement Cash / Bank Cockpit
- [ ] Implement Tax Cockpit
- [ ] Implement Reporting Workbench
- [ ] Implement Audit Vault (read-only)

## Phase 11 — Publishing and artifacts
- [ ] Implement XLSX reporting pack output
- [ ] Implement DOCX close memo output
- [ ] Implement PPTX executive summary output
- [ ] Preserve evidence linkage in all exports

## Phase 12 — Verification
- [ ] Add Clarify gate checklist for unresolved finance-control ambiguity
- [ ] Add Verify gate checklist for PRD/constitution alignment
- [ ] Record Smart Success Criteria pass/fail disposition
- [ ] Verify audit trail completeness for all material mutations

## Phase 13 — Document Intelligence for Record-to-Report

- [x] Define normalized document schema for finance-document ingestion
- [x] Map `prebuilt-invoice` outputs into AP and accrual-support signals
- [x] Map `prebuilt-receipt` outputs into expense-support and exception signals
- [x] Map `prebuilt-bankStatement` outputs into reconciliation-support signals
- [x] Map `prebuilt-check` outputs where relevant
- [x] Map `prebuilt-layout` / `prebuilt-read` outputs into semi-structured finance-document handling
- [x] Define custom classifier for BIR and local finance-support document families
- [x] Define custom extraction targets for withholding, liquidation, remittance, and cash-advance support documents
- [x] Persist extracted outputs with evidence linkage into Odoo Documents
- [x] Add review/validation step before extracted content affects close, tax, or reporting workflows
 
 ## Phase 14 — Performance Benchmarks
- [ ] Implement SAP Concur-grade Accrual visibility logic (RNI/BNP)
- [ ] Implement Card Hygiene exception cards (>48hr aging)
- [ ] Implement Payout Integrity reconciliation logic (Odoo vs Bank/Gateway)

### 14.1 Specialist Activation: Collections Agent (Plane B)
- **Target Persona**: The "D365 Collections in Outlook" equivalent.
- **Surface**: M365 (Teams/Outlook) + Professional Dashboard.
- **Capability**: Automated dunning candidate identification (via `credit_control`), AR-aging summarization, and AI-assisted invoice chasers.
- **Requirement**: Must link every chaser to the specific `customer_invoice` evidence pack.

## Roadmap Phase 3 — Mature (Agentic Governance)
## Phase 15 — Cash Forecasting (Joule Parity)
- [ ] T-029: Design Cash Forecast Bot contract: balances, open AR/AP, statement reconciliation inputs
- [ ] T-030: Extend ipai-odoo-mcp with cash forecast read models and aggregation endpoints
- [ ] T-031: Create cash-forecast eval dataset: 7/14/30-day scenarios with actual outcomes
- [ ] T-032: Add /cash-forecast slash command and Teams bot invocation flow
- [ ] T-033: Add finance-agent eval harness for cash forecast explanation quality and variance thresholds
