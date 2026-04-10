# Implementation Plan — Pulser: Odoo 18 PH Copilot

## Status
Draft

---

## Technical summary
Pulser will be implemented as an Odoo-native copilot shell backed by Microsoft Foundry.
Use the Foundry SDK and project endpoint for agent-native capabilities such as agents,
evaluations, and tracing; use the OpenAI-compatible client for model-shaped interactions.
Use Foundry Tools only for workload-specific services such as Document Intelligence and
search/grounding integration where needed. The Foundry article explicitly distinguishes these
lanes and recommends the Foundry SDK for Foundry-native features.

---

## Architecture decisions

### AD-001 — Primary runtime
Use Microsoft Foundry as the primary Pulser runtime for:
- agent orchestration
- evaluation flows
- tracing
- project-scoped configuration

Rationale:
- Pulser is an agentic application, not inference-only
- Foundry SDK is the recommended path for agents and project-native capabilities
- project endpoint reduces endpoint sprawl for the app surface

### AD-002 — Model interaction path
Use an OpenAI-compatible client derived from the Foundry project client for:
- responses
- structured outputs
- summarization
- action planning
- model/tool-call shaped interactions

### AD-003 — Odoo remains SoR
Keep Odoo 18 as the transactional system of record.
Pulser may read Odoo context and propose or execute bounded actions, but it does not become
the source of truth for records, approvals, journals, invoices, or compliance state.

### AD-004 — Thin bridge doctrine
Keep `ipai_*` limited to thin bridge/meta behavior. Do not build parity-replacement ERP modules
under Pulser scope when Odoo/OCA already own the domain behavior.

### AD-005 — Approval-gated action model
Classify actions into:
- low risk: allowed tool execution if policy allows
- medium risk: soft confirmation or supervisor review
- high risk: mandatory human approval

---

## Endpoint assumptions
- Foundry base resource endpoint is confirmed as:
  `https://ipai-copilot-resource.services.ai.azure.com/`
- Project-specific endpoint must append:
  `/api/projects/<project-name>`
- Project name is currently unknown in this spec and must remain a placeholder until verified.

---

## Workstreams

### Workstream 1 — Odoo assistant shell
Deliver:
- OWL systray entry point
- contextual side panel or modal
- record-context packaging
- user/session correlation

### Workstream 2 — Pulser gateway/service
Deliver:
- Foundry SDK project client initialization
- OpenAI-compatible client usage path
- prompt/context assembly
- policy enforcement
- tool dispatch
- trace correlation

### Workstream 3 — Knowledge grounding
Deliver:
- approved policy sources
- PH compliance reference sources
- historical transaction grounding strategy
- retrieval contracts and citation/explanation format for internal use

### Workstream 4 — Finance and compliance tools
Deliver:
- record explanation tool
- AP review tool
- draft note/email/follow-up tool
- PH compliance checklist/workpaper tool
- bounded Odoo action tools

### Workstream 5 — Evals and observability
Deliver:
- eval dataset for supported scenarios
- trace inspection
- latency/error instrumentation
- action safety audit logs

---

## Module and service boundaries

### Odoo addon boundary
Owns:
- UI surfaces
- context extraction
- access-control-aware record packaging
- server actions exposed to Pulser

Does not own:
- heavy model orchestration
- standalone retrieval infrastructure
- cross-system policy engine outside required bridge logic

### Pulser service boundary
Owns:
- Foundry client integration
- orchestration
- tool routing
- policy gates
- trace metadata
- eval hooks

Does not own:
- final transactional truth
- business logic already native to Odoo/OCA

---

## Data flow
1. User opens a supported Odoo record or general assistant entry point
2. Odoo addon assembles scoped context based on current record and user permissions
3. Pulser gateway sends request through Foundry project integration
4. Model/agent selects response path:
   - direct answer
   - retrieval-grounded answer
   - tool proposal
5. Policy engine classifies requested action
6. If action is low-risk and allowed, bounded tool executes
7. If action is high-risk, approval UI is required before execution
8. Trace/log metadata is persisted
9. Result is returned to Odoo UI with rationale/explanation

---

## NFRs
- P95 assistant response for simple record-summary flows should be operationally acceptable for in-app use
- Every executed tool action must emit a trace/log record
- Pulser must respect Odoo ACLs and record rules
- Fail closed on ambiguous high-risk actions
- Degrade gracefully when Foundry, retrieval, or document services are unavailable

---

## Risks
- Over-scoping into a generic multi-agent platform
- Weak grounding quality producing confident but low-value answers
- Excessive addon complexity instead of thin bridge behavior
- Compliance expectations exceeding MVP document/tool coverage

---

## Rollout phases

### Phase 1
- record summary
- record explanation
- draft generation
- trace baseline

### Phase 2
- AP review assistance
- expense/account/tax suggestions
- anomaly and variance explanation

### Phase 3
- PH compliance checklist/workpaper flows
- retrieval-grounded policy answers
- approval-gated bounded actions

### Phase 4
- eval hardening
- observability
- safety refinement
- expanded supported record types

---

## Touch points

### Repo paths
- `addons/ipai/ipai_odoo_copilot/` — canonical copilot shell
- `addons/ipai/ipai_copilot_actions/` — action queue + approval
- `addons/ipai/ipai_*` — thin bridge modules only
- `spec/pulser-odoo-ph/` — this spec bundle
- `docs/architecture/` — architecture decision records

### Services
- **Odoo addon** = UI + server actions + access control + context packaging
- **Pulser gateway/service** = Foundry client, tool routing, policy enforcement, trace correlation
- **Retrieval index** = policies, BIR references, internal docs
- **Evidence store/logging** = prompt/response/tool audit trail
