# Product Requirements Document — Pulser for Odoo

Pulser for PH is the primary agentic ERP workspace built on Odoo CE 18 and Azure AI. This PRD defines the requirements for a professional, enterprise-grade B2B SaaS platform.

---

## 1. Surface and Tenancy (BOM 1)
- **Tenancy Model**: Pulser Tenant represents a Customer Organization.
- **Boundaries**: Pulser Tenant != Odoo Company != Entra Tenant.
- **Surfaces**: 
    - `insightpulseai.com` (Public Brand)
    - `erp.insightpulseai.com` (Authenticated ERP Runtime)
    - `w9studio.net` (Separate Brand Surface)

## 2. Business Process Requirements (BOM 2)
Pulser must execute formal end-to-end business scenarios:
- **Project to Profit**: Sales/Deal context, WBS, Resourcing, Profitability, and OKRs.
- **Record to Report**: Finance close, reconciliation, audit trails, and retained evidence.
- **Source to Pay**: Spend control, AP, expense/liquidation, and BIR readiness.
- **Order to Cash**: Billing, collections, and revenue linkage.
- **Administer to Operate**: Control plane ops, onboarding, and IAM governance.

## 3. Odoo / ERP Integration (BOM 3)
- **Baseline**: Odoo 18 CE + Curated OCA stack.
- **Bridges**: Thin `ipai_*` modules for Finance PPM, Copilot shells, and evidence vaulting.
- **Cutover Controls**: Mandatory AR/AP clearing, trial-balance validation, and bank-reconciliation handling for production activation.

## 4. Agent and Runtime Plane (BOM 4)
- **Reasoning**: Azure AI Foundry / OpenAI.
- **Grounding**: Azure AI Search linked to Odoo Documents.
- **Specialists**: Agents for AP, Expense, PH Tax (BIR), Close, and Reporting.
- **Publishing**: Native generation of PPTX, DOCX, and XLSX artifacts.

## 5. Channel Shell Strategy (BOM 5)
- **Enterprise Reach**: Microsoft Agents SDK (M365/Teams/Webchat).
- **Internal Ops**: GitHub Copilot SDK (Developer/DevOps assistants).
- **Auth**: Secondary shells must not replace Entra ID/Managed Identity as the primary auth path.

## 6. Control and Admin Planes (BOM 6, 7)
- **Service-Level Plane**: Governs tenant onboarding (wizard/milestones), stamp assignment, and release targeting.
- **Tenant-Level Plane**: Governs tenant settings, feature flags, and integration configuration.

## 7. Deployment Stamps and Scale (BOM 8)
- **Unit**: Independently deployable slices of capacity.
- **Staging**: Releases promoted stamp-by-stamp via ACA revisions and label-based routing.

## 8. Infrastructure and Delivery (BOM 9, 10, 11)
- **Stack**: Azure Container Apps (ACA), Postgres Flexible Server, Key Vault, and Entra ID.
- **ALM**: PR-only merges, protected branches, and policy-gated pipelines across `.github`, `odoo`, `agent-platform`, `infra`, and `docs`.

## 9. Implementation and Go-Live Factory (BOM 12, 13)
- **Workflow**: Guided onboarding -> Data Migration/Validation -> UAT -> Activation Gate -> Stabilization.
- **Gating**: Production activation requires completion of onboarding, migration, and security checklists.

## 10. Reporting and Intelligence (BOM 14)
- **Benchmarks**: SAP Concur-grade analytics for accruals, card hygiene, and reconciliation.
- **Outputs**: Project profitability dashboards and automated Management/Board reporting packs.

## 11. Security and Governance (BOM 15)
- **Identity**: Least privilege at root scope and subscription scope.
- **Agent Governance**: Sponsors required for all production agent identities.

## 12. Live-Site Operations (BOM 16)
- **Posture**: Actionable telemetry, shift-right validation, and emergency hotfix lanes.

---

## 13. Normalized Success Criteria (SMART)

| ID | Objective | Metric | Target |
|----|-----------|--------|--------|
| SC-PH-01 | Scenario coverage | Major Pulser capabilities mapped to at least one E2E scenario | 100% |
| SC-PH-02 | Project-to-profit completeness | Scoped Finance PPM capabilities mapped to Project to profit | ≥ 90% |
| SC-PH-03 | Record-to-report completeness | Scoped close/reporting capabilities mapped to Record to report | ≥ 90% |
| SC-PH-04 | Source-to-pay coverage | Scoped AP/expense/cash-advance workflows mapped to Source to pay | 100% |
| SC-PH-05 | Tenant terminology clarity | Product/docs distinguish Pulser tenant, Odoo company, and Entra tenant | 100% |
| SC-PH-06 | Control-plane coverage | Onboarding, lifecycle, config, rollout, health ops in control plane | 100% |
| SC-PH-07 | Stamp readiness | Deployment-stamp-capable environments defined before GA | At least 2 |
| SC-PH-08 | Progressive rollout safety | Finance-critical releases supporting canary/staged promotion | 100% |
| SC-PH-09 | PR discipline | Scoped repos with protected branches and PR-required merge flow | 100% |
| SC-PH-10 | Pipeline discipline | Staging/production environment changes executed through pipelines | 100% |
| SC-PH-11 | Container delivery | Scoped runtime services built and published as container images | 100% |
| SC-PH-12 | Least-privilege hygiene | Unknown principals with Owner access | 0 |
| SC-PH-13 | Root governance | Unexplained standing root-scope privileged assignments | 0 |
| SC-PH-14 | Privileged access discipline | Admin paths using eligible or time-bound activation (PIM) | ≥ 90% |
| SC-PH-15 | Agent governance | Production agent identities with accountable sponsor/owner defined | 100% |
| SC-PH-16 | Onboarding completeness | Production tenants completing required onboarding before activation | 100% |
| SC-PH-17 | Implementation governance | Active tenants with defined goals, scope, and readiness state | 100% |
| SC-PH-18 | Migration completeness | Production tenants completing migration validation before activation | 100% |
| SC-PH-19 | UAT completion | Scoped critical workflows passing UAT before activation | 100% |
| SC-PH-20 | Cutover completeness | Required cutover checklist items completed for each activation | 100% |
| SC-PH-21 | Balance validation | AR/AP/trial-balance reconciliation checks before activation | 100% |
| SC-PH-22 | Stabilization readiness | Production go-lives entering a defined stabilization window | 100% |
| SC-PH-23 | Profitability visibility | Pilot projects exposing budget, forecast, and actual margin views | ≥ 90% |
| SC-PH-24 | Project-finance linkage | Project workflows producing finance-consumable budget/actual signals | ≥ 90% |
| SC-PH-25 | Expense accrual coverage | Scoped unpaid employee-spend liabilities visible in accrual views | 100% |
| SC-PH-26 | Card exception coverage | Unassigned or unsubmitted card transactions visible in views | 100% |
| SC-PH-27 | Reconciliation control | Scoped extracted-vs-unpaid items visible in reconciliation dashboards | ≥ 90% |
| SC-PH-28 | Approval transparency | Scoped approver-role and limit structures queryable | 100% |
| SC-PH-29 | Evidence-linked artifacts | Publishable artifacts retaining evidence linkage before release | 100% |
| SC-PH-30 | Publishable outputs | Critical finance workflows generating native PPTX, DOCX, XLSX | 100% |
| SC-PH-31 | Grounded-answer quality | Pulser answers on retained evidence returning citation/linkage | ≥ 95% |
| SC-PH-32 | Live-site telemetry | Production runtime components emitting logs, traces, and alerts | 100% |
| SC-PH-33 | ACA safe release | ACA-hosted services supporting revision/traffic-based patterns | 100% |
| SC-PH-34 | First-close readiness | Newly activated tenants completing first-close review in stabilization | 100% |

---

*Last updated: 2026-04-11*
