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

# Constitution — Pulser Project to Profit

## 1. Purpose

This bundle governs Pulser capabilities that connect commercial setup, project planning, delivery execution, project finance, billing readiness, and profitability control.

It defines the rules for implementing a Project-to-Profit operating model on top of:
- Odoo CE/OCA 18 as the transactional system of action
- Pulser as the guided control, intelligence, reporting, and publishing layer
- Odoo Documents as the retained evidence surface
- Azure-native runtime, identity, and observability infrastructure

## 2. Benchmark principle

Use Dynamics 365 Project Operations as the business-process benchmark for:
- quote and commercial handoff
- project contract setup
- work breakdown structure
- resource and delivery planning
- project execution
- forecast and budget control
- project accounting and profitability analysis

This benchmark informs operating model and workflow design only.
Pulser must not attempt literal screen-for-screen or schema-for-schema parity with Microsoft products.

## 3. Odoo-first principle

Odoo remains the transactional system of action for:
- project records
- tasks and milestones
- timesheets
- expenses
- sales and billing objects
- accounting postings
- attachments and evidence

Pulser may: guide, summarize, validate, reconcile, forecast, publish, route, surface exceptions, generate artifacts.

Pulser may not: bypass Odoo truth, silently mutate records without policy allowance, bypass approvals or evidence controls, substitute grounded signals with unverified synthesis.

## 4. Lifecycle principle

All Project-to-Profit features must map to these phases: Initiate, Execute, Analyze. No feature may be added if it cannot be clearly placed in one of these lifecycle phases.

## 5. Forecast vs budget principle

Forecasts and budgets are distinct controls.

Forecasts support: operational planning, expected cost/revenue outlook, delivery adjustments, PM and controller visibility.

Budgets support: financial control, approval discipline, baseline governance, formal variance comparison.

A design that collapses forecast and budget into one uncontrolled object violates this constitution.

## 6. WBS principle

The work breakdown structure is not a cosmetic task list. It must support: decomposition of scope, scheduling, milestone planning, ownership assignment, cost estimation, readiness and progress assessment.

Project plans without real WBS quality controls are non-compliant.

## 7. Profitability principle

Project delivery must be financially observable. Pulser must surface profitability signals at least at: project level, milestone or phase level where applicable, portfolio level. Profitability views must be grounded in transactional signals, not narrative-only judgments.

## 8. Evidence principle

All material project-finance outputs must retain linkage to source records and evidence in Odoo Documents. This includes: executive packs, client-facing status packs where retained, project health snapshots, budget/forecast/actual exports, billing-readiness outputs, margin and variance reports.

## 9. Channel principle

Pulser may be surfaced inside Microsoft 365 channels using the Microsoft 365 Agents Toolkit and related Microsoft Agents SDK scaffolding, but this is a channel/distribution layer, not the core product runtime.

Canonical rule:
- Pulser core runtime remains Pulser-owned and externally hosted
- Microsoft 365/Teams/Outlook/Word/Excel are channel surfaces
- toolkit scaffolding may be used for bot/app packaging, provisioning, and lifecycle automation
- no channel surface may bypass Pulser policy, RBAC, or evidence rules

## 10. Direct ingress principle

Canonical public and operator ingress for Pulser remains: Azure DNS, direct custom-domain binding to Azure Container Apps origins, certificate binding at the application edge. No Cloudflare and no proxy-based canonical ingress are assumed in this bundle.

## 11. RBAC principle

Project-to-Profit behavior must resolve from: surface, tenant, role group, approval band, evidence scope, expertise mode, task type, risk level. Contact lists, org charts, and email directories must not be treated as RBAC authority.

## 12. Approval principle

Pulser must separate: preparer authority, reviewer authority, threshold approver authority, final signoff authority, platform administration authority. Project profitability and billing-readiness assistance must never escalate into unauthorized approval behavior.

## 13. Safety principle

Pulser must not:
- auto-approve project financial commitments without policy
- publish client or executive packs without evidence linkage
- mark billing-ready when required prerequisites are missing
- suppress uncertainty when project profitability signals are incomplete
- infer authoritative contract or financial facts from weak retrieval alone

## 14. Verification principle

All material Project-to-Profit work must pass: Clarify gate before final planning when ambiguity remains, Verify gate before merge/release for production-impacting changes.

Verify must check: lifecycle alignment, constitutional compliance, Smart Success Criteria coverage, evidence linkage, rollout and rollback readiness where applicable.

## 15. Document-ingestion principle

Pulser Project to Profit may use Azure Document Intelligence as the document-ingestion and structuring layer for project and commercial evidence.

### 15.1 Allowed use
Use Document Intelligence for:
- contract extraction
- invoice extraction
- receipt extraction
- layout/read extraction of semi-structured project documents
- custom classification and extraction for project-specific document families

### 15.2 Product rule
Document Intelligence may extract and structure evidence, but it does not replace:
- Odoo transactional truth
- Pulser policy validation
- evidence review requirements
- approval or publish controls
