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
- **Source to Pay**: Spend control, AP, expense/liquidation, **Accrual Visibility**, **Card Hygiene**, and BIR readiness.
- **Order to Cash**: Billing, collections, and revenue linkage.
- **Administer to Operate**: Control plane ops, onboarding (SCP/TMP), and IAM governance.

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

Pulser follows a "One Core, Three Shells" Hub-and-Spoke architecture:
- **Web Shell (Professional)**: The primary IPAI/Next.js dashboard for high-density finance and project administration.
- **Enterprise Shell (Productivity)**: Optimized via the **Microsoft Agents SDK** for native integration into Teams, Outlook, and M365 Copilot.
- **Engineering Shell (Ops)**: Optimized via the **GitHub Copilot SDK** for IDE, CLI, and repo-aware operator commands.
- **Authority**: No delivery shell may replace or bypass the Pulser Core authority or the SaaS control plane.
- **Identity Bridge**: All shells must use **Microsoft Entra ID (OIDC)** for authentication handoff to the Core.

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

### 9.1 Phase Model
- **Activation Lifecycle**: 4-Phase progression: **Bootstrap** (Goals) -> **Ingestion** (Technical) -> **Validation** (UAT/Balance) -> **Live Site** (Cutover).
- **Mandatory Gates**: Hard gating of production activation on **Security**, **Data Integrity** (AR/AP/TB reconciliation), and **Scenario UAT** (100% sign-off on P1 stories).

### 9.2 Factory Operations
- **Migration Scope**: Structured migration of Master, Open Transactional (sub-ledger granular), and 24-months of Historical TB data.
- **Factory Dashboard**: The TMP must provide a "Tenant Implementation Dashboard" for tracking readiness against the 4-phase lifecycle and cutover checkpoints.
- **Stabilization Gate**: Mandatory 30-day Hypercare window (Day 1-5 daily LSR) and **First-Close Review** before steady-state handoff.
- **Metrics**: Track metrics for **Checklist Compliance**, **Time-to-Activation**, and **First-Close Variance**.

---

## 39. SaaS Tenancy Configuration
- **Isolation**: Tenant = Organization.
- **Identity**: Entra ID OIDC is the mandatory bridge.
- **Branding**: Tenant-specific themes and logos in the Professional Shell.

## 40. Service Control Plane (SCP)
- **Authority**: The SCP governs the whole fleet.
- **Function**: Tenant provisioning, stamp allocation, and global health monitoring.

## 41. Deployment Stamps
- **Unit of Scale**: An independent set of ACA + PostgreSQL + Redis.
- **Independence**: Failure in Stamp A must not impact Stamp B.
- **Scale-out**: New stamps are added to accommodate fleet growth.

## 42. Safe Rollout & Staged Promotion
- **Authority**: Release Orchestrator logic.
- **Sequence**: Canary -> EA -> GA.
- **Verification**: Health-check-gated traffic shifting at the stamp level.

## 43. Live-Site Operations Strategy
- **Culture**: No silos between dev and ops.
- **Alerting**: Actionable, high-signal alerts mapped to BOM layers.

## 44. Pulser Agent-Platform Reference
- **Core**: Foundry-native agents grounded in Odoo Documents.
- **MCP**: Mandatory for all external tool integrations.

---

## 10. Reporting and Intelligence (BOM 14)

### 10.1 Reporting Benchmarks
- **Standards**: SAP Concur-grade analytics for **Accruals** (outstanding liabilities), **Card Hygiene** (unassigned/unsubmitted), and reconciliation.
- **Outputs**: Project profitability dashboards and automated Management/Board reporting packs.

### 10.2 Finance Operating Surface (MB-500)
Pulser must deliver role-based **Cockpits** rather than a generic chat experience:
- **Finance Head**: Close Cockpit, BIR Compliance Cockpit, and Exec Brief.
- **Finance Manager**: Reconciliation Cockpit and Close Task Management.
- **AP/Expense/Treasury**: High-density work queues (AP Queue, Exceptions Cockpit).
- **Tax Lead**: BIR Compliance Cockpit and Rule-based Exception cards.
- **Auditor**: Read-only Evidence Vault views.

### 10.3 Close Pack KPIs
Standard Month-End and Quarter-End close packs must include:
- **Trial Balance Integrity**: Variance analysis vs previous period and budget.
- **Accrual Aging**: Visibility into outstanding liabilities by transaction date.
- **Payout Integrity**: Reconciliation of Odoo processed items vs Bank/Payment gateway status.

### 10.4 Integration Capability Matrix
Pulser must support a multi-layer integration model:
- **Data (ODATA v4)**: Primary path for Power BI and **Excel Studio** (Bulk reconciliation, Trial Balance sync).
- **Event (Service Bus)**: Asynchronous handling of business events (e.g., invoice posted, project completed).
- **Productivity (Office Shell)**: **Outlook Studio** sidebar (AR collections, customer context) and **Word/PPTX Studio** (Report assembly).
- **Reasoning (Foundry)**: RAG-based grounding on Odoo documents and finance metadata.

## 11. Security and Governance (BOM 15)
- **Identity Architecture**: Mandatory use of the **5-layer Finance RBAC Model** (Role -> Band -> Evidence -> Action -> UI).
- **Persona Management**: Roles must be assigned via **Microsoft Entra ID Role Groups**.
- **Approval Logic**: Separation of preparation work from approval authority via **Approval Bands A-E**.
- **Action Guard**: Hard enforcement of **Agent Action Scopes** (Summarize, Draft, Reconcile, Approve, etc.).
- **Least Privilege**: Zero unknown principals with Owner or root-scope access.

## 46. Umbrella and child-bundle topology

`spec/pulser-odoo/` is the umbrella platform bundle for Pulser for Odoo.

This bundle governs cross-cutting platform behavior and delegates primary business-operating-model detail to two bounded child bundles:

- `spec/pulser-project-to-profit/`
- `spec/pulser-record-to-report/`

### 46.1 Child-bundle responsibilities

#### `pulser-project-to-profit`
Owns:
- project / delivery / profitability lifecycle
- quote / contract / WBS / execution / billing-readiness / margin visibility
- the Project Operations-inspired operating model

#### `pulser-record-to-report`
Owns:
- finance control / reconciliation / close / reporting / tax-support lifecycle
- GL / AP / AR / budgeting / cash-bank / reporting / compliance support
- the Finance-inspired operating model

### 46.2 Umbrella responsibilities
The umbrella bundle owns:
- platform/runtime topology
- control plane and tenant admin
- deployment stamps
- direct ingress architecture
- behavior engine
- retrieval/foundry architecture
- RBAC and policy model
- export/publishing model
- live-site operations
- self-improvement architecture

## 47. Cross-bundle dependency model

The child bundles are complementary, not competing.

### 47.1 Project-to-Profit -> Record-to-Report handoff
The Project-to-Profit bundle must emit finance-consumable signals into the Record-to-Report bundle, including:
- billing-readiness signals
- forecast / budget / actual signals
- project health and margin signals
- accrual-relevant signals
- evidence-linked project-finance artifacts

### 47.2 Record-to-Report <- Project-to-Profit dependency
The Record-to-Report bundle must consume project-finance signals where relevant for:
- accrual review
- close readiness
- executive reporting
- reconciliation and blocker analysis

### 47.3 Product rule
Neither child bundle may redefine cross-cutting platform policy independently.

## 48. Microsoft 365 surface strategy

Pulser may be surfaced through Microsoft 365 channels for both child bundles where it improves user adoption and workflow fit.

### 48.1 Valid use cases
- Teams surface for finance and project users
- Outlook-adjacent workflow assist where appropriate
- Word / Excel-adjacent publishing or review flows
- enterprise chat entry points for authorized users

### 48.2 Architectural rule
Microsoft 365 Agents Toolkit is an optional surface/tooling layer only.
It may accelerate packaging, app/bot setup, and deployment scaffolding, but it is not the authoritative runtime, policy engine, or business logic layer.

### 48.3 Safety rule
Channel surfaces must remain subordinate to:
- Pulser behavior resolution
- Pulser RBAC and approval bands
- evidence scope
- mutation safety
- Odoo transactional truth

## 49. Smart success criteria additions

- SC-PH-46 Bundle alignment:
  100% of child bundles remain consistent with umbrella cross-cutting rules

- SC-PH-47 Cross-bundle handoff:
  100% of required project-finance signals needed by Record-to-Report are defined and consumable

- SC-PH-48 Channel-surface safety:
  100% of Microsoft 365 channel actions remain policy-gated and evidence-scoped

- SC-PH-49 Platform authority clarity:
  100% of runtime, policy, and mutation authority remains in Pulser/Odoo rather than channel scaffolding

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
| SC-PH-35 | Role clarity | finance users mapped to canonical Pulser role groups | 100% |
| SC-PH-36 | Approval separation | preparer vs reviewer vs approver vs final signoff separation enforced | 100% |
| SC-PH-37 | Evidence least privilege | finance roles limited to required evidence scope | 100% |
| SC-PH-38 | Agent least privilege | agent action scopes aligned to user role and approval band | 100% |
| SC-PH-39 | Audit immutability | audit-viewer role has no transact/edit/approve capability | 100% |

---

---

## 61. Normalized Bill of Materials (BOM)

| ID | Layer | Canonical Component |
|----|-------|--------------------|
| BOM-01 | Surface and Tenancy | insightpulseai.com (Brand), erp.insightpulseai.com (Action), Tenant = Organization |
| BOM-02 | Business Process | Project to Profit, Record to Report, Source to Pay, Order to Cash, Administer to Operate |
| BOM-03 | ERP Core | Odoo CE 18 + OCA, ipai_* thin bridges |
| BOM-04 | Reasoning Plane | Azure AI Foundry, Azure AI Search, Odoo Documents (retained evidence) |
| BOM-05 | Channel Shells | Professional Web, Enterprise M365 (SDK), Engineering DevOps (SDK) |
| BOM-06 | Service Control Plane | Fleet-wide onboarding, lifecycle, and stamp assignment (SCP) |
| BOM-07 | Tenant Admin Plane | Tenant-specific config, features, and implementations (TMP) |
| BOM-08 | Deployment Stamps | Regional/Scale-unit isolation slices (ACA + PG + Redis) |
| BOM-09 | Infrastructure | Azure Global (Front Door, Key Vault) + Regional (ACA, PG Flex) |
| BOM-10 | Delivery Model | Git + PR + Policy-gated Pipelines (Azure Pipelines / GHA) |
| BOM-11 | Container Authority | ACR per-stamp or shared, Immutable images |
| BOM-12 | Implementation Factory | 4-Phase Activation (Bootstrap, Ingestion, Validation, Live Site) |
| BOM-13 | Governance Gates | Security, Reconciliation (AR/AP/TB), Scenario UAT P1 |
| BOM-14 | Intelligence Plane | SAP Concur-grade Analytics (Accruals, Card Hygiene, Exception Cards) |
| BOM-15 | RBAC Model | 5-Layer Security (Role, Band, Evidence, Action, UI) |
| BOM-16 | Live-Site Model | Actionable Telemetry, Canary Promotion, Stabilization Review |

---

## 63. Finance RBAC model

Pulser finance access must be modeled through:
- **Business role** (e.g., Finance Head)
- **Approval bands** (A-E)
- **Evidence scopes** (Self, Team, Entity, Consolidated)
- **Agent action scopes** (Draft, Summarize, Reconcile, Approve)
- **UI Cockpit / Queue context** (Interaction Surface)

### 63.1 Canonical finance role groups
- pulser_finance_head (Cockpit: Finance Dashboard, BIR Compliance)
- pulser_finance_controller (Cockpit: Close Management, Reconciliation)
- pulser_ap_manager (Cockpit: AP Queue, Exceptions)
- pulser_ap_processor (Cockpit: AP Entry)
- pulser_tax_lead (Cockpit: BIR Compliance, Exception Cards)
- pulser_treasury_manager (Cockpit: Cash Flow, Bank Rec)
- pulser_billing_collections (Cockpit: AR Queue, Collections)
- pulser_project_finance_controller (Cockpit: Project Profitability)
- pulser_expense_reviewer (Cockpit: Expense Queue)
- pulser_exec_viewer (Cockpit: Exec Brief)
- pulser_audit_viewer (Cockpit: Read-only Evidence)
- pulser_finance_platform_admin (Cockpit: Service Monitoring)

### 63.2 Product rule
Identity directory records and contact lists must not be treated as RBAC authority.
RBAC authority must come from explicit role-group membership and approval/evidence/action policies.
Assign roles by **role group (Entra ID)**, not by individual name/email.

### 63.3 Approval model
Pulser must separate:
- preparer authority
- reviewer authority
- threshold approver authority
- final signoff authority
- platform administration authority

---

*Last updated: 2026-04-11*
