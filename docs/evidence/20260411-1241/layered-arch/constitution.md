# Constitution: Pulser for Odoo

> **Canonical Slug**: `pulser-odoo`
> **Human-facing title**: `Pulser for Odoo`
> **Subtitle**: `Pulser Assistant for Odoo`
> **Product**: Thin Odoo adapter layer for the Pulser Assistant platform.

---

## 1. Governing Principles

### 1.1 Odoo is an Adapter, Not an Authority
All transactional data remains in Odoo. The `pulser-odoo` layer provides context (Tier 6) and execution benchmarks (Tier 5), but does not determine policy. Intelligence and reasoning live in the Pulser Agent plane (Foundry/Agents).

### 1.2 Thin-Bridge Architecture
The Odoo Python footprint is restricted to:
- Context packaging (reading records user is authorized to see).
- Request delegation to external Pulser endpoints.
- UI rendering of assistant responses and suggested actions.
- Audit logging of every interaction.
- Admin configuration for connectivity and safety policies.

### 1.3 Read-Only Default
Assistant interactions are read-only by default. Write actions (posts, updates, approvals) require:
- Explicit admin-configured allowlists.
- Mandatory user confirmation in the UI.
- Direct ORM execution with audit linking.

### 1.4 Identity-First (Entra ID)
Every interaction must carry the authenticated Odoo user's identity. Production calls use Microsoft Entra ID for user-scoped authorization.

---

## 2. Invariants & Technical Constraints

1. **CE Only**: No dependencies on Odoo Enterprise or odoo.com IAP services.
2. **No LLM/Vector code in Odoo**: No `langchain`, `openai`, or vector stores inside the Odoo process.
3. **Audit Completeness**: Every interaction (including timeouts/failures) produces a non-deletable `ipai.copilot.audit` record.
4. **Graceful Degradation**: Odoo UI remains functional if the Pulser runtime is unavailable.
5. **Safe Models**: Standard Odoo models (`account.move`, `res.partner`) are accessible, but high-risk models are blocked at the adapter layer.
6. **Module Naming**: Legacy modules use `ipai_odoo_copilot` prefix. Future modules follow the `ipai_pulser_*` pattern.
7. **Canonical Path**: Specs live in `spec/pulser-odoo/`.

---

## 3. Tax & Compliance Rules (PH Benchmark)

1. **Dual-Basis Citations**: Every tax action must cite both the legal basis (Tier 1-2 BIR authority) and the localization mapping (Tier 5 Odoo config).
2. **ERP Records are Tier 6**: Never use transaction data to override legal authority.
3. **ATC Codes**: Use official BIR prefixes (WI/WC/WB) for all withholding classifications.
4. **Exception Handling**: Tax exceptions are immutable and must be resolved with evidence before the case is closed.

---

## 4. LLM Application Invariants

1. **Structured Output for Finance**: Every finance-critical response must use a defined JSON schema, not free-form prose.
2. **Grounding Before Generation**: The model must ground answers on active Odoo record fields, extracted document fields, or linked master data before generating any finance claim.
3. **Allowed Fallback States**: The model is explicitly allowed to return `not_found`, `not_yet_computable`, `needs_review`, or `blocked` instead of hallucinating certainty.
4. **No Chain-of-Thought as Safety**: Safety and correctness come from grounded source data, deterministic validations, and explicit action gating — not from chain-of-thought extraction or "show your reasoning" prompts.
5. **Tool Use Before Model Guessing**: Use search/retrieval/record inspection as affordances. Never let the model directly invent partner, tax, or posting state.
6. **Classify-Extract-Validate-Act**: Every finance workflow must separate these phases. No single-step "figure it out" patterns.

---

## 5. Transaction Invariants

1. **Draft-Only Creation**: Pulser creates draft records only. Silent posting is never allowed.
2. **Idempotency Required**: Every transaction must use an idempotency key. Reconnect/retry must not create duplicate drafts.
3. **Credit/Debit Notes for Corrections**: Validated invoice changes use credit note or debit note logic. Direct mutation of posted records is forbidden.
4. **Company Context Validation**: Every transaction must validate that the active company context matches the intended record target. Wrong-company-context actions are hard-blocked.

---

## 6. 8-Plane Governance Invariants

The complete Pulser production capability model spans 8 planes. All planes must be addressed before declaring production readiness.

1. **Data Plane**: Transactional data in Odoo/PG; raw documents in Blob Storage; extraction results stored separately from raw files.
2. **Document Pipeline**: Documents classified before record creation; low-confidence cases stop at review, not auto-post.
3. **LLM Application Layer**: Prompts are task-specific; output is schema-constrained; fallback states are explicit.
4. **Decision / Policy Layer**: Automation boundaries enforced at runtime; Foundry guardrail policies configured.
5. **Transaction Layer**: Drafts only; idempotent; audit-linked; evidence-traced.
6. **Integration Plane**: Structured upload handoff; result callbacks; Odoo-Foundry API contract defined.
7. **Governance / Control Plane**: Evals are real (not just definitions); red-team runs exist; stored completions exist; monitoring alerts are actionable.
8. **Operating / Compliance Plane**: Close cycles are template-instantiated; compliance scenarios are automated; evidence packs are generated; filing readiness is tracked.

---

## 7. External System Boundaries

1. **BIR Boundary**: Pulser never labels a workflow as "officially filed" or "officially paid" without verified external confirmation. BIR-bound workflows use explicit statuses: `ready_for_filing`, `submitted_externally_pending_confirmation`, `officially_confirmed`.
2. **Odoo Stores, Pulser Decides**: Pulser decides and prepares; Odoo stores and posts; humans approve when risk is non-trivial.
3. **No Vanity Metrics**: Number of agents running, models deployed, or eval definitions created without runs do not count as success. Only measured behavior in supported finance workflows counts.

---

## 8. Professional Publishing Principle

Pulser must treat PowerPoint, Word, and Excel generation as a governed professional publishing workflow, not as generic content generation.

For finance, compliance, close, and executive reporting use cases, Pulser must:
- generate native Office artifacts
- ground outputs in approved enterprise sources
- validate formatting and publishability before final output
- retain linked copies in Odoo Documents
- answer based on retained artifacts when they exist

Professional Office outputs must be:
- publishable-quality
- evidence-linked
- reproducible
- reviewable before release

---

## 9. Agentic Pulser — Mission & Doctrine

### 9.1 Mission
Pulser for PH is an agentic ERP finance and project-operations layer for Odoo. It exists to improve finance execution, control quality, project-spend discipline, PH tax/BIR readiness, close operations, and publishable reporting output.

### 9.2 Product doctrine
Pulser must behave as a governed agentic system, not merely a chat assistant.

Pulser must:
- observe live business state
- plan, decide, and act across bounded multi-step workflows
- prefer evidence over unsupported explanation
- enforce validation before completion for finance-critical actions
- retain durable evidence in Odoo Documents
- generate publishable native Office artifacts when requested

### 9.3 Canonical capability families

| # | Family | Scope summary |
|---|--------|---------------|
| 1 | `pulser-data-foundation` | Odoo transactional records, Finance PPM OKR/KR/milestone/task models, company/branch/fiscal period context, retained copies in Documents, read-only grounded access |
| 2 | `pulser-copilot-experience` | Odoo-native side panel, record-aware prompting, explain/block/escalate/recommend interactions, evidence-aware answers, role-aware next-step guidance |
| 3 | `pulser-agentic-workflows` | Plan/decide/act/validate/continue lifecycle, safe-action routing, multi-step completion, stop/escalate/approval boundaries, validation-before-completion |
| 4 | `pulser-analytics-insights-planning` | Analytics for live KPI/finance visibility, insights for anomaly/risk/opportunity surfacing, planning for OKRs/milestones/close sequencing/scenario guidance |
| 5 | `pulser-finance-close-and-reconciliation` | Month-end/year-end/tax-period close, reconciliation assistance, blocker detection, evidence packs, signoff readiness, finance performance review |
| 6 | `pulser-project-spend-and-profitability` | Expense and approval workflows, time/spend visibility, project profitability, cash advance issuance/liquidation, project-to-finance linkage |
| 7 | `pulser-ph-tax-and-bir-readiness` | VAT/withholding/TIN/ATC validation, 2307/2550Q/SAWT/SLSP readiness, BIR evidence packs, explicit external boundary states, missing-requirement blocker routing |
| 8 | `pulser-documents-evidence-grounding` | Retained copies in Odoo Documents, evidence completeness, missing evidence queue, file-linked reasoning and answers, evidence-aware workflow support |
| 9 | `pulser-office-publishing` | PowerPoint Studio, Word Studio, Excel Studio, publishability QA, retained artifact linkage |
| 10 | `pulser-mcp-testing-review-security` | MCP-backed read-only grounding, structured tool execution, evals/validation harnesses, governance/monitoring, review/security gates |

### 9.4 CFO operating triad
The clean finance operating surface is: **analytics → insights → planning**. All dashboard, reporting, and agentic-workflow design should align to this triad.

### 9.5 Agentic lifecycle
Every Pulser workflow must follow this governed lifecycle before production promotion:

```
Plan → Prototype → Create → Test → Review → Optimize → Secure
```

No finance-critical workflow may jump from generation to completion without validation and review boundaries.

---

## 10. Canonical Capability Family Principle

Pulser for PH must organize product scope, implementation planning, and delivery sequencing around the 10 canonical capability families defined in §9.3.

These families are the **target architecture** for Pulser and must be used consistently across:
- PRD scope definitions
- implementation plan phases
- task and board structure (epics, issues, tasks)
- OKR objective and key-result mapping
- evaluation suite organization
- release gate criteria

### Usage mandate
Every major feature, workstream, board epic, and release gate must declare which canonical capability family or families it advances. Unnamed scope is not valid scope.

### Governance tiers

| Tier | Families | Priority |
|------|----------|----------|
| 1 — Foundation | `pulser-data-foundation`, `pulser-copilot-experience`, `pulser-agentic-workflows`, `pulser-analytics-insights-planning`, `pulser-documents-evidence-grounding` | Must be in place before Tier 2 |
| 2 — Business execution | `pulser-finance-close-and-reconciliation`, `pulser-project-spend-and-profitability`, `pulser-ph-tax-and-bir-readiness` | Core value-delivery lanes |
| 3 — Scale and governance | `pulser-office-publishing`, `pulser-mcp-testing-review-security` | Governed publishing and operational hardening |

### Design rule
Pulser should go **deeper** in these finance, project-operations, close, compliance, evidence, and publishing lanes rather than mirror the full breadth of a general-purpose ERP or CRM suite. Scope expansion outside these families requires explicit spec amendment.

---

## 11. Git and Delivery Governance Invariant

All Pulser code changes must follow a governed, pipeline-driven delivery model. This is a hard engineering invariant, not a preference.

### SCM rule
- All source control uses **Git** (not TFVC, not direct-to-main).
- Every change ships via a **pull request** against a protected branch.
- No direct pushes to `main`, `release/*`, or equivalent protected branches.

### Branch policy rule
All key branches across scoped Pulser repos must enforce:
- required PR review before merge
- required status checks (lint, unit tests, security scans) before merge
- no self-approval where Azure DevOps / GitHub policy supports enforcement

### Pipeline rule
All environment changes (staging and production) must flow through a pipeline. No manual environment mutations outside pipeline execution.

### Runtime rule
Pulser defaults to **container-based delivery** for agent and web surfaces. VM-based deployment is an exception path only for workloads that require host-level control. Exceptions require documented justification.

### Azure DevOps rule
Azure DevOps is used for Boards, Pipelines, and MCP-integrated delivery workflows. TFVC and Azure DevOps Server on-prem are not required and should not be adopted unless a hard regulatory or isolation requirement mandates it.

### CAF lifecycle rule
Pulser must be operated as a real cloud adoption program under the Microsoft Cloud Adoption Framework lifecycle: **Strategy → Plan → Ready → Adopt → Govern → Secure → Manage**. IAM cleanup, landing-zone separation, and security hardening are part of Govern/Secure — not optional side maintenance.

---

## 12. Mandatory Identity and Governance Production Gates

Pulser for PH cannot be promoted to production or claim production-ready status while any of the following governance gaps remain unresolved. This rule is absolute and superior to feature completion.

### 12.1 Identity Invariants
1. **Azure RBAC cleanup**: The Azure estate must be least-privilege aligned.
2. **Root-scope isolation**: Unexplained root-scope standing privileged access (User Access Administrator or Owner) must be removed or formally justified via break-glass policy.
3. **Ghost Principal elimination**: All unknown/orphaned Owner principals at subscription scope must be eliminated.
4. **JIT/PIM posture**: Privileged human/admin access must be moved toward eligible / time-bound activation (Azure PIM).
5. **Agent Identity Governance**: Every production agent identity must have an accountable human sponsor/owner and a defined review cadence.

### 12.2 Governance Invariants
1. **CAF Alignment**: Rollout must be mapped to the CAF Strategy → Plan → Ready → Adopt → Govern → Secure → Manage lifecycle.
2. **Landing Zone separation**: Platform, Application, and Security responsibilities must be logically and/or physically separated in Azure.
3. **Auditability**: Every agentic interaction must be traces in `ipai.copilot.audit`.

---

## 13. SaaS Multitenancy Principle

Pulser must be designed as a business-to-business (B2B) multitenant SaaS platform.
- **Tenant Definition**: For Pulser, a tenant is a customer organization.
- **Independence**: An Odoo company, branch, department, or project is an internal structure and is not the same thing as a SaaS tenant.
- **Identity Isolation**: The Microsoft Entra tenant (identity substrate) must be distinguished from the Pulser customer tenancy (business substrate).

## 14. Control Plane Principle

Pulser must include a productized control plane for lifecycle and rollout management, separated from the tenant data plane.
- **Service-level Control Plane**: Governs tenant onboarding, stamp assignment, release targeting, policy distribution, and platform health.
- **Tenant-level Admin Plane**: Governs tenant-specific settings, maintenance actions, feature enablement, and evidence/document policies.

## 15. Deployment Stamp Principle

Pulser must scale and isolate through **deployment stamps**.
- **Definition**: A deployment stamp is an independently deployable and recoverable slice of runtime and platform capacity serving a bounded set of tenants.
- **Role**: Stamps are used to reduce blast radius, support safe progressive rollouts, and enable regional expansion.

## 16. Live-Site-First Principle

Pulser must be operated with a live-site-first posture.
- **Operational Priority**: Production telemetry, actionable alerts, progressive exposure, and automated recovery are first-class product requirements.
- **Reliability Culture**: Engineering owns the production quality; hotfixes follow the same Git discipline as features.

---

## 17. Layered Architectural Invariant: Core and Shells

Pulser is designed as a modular platform where a single reasoning authority serves multiple delivery shells.

### 17.1 The Pulser Core
The center of the platform is the **Pulser Core**, which owns reasoning, authority, and state:
- **ERP Authority**: Odoo (Action) and Odoo Documents (Evidence).
- **Reasoning Plane**: Azure AI Foundry, OpenAI, and AI Search.
- **Platform Management**: SaaS Control Plane and Deployment Stamps.

### 17.2 The Three Shells
Delivery is handled through three distinct shells around the core:
1. **Core SaaS/Runtime Shell**: The primary web/API gateway for customer-facing services.
2. **Enterprise Productivity Shell**: Adapters for M365 Copilot, Teams, and future Outlook/Excel experiences (leveraging Microsoft Agents SDK).
3. **Engineering/Operator Shell**: Adapters for repository-aware internal assistants and DevOps copilots (leveraging GitHub Copilot SDK).

### 17.3 Dependency Rule
The Pulser Core must not depend on the specific authentication, billing, or substrate assumptions of its delivery shells (e.g., Dataverse, Copilot Studio, or GitHub Copilot key-based auth). Shells are **adapters** to the core, not its foundation.

---

*Last updated: 2026-04-11*
