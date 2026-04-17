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

# Tasks — Pulser Project to Profit

## Roadmap Phase 1 — Seed (Foundation & Initiate)
## Phase 1 — Domain and object contract
- [x] Define `project` shell contract and required fields (via `module_install_manifest.yaml`)
- [ ] Define `project_contract` model or mapping contract
- [ ] Define `project_quote_handoff` contract
- [/] Define `work_package`, `task`, and `milestone` hierarchy contract (WBS hydrated)
- [ ] Define `resource_assignment` visibility contract
- [ ] Define `evidence_document` linkage contract

## Phase 2 — Initiate lifecycle
- [ ] Implement commercial handoff to project setup workflow
- [ ] Implement contract and billing-model capture
- [ ] Implement WBS setup guidance and validation
- [ ] Implement forecast baseline capture
- [ ] Implement budget baseline capture
- [ ] Implement project setup evidence pack

## Phase 3 — Execute lifecycle
- [ ] Implement execution-state aggregation from tasks and milestones
- [ ] Implement timesheet completeness signals
- [ ] Implement expense completeness signals
- [ ] Implement vendor-cost linkage signals
- [ ] Implement blocker and change-signal capture
- [ ] Implement delivery cockpit summary surfaces

## Roadmap Phase 2 — Scale (Operational Automation)
## Phase 4 — Billing readiness
- [ ] Define billing-readiness rules by contract/billing model
- [ ] Implement milestone/deliverable readiness checks
- [ ] Implement evidence-completeness checks for billing readiness
- [ ] Implement billing-ready signal publication

## Phase 5 — Analyze lifecycle
- [ ] Implement forecast vs actual model
- [ ] Implement budget vs actual model
- [ ] Implement cost variance model
- [ ] Implement margin/profitability model
- [ ] Implement project health snapshot model
- [ ] Implement portfolio rollup model

## Phase 6 — UX and role surfaces
- [ ] Implement Project Setup Workbench
- [ ] Implement Delivery Cockpit
- [ ] Implement Project Finance Cockpit
- [ ] Implement Portfolio / Executive Cockpit
- [ ] Implement evidence-first publish and action flows
- [ ] Keep chat as drill-down, not default workflow

## Phase 7 — Publishing and artifacts
- [ ] Implement XLSX project-finance output
- [ ] Implement DOCX project summary output
- [ ] Implement PPTX executive portfolio output
- [ ] Preserve evidence linkage in all exports

## Phase 8 — Policy and verification
- [ ] Map project roles to Pulser role groups and approval bands
- [ ] Enforce evidence visibility scopes
- [ ] Add Clarify gate checklist for unresolved project-finance ambiguity
- [ ] Add Verify gate checklist for PRD/constitution alignment
- [ ] Record Smart Success Criteria pass/fail disposition
- [ ] Implement Signal Contract validation for project-to-finance handoffs

## Phase 9 — Document Intelligence for Project-to-Profit

- [x] Define normalized document schema for project/commercial ingestion
- [x] Map `prebuilt-contract` outputs into contract and billing assumptions
- [x] Map `prebuilt-invoice` outputs into project cost and billing-support signals
- [x] Map `prebuilt-receipt` outputs into expense-support signals
- [x] Map `prebuilt-layout` / `prebuilt-read` outputs into semi-structured project evidence handling
- [x] Define custom classifier for project-specific document families
- [x] Define custom extraction targets for SOW, project brief, milestone signoff, and change-request documents
- [x] Persist extracted outputs with evidence linkage into Odoo Documents
- [x] Add review/validation step before project-finance signals become actionable
 
 ## Roadmap Phase 3 — Mature (Agentic Governance)
## Phase 10 — Practice Hardening (Bid-to-Billing)
 - [ ] Configure internal IPAI tenant with P2P WBS and Milestone standards
 - [ ] Implement Internal Profitability Dashboard (Margin vs Budget)
 - [ ] Verify Bid-to-Billing lifecycle for first internal project
 - [ ] Formalize 'Project to Profit' as a repeatable practice delivery model

## Phase 11 — M365 Specialist Activation
 - [x] Functional [Copilot Gateway](../../agents/copilot_gateway.py) (SDK v2)
 - [x] Specialist Specialist Routing (PFP, FCP, BTP, AEP, TMP, OSP)
 - [x] Hardened [Skills Registry](../../docs/architecture/SKILLS_REGISTRY.md)
 - [x] Bicep Infrastructure Hardening (Bot Proxy & Gateway)
 - [x] Deployment Workflow Secret Injection
