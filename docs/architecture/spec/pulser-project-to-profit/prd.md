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

# PRD — Pulser Project to Profit

## 1. Executive summary

Pulser Project to Profit implements a governed delivery-profitability operating model on Odoo.

> Pulser P2P is not only a technical platform; it is a services-led ERP and project-operations transformation offer, supported by benchmark environments, partner-ready packaging, and eligible channel/benefit economics where available.

It turns Odoo into a system where:
- commercial handoff becomes structured project setup
- WBS and milestone plans become execution truth
- time, expense, vendor cost, and billing signals stay connected
- project managers, controllers, and finance heads work from shared project-finance state
- profitability and readiness are continuously measurable
- publishable project-finance outputs are evidence-linked and policy-safe

This bundle uses the Dynamics 365 Project Operations operating model as the benchmark for how sales, resourcing, project management, and finance should connect, but implements that behavior in an Odoo-first, Pulser-governed architecture.

## 2. Problem statement

Typical ERP and project setups fail at Project-to-Profit in five ways:
1. Commercial and delivery handoff is weak.
2. WBS exists as a task list, not a financial planning/control object.
3. Forecast, budget, and actuals drift apart across spreadsheets and messages.
4. Billing readiness is discovered late.
5. Executives and finance get fragmented visibility into margin risk.

This bundle enters a and **$20T project economy** where **88M people** are expected to work in project management by 2027. Service-centric organizations require a and **services-led ERP transformation** that Odoo on Azure + Pulser is uniquely positioned to deliver as a D365 displacement play.

Pulser must solve these problems by making project delivery financially governable and evidence-backed.

## 3. Product goal

Implement a bounded Project-to-Profit capability on top of Odoo that supports:
- structured commercial-to-project initiation
- governed project planning
- delivery execution tracking
- project-finance visibility
- billing readiness
- profitability analysis
- executive and finance reporting

## 4. Non-goals

This bundle does not attempt to:
- replace Odoo with a separate PM database
- implement all Microsoft Project Operations product surfaces literally
- become the full Record-to-Report control layer
- own GL, tax, or close as primary domains
- bypass finance approval or accounting truth

Those concerns belong in the umbrella Pulser bundle and the Record-to-Report bundle.

## 5. Primary users

### 5.1 Sales / account lead
Needs: quote and scope handoff, pricing/billing assumptions retained, contract and delivery-start readiness.

### 5.2 Project manager
Needs: WBS and milestone management, risk/blocker/slippage visibility, execution summaries, delivery-status publishing.

### 5.3 Project finance controller
Needs: forecast vs budget vs actual visibility, cost and margin variance, billing readiness, portfolio comparison.

### 5.4 Finance controller / finance head
Needs: project profitability visibility, delivery-finance linkage, accrual candidates, executive portfolio summaries.

## 6. Lifecycle and scope

### 6.1 Initiate
Pulser must support: quote/proposal handoff, project shell creation, project contract setup, WBS and milestone definition, forecast baseline, budget baseline, billing model setup, initial evidence pack.

### 6.2 Execute
Pulser must support: task and milestone execution status, dependency and blocker visibility, resource and owner assignment visibility, time capture completeness, expense capture completeness, vendor/third-party cost linkage, change signal capture, billing-readiness signal generation.

### 6.3 Analyze
Pulser must support: forecast vs actual, budget vs actual, cost variance, revenue and billing readiness, margin and profitability views, portfolio risk summaries, finance and executive reporting packs.

## 7. Core objects

The minimum domain contract for this bundle is:
- `project`
- `project_contract`
- `project_quote_handoff`
- `work_package`
- `task`
- `milestone`
- `resource_assignment`
- `time_entry`
- `expense_entry`
- `vendor_cost`
- `forecast`
- `budget`
- `actual`
- `billing_event`
- `billing_readiness_signal`
- `project_health_snapshot`
- `evidence_document`

These may map to multiple Odoo/OCA/local models, but the contract must exist.

## 8. Functional requirements

### FR-1 Commercial handoff
Pulser must transform quote/proposal information into a governed project shell with: client, scope summary, billing model, contract references, margin assumptions, evidence linkage.

### FR-2 Project contract support
Pulser must support project contract state sufficient for: project launch gating, billing model determination, readiness review, later billing and collections handoff.

### FR-3 WBS support
Pulser must support hierarchical WBS structures that include: parent/child work items, milestone relationships, owner assignment, optional dependency awareness, estimated effort/cost signals.

### FR-4 Baseline setup
Pulser must support a starting forecast and a starting budget, with explicit separation between the two.

### FR-5 Execution signals
Pulser must continuously derive execution signals from: task state, milestone state, timesheet completeness, expense completeness, vendor cost presence, blocked work, change activity.

### FR-6 Billing readiness
Pulser must compute billing-readiness signals from: contract/billing model, milestone or deliverable status, supporting evidence completeness, cost and delivery completeness where required.

### FR-7 Profitability analysis
Pulser must compute profitability views using: forecast, budget, actuals, billing/revenue signals where available.

### FR-8 Portfolio summaries
Pulser must provide project portfolio visibility for controllers and finance heads, including: margin at risk, forecast drift, milestone slippage, billing readiness, project health.

### FR-9 Publishable outputs
Pulser must generate publishable project-finance outputs in: XLSX, DOCX, PPTX.

### FR-10 Evidence linkage
All material project-finance outputs must retain evidence linkage to source records or Odoo Documents artifacts.

### FR-11 Partner operations integration
The product must support P2P-specific partner-operations integrations with Partner Center workspaces where relevant for:
- referral management (deal handoff)
- project-led incentives and earnings tracking
- services-offering publication in the Microsoft Commercial Marketplace
- customer subscription readiness for D365 Project Operations displacement motions

## 9. UX requirements

### 9.1 Default surfaces
- Project Setup Workbench
- Delivery Cockpit
- Project Finance Cockpit
- Portfolio / Executive Cockpit

### 9.2 Interaction model
- cockpit-first for project/finance roles
- action pills for high-confidence next steps
- chat as drill-down reasoning, not the default workflow surface
- evidence and assumptions visible before material publish or approval actions

### 9.3 Expertise modes
- beginner = guided setup and more helper text
- intermediate = grouped steps and moderate density
- expert = compact surfaces and lower explanation density

Expertise mode affects presentation, not permissions.

## 10. Channel and distribution requirements

Pulser Project to Profit may be surfaced through: Odoo native UI, Pulser web/control surfaces, Microsoft 365 channels using Microsoft 365 Agents Toolkit packaging/scaffolding where justified.

Channel surfaces must remain subordinate to Pulser policy, evidence, and mutation controls.

### 10.1 Partner and Benchmark Foundation
The P2P bundle must:
- support a services-led project-operations go-to-market motion
- maintain competitor/benchmark validation against Microsoft and **D365 Project Operations partner sandbox** environments
- support workshop-led discovery and envisioning motions for project scenarios
- define how partner benefits, credits, and incentives can reduce pre-sales and demo costs
- define a partner-operations model for project-operations deals using Partner Center as the default system for referrals, incentives, and Marketplace offers
- prefer Partner Center APIs and native workflows over custom P2P-specific partner-ops backoffice tooling

### 10.2 Partner operations doctrine (P2P)
For Microsoft-partner execution, Pulser P2P will adapt around **Partner Center** as the native partner-operations system for referral management, incentive tracking, and project-services marketplace publishing, using thin integrations instead of duplicative custom backoffice tooling.

## 11. Security and policy requirements

- RBAC must be role-group-based
- approval bands must remain separate from role groups
- evidence visibility must be scoped
- no unauthorized project or billing approvals
- no publish action without evidence-linked source state
- no hidden fallback mutation after failed validation

## 12. Integration requirements

This bundle must integrate with: Odoo project/task structures, timesheets, expenses, billing/invoicing objects, analytics/financial dimensions where used, Odoo Documents, Pulser policy engine, Pulser export/publishing services, optional Teams/M365 channel surfaces where justified.

## 13. Risks

- WBS implemented as cosmetic hierarchy instead of a control surface
- forecast and budget collapsed into one object
- billing readiness inferred without evidence
- profitability surfaced without actual cost completeness
- portfolio view loses traceability to project-level records
- channel surfaces diverge from canonical policy behavior

## 14. Clarify gate checklist

This bundle must be clarified before planning if any of the following are unresolved:
- billing model variants
- contract state model
- margin signal formula
- forecast vs budget ownership
- milestone completion semantics
- evidence requirements for billing-ready status
- acceptable portfolio rollup rules

## 15. Smart Success Criteria

- **SC-PTP-01 Lifecycle completeness:** 100% of scoped project flows map to Initiate / Execute / Analyze
- **SC-PTP-02 WBS coverage:** at least 90% of pilot projects use WBS + milestones + owner assignment
- **SC-PTP-03 Forecast visibility:** at least 90% of pilot projects expose forecast vs actual
- **SC-PTP-04 Budget control:** at least 90% of financially controlled projects expose budget vs actual
- **SC-PTP-05 Billing-readiness quality:** at least 90% of pilot billing-ready flags have required evidence and prerequisite signals
- **SC-PTP-06 Profitability visibility:** at least 90% of pilot projects expose margin/profitability view
- **SC-PTP-07 Portfolio observability:** 100% of portfolio cockpit projects expose current health snapshot
- **SC-PTP-08 Evidence linkage:** 100% of project-finance outputs retain evidence linkage
- **SC-PTP-09 Publishable outputs:** 100% of scoped executive/project-finance reports can generate native XLSX, DOCX, and PPTX
- **SC-PTP-10 Mutation safety:** 100% of project-finance mutations remain within RBAC and approval-band policy
- **SC-PTP-11 Benchmark authority:** 100% of P2P specialists verified against D365 Project Operations sandbox benchmarks
- **SC-PTP-12 Services ratio:** track and maintain target services-to-software revenue ratio for transformation engagements
- **SC-PTP-13 Envisioning conversion:** track conversion rate from envisioning/discovery to implementation
- **SC-PTP-14 Partner-ops compliance:** 100% of project-led referrals and incentives managed via Partner Center native workflows/APIs

## 16. Specialist Execution Engines (BOM-03)

The Project to Profit bundle governs the following specialized agentic execution engines:

### 16.1 PPM Clarity Engine (PM-01) — Phase 1/2
- **Phase 1**: Portfolio/Program structure using Odoo CE + OCA.
- **Phase 2 Scale**: Budget vs. Actual variance, Cost-center tracking, Portfolio health computation.
- **Phase 3 Strategic**: Investment scoring, Risk/Issue registers, Phase-gate automated reviews.

### 16.2 WBS Studio (PM-02) — Phase 1
- **Hierarchical Control**: Level 0 (Project) → Level 1 (Work Package) → Level 2 (Task) → Level 3 (Subtask).
- **Quality Gates**: Score-based billing-readiness (Owners + Estimates + Deadlines + Baselines).
- **Rule**: Score < 60 blocks billing-readiness until remediated.

## 17. Document-ingestion principle (Refined)
Pulser P2P uses Azure Document Intelligence as the authoritative ingestion layer for delivery evidence.
- **Prebuilt Models**: `prebuilt-contract`, `prebuilt-invoice`, `prebuilt-receipt`.
- **Custom Mapping**: Use custom classifiers for Statements of Work (SOW), Project Briefs, and Milestone Signoffs.
- **Rule**: Document Intelligence is an extraction layer only; Pulser remains the delivery/readiness authority.
