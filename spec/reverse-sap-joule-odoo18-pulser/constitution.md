# Constitution — Reverse SAP Joule for Odoo 18 Pulser

> Immutable architecture rules for the Odoo-native AI copilot/agent
> platform that reverses SAP Joule's ERP AI assistant model.

---

## Principle 1 — Pulser is Odoo-first

Pulser must ground all business actions in Odoo models, permissions, and
workflow state. Odoo is the transactional backend; Pulser is the
intelligence layer. Pulser never becomes a parallel system of record.

## Principle 2 — Copilot shell and agent runtime are separate concerns

Conversational UX (the copilot shell) and managed agent execution (the
agent runtime) must remain distinct architectural layers. The shell handles
user interaction; the runtime handles orchestration, tool invocation,
tracing, and evaluation.

## Principle 3 — RAG is for knowledge, not ERP truth

Retrieval-augmented generation may support help documentation, SOPs,
policy lookup, and procedural guidance. It must not replace live
operational state from Odoo. When a user asks "what is invoice X status?",
the answer comes from Odoo, not from a search index.

## Principle 4 — Safe action gates are mandatory

All transactional actions must be classified as one of:

- **Advisory**: suggest, preview, no state change
- **Approval-gated**: propose action, require human confirmation
- **Auto-routable**: low-risk, policy-compliant, auto-execute with audit log

No unclassified transactional action may execute.

## Principle 5 — Domain agents are subordinate to workflow truth

Specialized agents (expense agent, project agent, tax agent, HR agent) may
act on work, but never bypass Odoo approval, accounting, or permission
controls. Agent actions are bounded by the same security groups and
record rules that apply to human users.

## Principle 6 — Explainability is mandatory

Every Pulser action must emit:

- Rationale (why this action)
- Source inputs (which data informed it)
- Confidence level
- Referenced policy or rule
- Reversible action log

No opaque autonomous decisions.

## Principle 7 — MVP is the lightweight pilot lane

The MVP default is the lightweight pilot runtime (Azure Container Apps),
not the full governed landing-zone lane (Foundry Agent Service). Governed
runtime is a promotion target, not MVP baseline.

Non-MVP bridge capabilities (broad multi-agent autonomy, heavy cross-suite
orchestration, mandatory governed deployment) are not required baseline.

## Principle 8 — Azure-native runtime

All Pulser runtime, identity, secrets, observability, and AI execution
must be Azure-native per platform doctrine.

## Principle 9 — MVP is a viable horizontal slice

For ERP/SaaS-adjacent features, MVP must be defined as the smallest viable
cross-cutting slice that delivers end-to-end value. Avoid isolated
component-only MVPs when the user workflow depends on multiple tightly
connected business objects.

## Principle 10 — SaaS and multitenancy are separate decisions

SaaS is the delivery/business model. Multitenancy is an architecture choice.
Tenant model, data isolation, and shared-component boundaries must be chosen
explicitly per feature.

## Principle 11 — Control plane is first-class

Administrative control, tenant/workspace/project configuration, and
operational rollout controls are part of the product architecture, not an
afterthought.

- Runtime: Azure Container Apps (pilot) / Foundry Agent Service (governed)
- Identity: Microsoft Entra ID
- Secrets: Azure Key Vault + managed identity
- AI: Azure AI Foundry
- Search: Azure AI Search (only when knowledge grounding required)

## Principle 12 — External checklists inform review, not source-of-truth design

Community and external review checklists may be used to validate readiness
and catch omissions, but they do not replace the feature bundle as the
source of truth.

- Azure review checklists are review aids and promotion-lane controls.
- Odoo go-live checklists are operational readiness aids.
- Neither may override Odoo-first workflow/accounting truth or the MVP
  scope defined in this bundle.

## Principle 13 — Odoo-native testing is required

Addon and bridge code must follow Odoo-native testing patterns.

At minimum:

- model/business logic tests use Odoo test case classes
- form-driven behaviors use server-side `Form` tests
- HTTP / tour behavior uses `HttpCase` only where UI flow coverage is actually required
- test selection must be explicit through tags
- browser-critical end-to-end flows may use Playwright where backend/form
  coverage is insufficient
- MVP is not complete without executable tests for core workflows

## Principle 14 — Browser automation is targeted, not default

Playwright is reserved for browser-critical flows and smoke coverage.
Chrome DevTools is a debugging surface, not the primary test framework.
Manual QA and ad hoc scripts do not replace executable automated tests.

## Principle 15 — MCP tooling is optional and bounded

MCP servers are optional developer and operator tooling surfaces. They
assist with automation, debugging, reference lookup, and platform
validation. They must never own workflow state, business logic, or
approval truth.

Allowed roles:

- Playwright MCP for browser automation
- Chrome DevTools MCP for debugging
- Azure MCP Server for platform/runtime validation
- Microsoft Learn MCP for documentation lookup
- Azure DevOps MCP only if work-item sync is explicitly in scope

Prohibited role: MCP as the primary owner of workflow or business state.

## Principle 16 — Experimental MCP integrations are non-critical

Experimental or preview MCP integrations (e.g., Azure AI Foundry MCP)
must not be on the MVP critical path. They may be evaluated and adopted
when stable, but must not block delivery or become implicit dependencies.

## Principle 17 — Foundry Project Connections Are Optional and Minimum-Necessary

The Foundry project (`ipai-copilot`) supports attachable connections (Azure OpenAI,
AI Search, Cosmos DB, Storage, Fabric, etc.). These are optional enrichments, not
mandatory baseline dependencies.

- Do not assume any connection is already configured unless explicitly proven.
- For the Pulser assistant / agent runtime: attach Azure OpenAI where inference is
  required; attach AI Search only when knowledge grounding over a policy corpus is
  explicitly in scope (governed mode, not pilot mode); attach Application Insights
  where App Insights is the declared observability target.
- Add only the minimum connections required for MVP.
- Microsoft Fabric is preview and must not be on the MVP critical path.
- Document every new project connection before implementation depends on it.

## Principle 18 — API edge replacement is facade-only

FastAPI or external API layers may replace the public/mobile API edge,
but they must not replace Odoo/OCA as the owner of workflow, approvals,
accounting, tax, or ERP state. The FastAPI edge may package, orchestrate,
proxy, or expose workflows, but Odoo remains the authoritative write path
for all ERP business objects.
