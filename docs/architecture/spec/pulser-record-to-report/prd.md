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
| **Document type** | Platform Engineering Specification (PRD) |
| **Owner** | Jake Tolentino — CTO, InsightPulseAI |
| **Azure Subscription** | Dev: eba824fb · Sponsored: eba824fb · Prod: see §10 |
| **ADO Org** | dev.azure.com/insightpulseai · Project: ipai-platform |
| **GitHub** | InsightPulseAI/odoo · Repo: github.com/InsightPulseAI/odoo |
| **Contact** | +63 968 269 9265 · business@insightpulseai.com |

---

# PRD — Pulser Record to Report

## 1. Executive summary

Pulser Record to Report implements a governed finance-control, close, reporting, cash, and tax operating model on Odoo.

It turns Odoo into a system where:
- GL, AP, AR, bank, and tax state is continuously observable as control surfaces
- reconciliation and exception states are explicit, not implicit
- close readiness is continuously measurable, not discovered at period-end
- publishable reporting packs are evidence-linked and policy-safe
- tax and compliance readiness is tracked alongside accounting truth
- audit trails are complete and inspectable

## 12. Document-ingestion principle

Pulser Record to Report may use Azure Document Intelligence as the document-ingestion and structuring layer for finance, close, reconciliation, and tax-support evidence.

### 12.1 Allowed use
Use Document Intelligence for:
- invoice extraction
- receipt extraction
- bank-statement extraction
- check extraction where relevant
- layout/read extraction for semi-structured finance documents
- custom classification and extraction for local finance and tax-support document families

### 12.2 Product rule
Document Intelligence may extract and structure finance evidence, but it does not replace:
- Odoo accounting truth
- Pulser validator and policy gates
- approval controls
- tax/compliance signoff authority

## 16. Azure Document Intelligence integration

Record-to-Report should use Azure Document Intelligence as the ingestion layer for finance evidence and support documents.

### 16.1 Prebuilt models to use where they fit
Preferred prebuilt models:
- `prebuilt-invoice`
- `prebuilt-receipt`
- `prebuilt-bankStatement`
- `prebuilt-check`
- `prebuilt-layout`
- `prebuilt-read`

### 16.2 Custom model strategy
Use custom classification and custom extraction for local or organization-specific document families, such as:
- BIR support documents
- withholding certificates
- remittance proofs
- liquidation forms
- cash advance support
- agency/client-specific finance attachments

### 16.3 US tax model rule
Use Azure Document Intelligence US tax models only for supported US tax forms.
Do not use US tax prebuilt models as the default approach for PH/BIR workflows.

### 16.4 Expected outputs
Document ingestion should normalize into:
- AP and accrual candidates
- reconciliation evidence
- close blockers
- tax-support packages
- evidence-linked reporting packs

### 16.5 Product rule
Document Intelligence is an extraction layer only.
Pulser remains responsible for:
- policy gating
- reconciliation logic
- close readiness
- role-aware action routing
- tax/compliance support packaging

This bundle uses the Dynamics 365 Finance operating model as the benchmark for scope but implements that behavior in an Odoo-first, Pulser-governed architecture.

## 2. Problem statement

Typical Odoo finance deployments fail at Record-to-Report in six ways:
1. Close is a monthly scramble instead of a continuous control.
2. Reconciliation state is invisible until someone queries it manually.
3. AP accruals and missing support are discovered late.
4. AR and collections visibility is fragmented across spreadsheets and email.
5. Reporting packs are reconstructed every period, not continuously available.
6. Tax readiness is separate from accounting truth instead of tied to it.

Pulser must solve these problems by making finance control continuously observable, exception-driven, and evidence-backed.

## 3. Product goal

Implement a bounded Record-to-Report capability on top of Odoo that supports:
- GL, AP, AR finance-control visibility
- continuous reconciliation tracking
- close readiness and blocker visibility
- budget and cost-control surfaces
- cash and bank support views
- publishable reporting packs
- tax and compliance evidence packaging
- complete audit trails

## 4. Non-goals

This bundle does not attempt to:
- replace Odoo accounting modules
- implement all Microsoft Finance product surfaces literally
- own project delivery or profitability (that lives in Project-to-Profit)
- bypass Odoo's accounting truth
- introduce a parallel GL

Those concerns belong in Project-to-Profit or the umbrella Pulser bundle.

## 5. Primary users

### 5.1 AP processor / AP manager
Needs: invoice matching, exception visibility, accrual candidate tracking, vendor support completeness, batch payment preparation.

### 5.2 AR specialist / collections manager
Needs: customer invoice status, payment application, dunning readiness, collections aging, credit exposure.

### 5.3 Finance controller
Needs: period close status, reconciliation blockers, journal review, intercompany readiness, management reporting.

### 5.4 Tax lead
Needs: tax support package completeness, filing readiness, evidence linkage for returns, compliance deadline tracking.

### 5.5 Treasury manager
Needs: cash position visibility, bank reconciliation state, cash flow forecast, liquidity exposure.

### 5.6 Cash Forecasting (Joule Parity)
- **User Story**: As CKVC or RIM, I can request a rolling 7/14/30-day cash forecast and receive a projected daily position based on bank balances, open receivables, open payables, and reconciled statement activity, with key drivers and exceptions explained.
- **Acceptable Criteria**:
    - Generation completes in <20 seconds for a 30-day horizon on 12-month ledger history.
    - Forecast explanation identifies top drivers with traceable source records for ≥95% of movements.
    - Forecast variance vs actual daily closing cash is within pilot tolerance for ≥80% of forecast days.

### 5.6 Finance head
Needs: consolidated close readiness, cross-entity reporting, executive reporting packs, audit-readiness summaries.

### 5.7 Audit viewer
Needs: read-only evidence vault, complete mutation trail, approval chain visibility.

### 5.8 Platform administrator
Needs: configuration and workflow governance, no business approval rights.

## 6. Functional scope

### 6.1 GL control
Pulser must surface: journal posting status, trial balance completeness, suspense account state, intercompany readiness, period lock state.

### 6.2 AP control
Pulser must surface: unmatched bills, missing support, accrual candidates, payment batch readiness, vendor master exception state, AP aging.

### 6.3 AR control
Pulser must surface: unpaid invoices by aging bucket, collections follow-up candidates, credit-note coverage, customer payment application completeness, dunning readiness.

### 6.4 Budget control
Pulser must surface: budget vs actual by cost center / department / analytic, overspend candidates, budget transfer state, approval chain status.

### 6.5 Cash and bank
Pulser must surface: bank statement import state, unreconciled bank items, cash position by bank account, pending wires and transfers, cash flow forecast inputs.

### 6.6 Cost accounting
Pulser must surface: cost allocation state, department/project overhead coverage, cost driver completeness, cost-center variance.

### 6.7 Reporting
Pulser must produce: trial balance packs, management reporting packs, executive summary packs, board packs where retained, regulatory or statutory packs where policy requires.

### 6.8 Tax
Pulser must surface: filing deadlines, filing-ready evidence packages, input-tax reconciliation state, withholding remittance readiness, e-invoicing/e-filing state where applicable.

### 6.9 Close
Pulser must surface: close checklist status, blocker count and kind, accrual readiness, reconciliation completeness, journal-review state, reporting-pack readiness.

### 6.10 Reporting Benchmarks
- **Standards**: SAP Concur-grade analytics for **Accruals** (outstanding liabilities), **Card Hygiene** (unassigned/unsubmitted), and reconciliation.
- **Accrual Visibility**: 100% visibility into received-not-invoiced and billed-not-posted states.
- **Card Hygiene**: Exception cards for transactions > 48hrs without submission/receipt.

### 6.11 Close Pack KPIs
The R2R bundle must natively support the generation of standardized Close Packs:
- **Trial Balance Integrity**: Variance analysis vs previous period and budget.
- **Accrual Aging**: Outstanding liabilities by transaction date and vendor category.
- **Payout Integrity**: Reconciliation of Odoo processed items vs Bank/Payment gateway status.
- **Compliance Score**: % of close evidence verified vs mandatory checklist.

### 6.12 Finance Operating Surface (Cockpits)
Pulser must deliver role-based **Cockpits** rather than simple chat:
- **Finance Head**: Close Cockpit, BIR Compliance Cockpit, and Exec Brief.
- **Finance Manager**: Reconciliation Cockpit and Close Task Management.
- **AP/Expense/Treasury**: High-density work queues (AP Queue, Exceptions Cockpit).
- **Tax Lead**: BIR Compliance Cockpit and Rule-based Exception cards.
- **Auditor**: Read-only Evidence Vault views.

## 7. Core objects

The minimum domain contract for this bundle is:
- `journal_entry` / `move`
- `vendor_bill`
- `customer_invoice`
- `payment`
- `bank_statement`
- `reconciliation_state`
- `budget`
- `accrual_candidate`
- `close_checklist_item`
- `tax_support_package`
- `reporting_pack`
- `evidence_document`
- `audit_trail_entry`

These may map to multiple Odoo/OCA/local models, but the contract must exist.

## 8. Functional requirements

### FR-1 Continuous close visibility
Pulser must compute close-readiness state continuously, not only at period-end.

### FR-2 Exception-driven surfaces
All finance-control surfaces must be exception-first: show what needs attention before showing what is healthy.

### FR-3 Reconciliation state
Pulser must compute and expose reconciliation completeness for every scoped account and entity.

### FR-4 Accrual candidate generation
Pulser must derive AP accrual candidates from received-not-invoiced and billed-not-posted state.

### FR-5 Collections workflow support
Pulser must compute dunning and follow-up candidates from AR aging and payment behavior.

### FR-6 Evidence linkage
All material outputs must retain source-record linkage to Odoo Documents or transactional records.

### FR-7 Reporting pack generation
Pulser must produce XLSX, DOCX, and PPTX reporting packs with retained evidence linkage.

### FR-8 Tax readiness signals
Pulser must track filing deadlines, required support, and filing-ready state for scoped tax obligations (including BIR compliance where applicable).

### FR-9 Audit trail
Every material mutation must produce a complete audit trail entry with actor, timestamp, action, state diff, evidence reference, and approval chain.

### FR-10 Policy gating
All close, tax, and approval-sensitive mutations must pass through Pulser policy engine evaluation before commit.

### FR-11 Partner operations and revenue-ops integration
The product must support R2R-specific partner-operations integrations with Partner Center workspaces where relevant for:
- incentive and rebate tracking (earnings management)
- customer-billing governance (Azure/M365 subscription management)
- partner-earnings reconciliation and revenue-ops reporting
- audit-readiness for partner-program compliance

## 9. UX requirements

### 9.1 Default surfaces
- GL Control Cockpit
- AP Cockpit
- AR / Collections Cockpit
- Close Cockpit (checklist-driven)
- Cash / Bank Cockpit
- Tax Cockpit
- Reporting Workbench
- Audit Vault (read-only)

### 9.2 Interaction model
- cockpit-first for all finance roles
- exception-first display order
- evidence visible next to every material claim
- chat as drill-down reasoning, not primary workflow
- publishable outputs gated on evidence-completeness check

### 9.3 Expertise modes
- beginner = guided control surfaces with more explanation
- intermediate = grouped exception clusters with moderate density
- expert = compact high-density surfaces with keyboard-first navigation

## 10. Channel and distribution requirements

Pulser Record to Report may be surfaced through: Odoo native UI, Pulser web/control surfaces, Microsoft 365 channels via Microsoft 365 Agents Toolkit scaffolding where justified.

Channel surfaces must remain subordinate to Pulser policy, evidence, and mutation controls. No channel surface may bypass approval bands or audit requirements.

### 10.1 Partner operations doctrine (R2R)
For Microsoft-partner execution, Pulser R2R will adapt around **Partner Center** as the native partner-operations system for incentive/rebate tracking, customer-billing governance, and revenue-ops reporting, using thin integrations instead of duplicative custom backoffice tooling.

## 11. Security and policy requirements

- RBAC must be role-group-based across AP, AR, controller, tax, treasury, finance head, audit, and platform-admin scopes
- approval bands must remain separate from role groups
- evidence visibility must be scoped by entity and role
- no unauthorized journal posting, period close, or tax filing
- no reporting-pack publication without evidence-linked source state
- no hidden fallback mutation after failed validation
- audit viewers must have read-only access to the full mutation trail

## 12. Integration requirements

This bundle must integrate with: Odoo accounting core (account.move, account.move.line), AP/AR/bank modules, tax/fiscal modules, OCA reconciliation modules where used, Odoo Documents, Pulser policy engine, Pulser publishing/export layer, BIR compliance bundle, close orchestration bundle, optional Teams/M365 channel surfaces where justified.

## 13. Risks

- close surfaces become narrative-only instead of exception-driven
- reconciliation state is computed but not made authoritative
- accrual candidates become noisy without filtering
- reporting packs diverge from Odoo authoritative state
- tax readiness becomes disconnected from accounting truth
- audit trail becomes incomplete for AI-assisted mutations
- channel surfaces bypass approval bands

## 14. Clarify gate checklist

This bundle must be clarified before planning if any of the following are unresolved:
- close checklist definition by entity type
- AP accrual rules by vendor/expense type
- AR dunning policy and escalation paths
- reconciliation completeness threshold
- tax package structure by filing type
- audit-trail retention requirements
- cross-entity consolidation rules

## 15. Smart Success Criteria

- **SC-RTR-01 Close control coverage:** 100% of scoped close steps represented in Pulser checklist/control surfaces
- **SC-RTR-02 Reconciliation visibility:** at least 90% of scoped reconciliation items visible in dashboards
- **SC-RTR-03 AP exception coverage:** 100% of scoped AP/accrual exceptions visible in Pulser
- **SC-RTR-04 AR and collections visibility:** at least 90% of scoped receivable and collection signals visible in Pulser
- **SC-RTR-05 Cash/bank readiness:** at least 90% of scoped bank/cash reconciliation signals visible in Pulser
- **SC-RTR-06 Reporting pack readiness:** 100% of publishable close/reporting outputs retain evidence linkage
- **SC-RTR-07 Tax readiness:** 100% of scoped tax/filer-support outputs remain evidence-linked and policy-gated
- **SC-RTR-08 Audit trail completeness:** 100% of material mutations produce complete audit trail entries
- **SC-RTR-09 Policy gating:** 100% of close/tax/approval-sensitive mutations pass through policy engine evaluation
- **SC-RTR-10 Publishable outputs:** 100% of scoped reporting packs can generate native XLSX, DOCX, and PPTX
- **SC-RTR-11 Cash forecast latency:** /cash-forecast 30-day projection completes in <20 seconds.
- **SC-RTR-12 Cash forecast explainability:** projected movements with traceable driver records ≥95%.
- **SC-RTR-13 Cash forecast accuracy:** daily variance within pilot tolerance for ≥80% of days.
- **SC-RTR-14 Partner-ops financial compliance:** 100% of scoped incentives, rebates, and partner-billings managed via Partner Center native data and workflows

## 16. Specialist Execution Engines (BOM-03)

The Record to Report bundle governs the following specialized agentic execution engines:

### 16.1 AP Invoice Agent (AP-01) — Phase 2
- **Automatic Matching**: Match vendor bills (PDF/OCR) to Odoo Purchase Orders or Receipts.
- **Tax Compliance**: Calculate EWT/VAT based on TaxPulse SSOT rules for Philippine entities.
- **Fail-Closed Governance**: Hard gate to prevent posting bills with ambiguous tax mappings or missing evidence.
- **Evidence-Backed**: Generate an agent evidence pack for every posted supplier bill.

### 16.2 Bank Reconciliation Agent (BR-01) — Phase 2
- **Automation Target**: 80%+ of high-confidence matches with zero human intervention.
- **Matching Search**: Multi-vector search using Reference, Amount (exact/delta), Date proximity, and Name.
- **Exception Orchestration**: States: `ingested` → `matched` → `ambiguous` → `exception` → `quarantined`.
- **Transparency**: Link every match to a specific Odoo `account.move` or `account.payment`.

### 16.3 TaxPulse BIR Integration (TX-01) — Phase 2
- **Phase 1 Foundation**: Basic evidence capture and audit trail for filing periods.
- **Phase 2 Operational Lane**: Lifecycle support for **eBIRForms**, **eFPS** (filing), **ePAY** (payment), and **eAFS** (attachments).
- **Phase 3 Strategic Lane**: Autonomous Filing, Registration update support (**ORUS**) and software certification readiness (**eTSPCert**).
- **Evidence Timeline**: Track filing status by entity and period: `draft` → `filed` → `paid` → `evidenced`.
- **Attachment Packs**: Standardized eAFS bundles per RMC 17-2024 and applicable RMOs.

## 17. Document-ingestion principle (Refined)
Pulser R2R uses Azure Document Intelligence as the authoritative ingestion layer for finance evidence.
- **Prebuilt Models**: `prebuilt-invoice`, `prebuilt-receipt`, `prebuilt-bankStatement`.
- **Custom Mapping**: Use custom classifiers for BIR-specific support documents (2307, 1601-C).
- **Rule**: Document Intelligence is an extraction layer only; Pulser remains the policy/accounting authority.

## 18. Release Gates: Cash Forecasting (G-CF)
Before the Cash Forecast Bot is promoted to GA, it must satisfy:
- **G-CF-01**: 100% pass on `tests/finance/test_cash_forecast_inputs.py`.
- **G-CF-02**: ≥95% score on `evals/capability/finance/cash_forecast_eval.yaml`.
- **G-CF-03**: Numerical variance within pilot thresholds on `datasets/finance/cash_forecast/golden_set.jsonl`.
