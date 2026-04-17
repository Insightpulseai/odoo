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
| **Document type** | Platform Engineering Specification (Constitution) |
| **Owner** | Jake Tolentino — CTO, InsightPulseAI |
| **Azure Subscription** | Dev: eba824fb · Sponsored: eba824fb · Prod: see §10 |
| **ADO Org** | dev.azure.com/insightpulseai · Project: ipai-platform |
| **GitHub** | InsightPulseAI/odoo · Repo: github.com/InsightPulseAI/odoo |
| **Contact** | +63 968 269 9265 · business@insightpulseai.com |

---

# Constitution — Pulser Record to Report

## 1. Purpose

This bundle governs Pulser capabilities for finance control, reconciliation, close, reporting, cash, tax, and compliance. It defines how Pulser should behave as the finance-control and reporting layer on top of Odoo.

## 2. Benchmark principle

Use Dynamics 365 Finance as the business-process benchmark for:
- general ledger
- accounts payable
- accounts receivable
- budgeting and budget control
- cash and bank management
- cost accounting
- financial reporting
- finance insights
- tax and globalization services

This benchmark informs operating model and scope design only. Pulser must not attempt literal feature or UI parity with Microsoft.

## 3. Odoo-first principle

Odoo remains the transactional system of action for: journal entries, bills and invoices, payments, statements and reconciliations, attachments and evidence, tax-support records, reporting source data.

Pulser provides: control surfaces, exception visibility, guided work, reconciliation assistance, close readiness, publishable reporting packs, evidence-grounded answers.

## 4. Record-to-Report principle

Record-to-Report is not a reporting-only function. It includes: accounting-control visibility, exception and reconciliation tracking, close readiness, evidence readiness, reporting-pack production, tax and compliance support.

## 5. Policy-gated principle

No close-, tax-, approval-, or reporting-sensitive mutation may bypass: RBAC, approval bands, evidence requirements, validator checks, auditability requirements.

## 6. Evidence principle

All material Record-to-Report outputs must retain evidence linkage, including: reconciliation packs, interim close packs, month-end close packs, tax support packs, executive and management reports, board-facing finance presentations where retained.

## 7. Accrual and exception principle

Pulser must make accrual and exception states visible, not implicit. A finance team should be able to identify: AP accrual candidates, missing support, unassigned or unreconciled items, blocked close items, tax-readiness blockers, collections and AR concerns.

## 8. Approval and segregation principle

Pulser must separate: preparer authority, reviewer authority, threshold approver authority, final signoff authority, audit-readonly authority, platform-admin authority.

No directory/contact list may be treated as the source of approval or RBAC truth.

## 9. Channel principle

Pulser may expose finance assistance inside approved Microsoft 365 channels using Microsoft 365 Agents Toolkit and related agent packaging/scaffolding, but such surfaces remain subordinate to: Pulser policy engine, evidence scope, mutation gates, Odoo transactional truth.

## 10. Direct ingress principle

Canonical public and operator ingress for Pulser remains: Azure DNS, direct custom-domain binding to Azure Container Apps origins, certificate binding at the application edge. No Cloudflare and no proxy-based canonical ingress are assumed in this bundle.

## 11. RBAC principle

Record-to-Report behavior must resolve from: surface, tenant, role group, approval band, evidence scope, expertise mode, task type, risk level. AP processors, AR specialists, controllers, tax leads, treasury managers, finance heads, audit viewers, and platform admins must resolve to distinct role groups with distinct mutation scopes.

## 12. Safety principle

Pulser must not:
- auto-post journal entries without policy authorization
- close periods without required checklist completion
- publish reporting packs without evidence linkage
- approve tax filings without dual-approval where policy requires
- mark reconciliations complete without matched evidence
- infer GL balances from weak retrieval — always query authoritative Odoo state

## 13. Audit principle

Every material mutation in the Record-to-Report scope must produce an auditable trail including: actor, timestamp, action, pre-state, post-state, evidence reference, approval chain.

Audit viewers must have read-only access to the full trail.

## 14. Verification principle

All material Record-to-Report work must pass: Clarify gate before final planning when ambiguity remains, Verify gate before merge/release for production-impacting changes.

Verify must check: control coverage, constitutional compliance, Smart Success Criteria coverage, evidence linkage, audit trail completeness, rollback/validation readiness where applicable.

## 15. Document-ingestion principle

Pulser Record to Report may use Azure Document Intelligence as the document-ingestion and structuring layer for finance, close, reconciliation, and tax-support evidence.

### 15.1 Allowed use
Use Document Intelligence for:
- invoice extraction
- receipt extraction
- bank-statement extraction
- check extraction where relevant
- layout/read extraction for semi-structured finance documents
- custom classification and extraction for local finance and tax-support document families

### 15.2 Product rule
Document Intelligence may extract and structure finance evidence, but it does not replace:
- Odoo accounting truth
- Pulser validator and policy gates
- approval controls
- tax/compliance signoff authority

## 16. AI-Benchmark Model Reference

Pulser Record to Report benchmarks its financial extraction and analysis patterns against state-of-the-art specialized financial models, specifically including the phi-4-based **financial-reports-analysis** model pattern.

### 16.1 Pattern Authority
The patterns established by the phi-4 financial model (e.g., optimized SEC 10-K/Q table extraction, formula validation, and multi-document synthesis) serve as the benchmark operating model for Pulser's financial reasoning.

### 16.2 IPAI Specification
While the US-SEC phi-4 model establishes the reasoning pattern, IPAI applies this pattern to specialized local domains:
- **Corpus**: Philippine BIR forms (2550Q, SLSP, SAWT), Odoo account.move records, and peso-denominated financial reports.
- **Authority**: RAG-first architecture over authoritative Odoo transactional truth.
- **Stage**: Stage 1 uses Claude 3.5 Sonnet with direct Odoo/DocAI grounding; Stage 2 moves to Azure AI Foundry fine-tuned local models once sufficient Philippine-labeled finance data exists.
