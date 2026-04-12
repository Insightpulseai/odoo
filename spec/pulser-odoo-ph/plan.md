# Implementation Plan — Pulser: Odoo 18 PH Copilot

## Status
Active

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

### AD-006 — Container application hosting baseline

Pulser services should use an Azure-managed container application hosting model appropriate
for microservices, API endpoints, background processing, and event-driven workloads.

### AD-007 — Split interactive and worker runtimes

User-facing conversational/API flows and background processing flows must be deployable
independently so they can scale, fail, and roll back independently.

### AD-008 — Internal-first service communication

Only user-facing entrypoints should require external ingress. Internal Pulser services
should prefer internal ingress and service-to-service discovery.

### AD-009 — Revision-safe delivery

Pulser deployments must use revision-aware rollout and rollback semantics so new versions
can be introduced with controlled risk.

### AD-010 — YAML-defined pipeline authority

Pulser delivery pipelines must be defined in version-controlled YAML. Azure DevOps pipeline
state must not become the primary source of truth over repo-authored pipeline definitions.

### AD-011 — CLI-driven pipeline operations

Pipeline lifecycle operations such as list, inspect, queue, update, and delete should be
automatable through Azure DevOps CLI and REST-backed flows, rather than relying on manual
portal-only operations.

### AD-012 — Repo-first release automation

Build, test, package, deploy, and rollback orchestration should be triggered from committed
pipeline definitions and branch/revision state, not ad hoc manual configuration in the
Azure DevOps UI.

### AD-013 — Multi-stage YAML delivery model

Pulser delivery must use a multi-stage YAML pipeline rather than a single flat build pipeline.
The minimum production-oriented stage model is: Build → Test → Deploy to Staging → Deploy to Production.

### AD-014 — Non-skippable quality gates

Stages that enforce required quality, security, or compliance controls must be marked as
non-skippable where appropriate.

### AD-015 — Human validation for protected deploys

Protected deployment stages must support manual validation / approval before execution
against protected environments or resources.

### AD-016 — Branch-gated production deployment

Production deployment stages must run only from explicitly allowed branches, at minimum
the canonical default branch and any explicitly approved release branches.

### AD-017 — Rollback and alternate deploy paths are explicit exceptions

Rollback and alternate production deployment paths must be modeled as explicit manual stages,
not hidden ad hoc operator behavior.

### AD-018 — Pipeline settings are governed operational state

Pipeline settings that affect execution behavior — including paused/disabled state, YAML path,
and work-item linking behavior — must be documented as governed runtime metadata, not tribal
knowledge.

### AD-019 — Foundry Agent Service is the managed agent runtime

Pulser agent execution should use Foundry Agent Service as the managed runtime for agent
conversations, tool orchestration, and governed production execution.

### AD-020 — RAG-first enterprise grounding

Pulser must prefer Foundry IQ / RAG over protected enterprise data as the primary grounding
pattern for business answers and recommendations.

### AD-021 — Fine-tuning is an exception path

Fine-tuning is allowed only when retrieval, prompting, and tool/workflow design do not meet
quality or latency targets.

### AD-022 — Enterprise identity and secret handling

Pulser services should prefer managed identities and external secret stores over embedded
credentials or repo-stored secrets.

### AD-023 — Private-by-default service topology

Where feasible, Pulser service dependencies such as knowledge stores, search, and
agent-adjacent services should use private/internal connectivity rather than unnecessary
public exposure.

### AD-024 — Observability is part of runtime definition

Operational monitoring, traceability, and quality/safety evaluation are required runtime
properties, not optional post-launch additions.

---

## Endpoint assumptions
- Foundry base resource endpoint is confirmed as:
  `https://ipai-copilot-resource.services.ai.azure.com/`
- Project-specific endpoint:
  `https://ipai-copilot-resource.services.ai.azure.com/api/projects/ipai-copilot`
- OpenAI-compatible endpoint:
  `https://ipai-copilot-resource.openai.azure.com/openai/v1`
- Project name: `ipai-copilot` (verified 2026-04-10)

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

### Workstream 6 — Runtime hosting and delivery

Deliver:

- containerized runtime boundary definitions
- separation of interactive services from background workers
- ingress model:
  - external for user-facing Pulser entrypoints
  - internal for private service components
- revision rollout / rollback expectations
- secrets, configuration, and telemetry handling

### Workstream 7 — Pipeline governance and automation

Deliver:

- map existing build/deploy flows to YAML pipeline definitions
- ensure pipeline metadata is reproducible from repo state
- define CLI-capable operational actions:
  - list pipelines
  - inspect pipeline details
  - queue runs
  - update pipeline metadata when required
  - delete deprecated pipelines safely
- define controlled exceptions where REST calls are needed beyond first-class CLI coverage

### Workstream 8 — Production pipeline shape

Deliver:

- canonical stage graph for pulser-odoo delivery
- which stages are skippable vs non-skippable
- staging and production validation requirements
- branch conditions for protected deploys
- rollback / alternate deploy exception flow

### Workstream 9 — Pipeline security controls

Deliver:

- approvals/checks required for protected resources
- service connection branch restrictions where applicable
- variable group authorization model
- agent trust model:
  - Microsoft-hosted by default
  - self-hosted only by explicit exception

### Workstream 10 — Knowledge plane and grounding

Deliver:

- grounded sources for Pulser answers
- retrieval boundaries between Odoo transactional data and indexed enterprise knowledge
- when structured lookup, semantic retrieval, and tool calls are each used
- criteria for when fine-tuning is justified

### Workstream 11 — AI platform security and observability

Deliver:

- managed identity / secret handling approach
- private/internal connectivity expectations
- monitoring, tracing, evaluation, and safety telemetry requirements
- protected access patterns for model and knowledge dependencies

### Workstream 12 — In-context document workflows

Deliver:

- classify uploaded attachments by document type
- extract structured invoice fields automatically via Document Intelligence
- match extracted data against Odoo entities (vendor, journal, taxes)
- surface structured confirmation cards in the Pulser side panel
- support one-click governed actions (create draft vendor bill, route for review)
- handle low-confidence and duplicate-detection exception paths
- display workflow state chips (uploaded → extracting → ready → draft created)

### Workstream 13 — Connectivity and action reliability

Deliver:

- retry/resume behavior for real-time connection loss
- idempotency keys for transactional actions
- visible status model for async jobs and pending actions
- degraded-mode behavior when Foundry or DI services are unavailable

### Workstream 14 — Accounting document directionality

Deliver:

- detect issuer vs recipient roles from invoice layout
- determine probable accounting direction:
  - customer invoice
  - vendor bill
  - credit note
  - unsupported/ambiguous
- bind next-action proposals to active Odoo company context

### Workstream 15 — Scenario engine

Deliver:

- canonical classifier for invoice/bill/expense/payment/correction families
- classification bound to active company context
- distinguish employee expense flow from AP bill flow
- distinguish issuer-side AR documents from recipient-side AP documents
- PO-match detection before raw line creation
- credit/debit note routing for posted-document corrections

### Workstream 16 — Exception engine

Deliver:

- duplicate reference checks
- partner matching (exact, fuzzy, missing)
- journal/tax validation
- PO matching and price variance detection
- reimbursement eligibility checks
- multi-company / branch / currency consistency checks
- retry/idempotency handling for transactional actions
- OCR confidence thresholds and manual-review routing

### Workstream 17 — Active form grounding

Deliver:

- capture active model, view type, record id/state, and visible field values from page context
- bind short user utterances to active-record intent
- prefer form-aware interpretation over generic fallback
- normalize typo-heavy prompts in finance contexts ("TA" → "tax", "COMPITER" → "computed")

### Workstream 18 — Expense validation skills

Deliver:

- inspect hr.expense draft state (category, amount, taxes, paid_by, employee)
- inspect category tax defaults
- compare receipt extraction against form values
- explain why tax is correct, missing, not applicable, or not yet computable
- create hr.expense from DI extraction output (create_expense safe action)

### Workstream 19 — Decision engine

Deliver:

- deterministic scenario routing from intake signal + active company context
- directionality overrides (issuer=AR, recipient=AP, employee=expense)
- confidence-to-action gating (HIGH→auto-draft, MEDIUM→review card, LOW→block)
- blocker handling (duplicate, missing master data, context mismatch)
- idempotent retry behavior for transactional actions
- fixed safe-action enum — model never improvises action names

### Workstream 18 — Eval dataset and rubrics

Deliver:

- canonical finance taxonomy (AR/AP/expense/correction/payment/ambiguous families)
- gold-label JSON schema with separate classification/extraction/decision/validation labels
- balanced JSONL datasets: smoke, core, edge, adversarial, regression
- annotation guide with context-sensitive labeling rules
- scoring rubrics for explanation quality and action selection
- release thresholds and hard-fail conditions
- context-sensitive eval cases (same artifact, different company → different correct answer)
- adversarial cases: directionality traps, duplicate traps, expense-vs-bill confusion

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

### Phase 1.5 — Runtime baseline hardening

- Containerize Pulser-facing services
- Establish external vs internal ingress boundaries
- Establish centralized logging / traces
- Establish revision-safe deployment path
- Establish job/worker lane for document and reconciliation processing

### Phase 1.6 — Delivery control-plane hardening

- Establish multi-stage YAML delivery
- Enforce non-skippable required gates
- Add manual validation for protected deploy stages
- Add branch-gated production conditions
- Add rollback/manual exception stages
- Authorize required variable groups and protected resources

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

---

## Acceptance gates

- Hosting boundary is defined: interactive vs worker
- Ingress boundary is defined: external vs internal
- Scaling mode is identified: request-driven, event-driven, scheduled, or fixed
- Rollback path is defined for each deployable runtime unit
- Telemetry destination and minimum trace fields are specified
- Each delivery pipeline has a version-controlled YAML definition
- No required production flow depends on portal-only manual configuration
- Operational actions required by release automation can be performed through CLI or scripted REST
- Default org/project targeting is documented for automation contexts
- Any stage-skip or emergency-run behavior is explicitly governed and auditable
- Pipeline is defined as YAML in-repo via documented YAML path
- Stage graph includes build/test/deploy separation
- Required quality/security stages are identified as skippable or non-skippable
- Protected deployment stages define manual validation / approval requirements
- Production deploy condition explicitly restricts source branches
- Variable groups used by YAML are explicitly authorized
- Service/resource access checks are documented for protected resources
- Rollback or alternate deploy behavior is explicit and manually governed
- The runtime clearly distinguishes model, tool, and retrieval responsibilities
- Grounding sources are identified and protected
- Any fine-tuning proposal includes a written justification for why RAG/tooling is insufficient
- Secret handling avoids repo-stored credentials and inline pipeline secrets
- Monitoring covers runtime health, agent behavior, and model usage/cost
- Externally exposed endpoints are explicitly justified; internal dependencies are not assumed public
- Invoice upload flow does not stop at generic conversational guidance
- Extraction result is shown as structured business data, not prose only
- At least one governed Odoo action is available directly from the extraction result
- Duplicate / vendor-match / missing-field checks run before draft creation
- Connectivity loss does not create ambiguous action outcomes
- For a clear single-page invoice, Pulser outputs extracted header/monetary fields, probable
  accounting document type, and at least one correct governed Odoo action
- Pulser proposes customer invoice or vendor bill based on document direction and company context
- In Expenses form context, "tax?" must not trigger a generic module clarification
- For incomplete expense drafts, Pulser identifies missing fields blocking tax computation
- For completed expense drafts, Pulser explains current tax state using live record data
- Pulser tolerates noisy/typo-heavy short prompts in finance contexts

---

## Anti-goals

- Do not collapse all Pulser responsibilities into a single monolithic runtime if interactive
  and batch workloads have different scaling and failure characteristics.
- Do not expose internal worker or retrieval services publicly without a clear requirement.
- Do not rely on Classic pipelines as the long-term authority model.
- Do not allow pipeline behavior to drift from repo-authored YAML without a committed change.
- Do not require manual Azure DevOps portal edits for standard release operations.
- Do not treat production deployment as just another automatic post-build step.
- Do not allow protected deployment stages to execute from arbitrary branches.
- Do not reference secret-bearing variable groups in YAML without explicit pipeline authorization.
- Do not make rollback an undocumented operator-only procedure.
- Do not default to fine-tuning when retrieval and tool design can solve the problem.
- Do not treat model-only chat output as sufficient for sensitive business actions.
- Do not store long-lived secrets in repo code, pipeline YAML, or addon manifests.
- Do not expose internal knowledge or agent dependencies publicly without a deliberate requirement.
- Do not force users to manually translate assistant suggestions into ERP actions.
- Do not use chat prose as the only UI for document extraction workflows.
- Do not allow reconnect failures to obscure whether a transactional action succeeded.
- Do not ask the user which module they mean when the active screen already provides the answer.
- Do not treat expense-tax validation like a generic accounting FAQ.
- Do not ignore visible zero/blank values when answering computation questions.

## 16. Identity and authentication implementation model

### Odoo authentication lane
Use Odoo's documented Microsoft Azure OAuth sign-in flow as the primary internal-user SSO model.

### Core implementation components
- Odoo system parameter enabling authorization header handling
- Entra app registration for Odoo login
- single-tenant internal-user audience by default
- redirect URL bound to the canonical Odoo base URL with `/auth_oauth/signin`
- Odoo OAuth provider configuration
- controlled first-link/reset/invitation flow

### Pulser gateway and web surfaces
For custom Pulser surfaces outside native Odoo login:
- use MSAL family libraries
- prefer package-managed integration
- avoid deprecated CDN delivery
- align scopes, token handling, and tenant model with Entra authority design

### Runtime/service identity
Use service identities or managed identities for:
- gateway-to-backend access
- Foundry/Azure service access
- storage/search/runtime integrations
- MCP and read-only database access where supported

### Guardrails
- internal employee auth and portal auth must not be conflated
- finance/document access must respect role boundaries
- read-only grounding paths must remain read-only
- first-user linking flow must match Odoo-supported behavior
