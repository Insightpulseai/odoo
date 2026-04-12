# Constitution — Pulser for Odoo

Pulser is a **custom-engine, multi-agent, policy-gated enterprise copilot** for Odoo-centered workflows. This document defines the engineering invariants and architectural constraints for the platform.

---

## 1. SaaS Multitenancy Principle (BOM 1)

Pulser is a B2B multitenant SaaS platform.
- **Tenant Definition**: A tenant is a customer organization.
- **Independence**: Pulser Tenant != Odoo Company != Microsoft Entra Tenant.
- **Isolation**: Tenant-internal structures (branches, projects, business units) must remain within the SaaS tenant boundary.

## 2. Business Process Authority (BOM 2)

Pulser must be architected around formal end-to-end business scenarios:
- **Primary**: Project to Profit (Sales, Resourcing, Finance) and Record to Report (Close, Audit).
- **Supporting**: Source to Pay (AP, Expense), Order to Cash (Billing, Collections), and Administer to Operate (Control Plane).
- **Benchmark**: Dynamics 365 Project Operations and **SAP Concur Expense/Accrual benchmarks** are the canonical operating model authorities.

## 3. Custom-Engine Architecture (BOM 3, 4)

Pulser is a **Custom-engine agent**.
- **Authority**: It does not rely on a host product’s built-in orchestration as the source of truth. It brings its own runtime, tools, policies, retrieval, and validators.
- **Orchestration**: Pulser is a **multi-agent orchestrated system** consisting of:
    - a **planner/router**
    - **specialist agents** (finance, project finance, research, ops)
    - **fallback / self-heal policies**
    - **tool calling, retrieval, and validators**
- **System of Action**: In Odoo, Pulser is a **transactional and operational copilot** that prepares, validates, routes, summarizes, and publishes.
- **Interaction**: Action pills are the primary interaction surface for focused finance personas. Chat completion is a secondary, augmenting capability for nuance.
- **Stateless Spokes**: Channel shells are stateless presentation layers and must not persist business state.

## 4. Channel Shell Adapters (BOM 5)

Pulser is delivered through specialized shells that adapt the Core authority to specific user contexts.
- **Web Shell (B2B)**: High-density Next.js dashboard for finance/ops professionals.
- **Enterprise Shell (M365)**: Integrated via **Microsoft Agents SDK** for Teams and Outlook.
- **Engineering Shell (DevOps)**: Integrated via **GitHub Copilot SDK** for IDE/CLI/Repo-aware operator tasks.
- **Identity Bridge**: All shells MUST use **Microsoft Entra ID (OIDC)** for auth handoff to the Core.

## 5. Control Plane Architecture (BOM 6, 7)

Pulser must maintain a productized separation between service operations and tenant administration.
- **Service Control Plane (SCP)**: Governs onboarding, lifecycle, stamp assignment, and the **Go-Live Factory** implementation states (Bootstrap -> Live Site).
- **Tenant Admin Plane (TMP)**: Governs tenant-specific settings, feature enablement, and **Activation Gate** visibility.

## 6. Deployment Stamp Invariant (BOM 8)

Pulser scales and isolates risks through deployment stamps.
- **Definition**: An independently deployable/recoverable slice of runtime and platform capacity.
- **Rollout Sequence**: Releases must be promoted through defined **Rollout Groups**:
    1. **Canary Stamp**: Internal test/internal-dev.
    2. **Early Adopter (EA) Stamp**: Selected beta tenants.
    3. **General Availability (GA) Stamps**: Production fleet.
- **Mechanism**: Every stamp-level update must use **ACA Revision Labels** and traffic splitting. Traffic must be shifted incrementally (e.g., 5% -> 25% -> 100%) with automated health-check validation at each step.

## 7. Delivery and Governance (BOM 10, 11, 15)

Pulser follows the Microsoft CAF (Cloud Adoption Framework) and rigorous ALM discipline.
- **Execution**: All production changes flow through policy-gated pipelines (Git + PR).
- **Security**: Lease privilege is a hard production gate. No unknown Owners or unexplained root-scope privileges are permitted.
- **Migration Authority**: All technical migrations must include a **Validation Log** (AR/AP/TB reconciliation) signed off by the tenant Finance Director before production activation.
- **Scenario Authority**: 100% sign-off on P1 user stories for the target Scenario UAT is a hard blocking gate for production activation.
- **Evidence-First**: Telemetry, logs, and audit trails are first-class product requirements.

## 8. Live-Site-First Operations (BOM 16)

Pulser must be operated as a "live site," not merely deployed software.
- **Culture**: Engineering owns production quality and reliability.
- **Strategy**: Shift-right for production-only validation (canaries, fault-injection).
- **Stabilization Invariant**: All new activations must complete the **Stabilization Window** and **First-Close Review** before being considered "Stable" (Steady State).

---

## 9. Finance Performance and Reliability Invariant (BOM 16)

Finance-operations applications must meet enterprise-grade reliability standards for high-volume execution.
- **Idempotency**: All critical finance flows (reconciliation, tax calculation, close-task creation) must support idempotent retries without duplicating data.
- **Async Execution**: Long-running reconciliations or batch processes must be executed asynchronously to prevent UI/API timeouts and ensure system stability.
- **Error Isolation**: Failure in one tenant or stamp's finance batch must not logically block the execution of other batches across the fleet.

---

---

## 10. Finance Authority and Action Scopes (BOM 15)

The agentic reasoning and action layer must be governed by a 5-layer Finance RBAC architecture:
1. **Business role** (e.g., Finance Head, AP Manager)
2. **Approval authority** (Bands A-E)
3. **Data/evidence visibility** (Evidence Scopes)
4. **Agent action permissions** (Action Scopes)
5. **UI Cockpit / Queue context** (Interaction Surface)

- **Action Invariant**: The agent must not execute actions (draft, approve, reconcile) beyond the user's assigned **Agent Action Scope**.
- **Evidence Invariant**: The agent's retrieval boundary is strictly enforced by the user's **Evidence Visibility Scope** (Self, Team, Entity, or Consolidated).
- **Approval Separation**: Use of **Approval Bands** (A-E) to separate preparation work from financial sign-off authority.
- **Role Authority**: Business roles must be assigned via **Microsoft Entra ID Role Groups**, not individual name mappings.

---

## 22. Umbrella-bundle principle

`spec/pulser-odoo/` is the umbrella platform bundle for Pulser for Odoo.

It governs:
- shared product rules
- shared architecture rules
- shared control-plane rules
- shared ingress/runtime rules
- shared RBAC and policy rules
- shared evidence and publishing rules
- shared live-site and self-improvement rules

It does not replace bounded child bundles for major business capabilities.

### 22.1 Required bounded child bundles

The primary business-capability bundles under this umbrella are:
- `spec/pulser-project-to-profit/`
- `spec/pulser-record-to-report/`

### 22.2 Scope split rule

Use:
- `pulser-project-to-profit` for the delivery/profitability spine
- `pulser-record-to-report` for the finance-control/close/reporting spine

The umbrella bundle remains the authority for cross-cutting rules that apply to both.

## 23. Cross-bundle consistency principle

All child bundles must inherit the umbrella bundle's cross-cutting rules for:
- Odoo as system of action
- Odoo Documents as retained evidence surface
- direct ACA ingress
- deployment-stamp model
- RBAC / approval-band separation
- policy-gated mutations
- publishable output and evidence linkage
- clarify / verify / CI validation gates
- self-improvement and self-healing safety

If a child bundle conflicts with the umbrella bundle on a cross-cutting rule, the umbrella bundle wins unless the umbrella is explicitly amended.

## 24. Channel-surface principle

Microsoft 365 surfaces are optional channel surfaces for both child bundles.

The **Microsoft 365 Copilot Extensibility** model (Declarative Agents, API Plugins, and Graph Connectors) is used to surface Pulser within Microsoft 365.

### 24.1 Declarative Agent strategy
Pulser uses **Declarative Agents** as tailored, packaged experiences for specific finance and project groups. Declarative Agents:
- define specialized instructions for the channel
- expose canonical Pulser actions as **API Plugins**
- link to Odoo grounding data via **Graph Connectors** where required

### 24.2 Custom Engine vs Extension model
Pulser (Azure AI Foundry + Odoo) remains the **Authoritative Custom Engine**.

Channel extensions (e.g., Teams Declarative Agents) serve as and **Surfaces/Channels** only:
- they consume canonical Pulser APIs
- they do not replace Pulser’s reasoning, orchestration, policy, or transactional authority
- no channel surface may bypass RBAC, evidence scope, approval bands, or mutation safety

---

*Last updated: 2026-04-12*
