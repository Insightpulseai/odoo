# Constitution — Reverse AvaTax for Odoo 18 Pulser

> Immutable architecture rules for the Odoo-native tax intelligence
> platform that reverses Avalara AvaTax's external tax engine model.

---

## Principle 1 — Odoo owns transactional truth

Invoices, vendor bills, expenses, tax records, and journal entries remain
Odoo-owned state. No connector, bridge, or agent may become a second
accounting source of truth.

## Principle 2 — External tax intelligence is connector-bound

Address validation, jurisdiction enrichment, and external tax-engine calls
must be isolated behind connector boundaries. Connectors are swappable
adapters, not embedded business logic.

## Principle 3 — Agentic review is explainable

Every Pulser tax decision, recommendation, or exception route must include:

- Rationale (why this decision)
- Source inputs (which data informed it)
- Confidence level
- Audit trace (reversible action log)

No opaque autonomous tax decisions.

## Principle 4 — No parallel ledger

No bridge, connector, or agent may become a second accounting source of
truth. Tax computation results feed into Odoo tax lines; they do not
maintain a separate tax ledger.

## Principle 5 — Local compliance is pack-based

Country- or tenant-specific tax/compliance behavior must be expressed as
installable policy/compliance packs, not core rewrites. PH BIR compliance
is the first pack. Packs are versioned, auditable, and independently
deployable.

## Principle 6 — Draft-first posting

External tax computation results enter Odoo as draft tax line proposals.
Posting requires Odoo-side approval workflow. No external system may
directly create posted tax entries.

## Principle 7 — MVP is explainable validation, not a full tax engine

The MVP is an Odoo-native tax/compliance control plane focused on validation
and explainable exceptions. It is not a standalone tax engine or full AvaTax
replacement.

Non-MVP bridge capabilities (broad filing automation, advanced autonomous
tax operations, mandatory third-party tax engine dependence) are not
required baseline. They are promotion-lane work.

## Principle 8 — Azure-native only

All runtime, identity, secrets, observability, and AI execution must be
Azure-native per platform doctrine.

- Runtime: Azure Container Apps
- Identity: Microsoft Entra ID
- Secrets: Azure Key Vault + managed identity
- Document Intelligence: Azure Document Intelligence
- AI: Azure AI Foundry (when governed runtime required)

## Principle 9 — MVP is a viable horizontal slice

For ERP/SaaS-adjacent features, MVP must be defined as the smallest viable
cross-cutting slice that delivers end-to-end value. Avoid isolated
component-only MVPs when the user workflow depends on multiple tightly
connected business objects.

## Principle 10 — SaaS and multitenancy are separate decisions

SaaS is the delivery/business model. Multitenancy is an architecture choice.
Tenant model, data isolation, and shared-component boundaries must be chosen
explicitly per feature.

## Principle 11 — External checklists inform review, not source-of-truth design

Community and external review checklists may be used to validate readiness
and catch omissions, but they do not replace the feature bundle as the
source of truth.

- Azure review checklists are review aids and promotion-lane controls.
- Odoo go-live checklists are operational readiness aids.
- Neither may override Odoo-first workflow/accounting truth or the MVP
  scope defined in this bundle.

## Principle 12 — Odoo-native testing is required

Addon and bridge code must follow Odoo-native testing patterns.

At minimum:

- model/business logic tests use Odoo test case classes
- form-driven behaviors use server-side `Form` tests
- HTTP / tour behavior uses `HttpCase` only where UI flow coverage is actually required
- test selection must be explicit through tags
- browser-critical end-to-end flows may use Playwright where backend/form
  coverage is insufficient
- MVP is not complete without executable tests for core workflows

## Principle 13 — Browser automation is targeted, not default

Playwright is reserved for browser-critical flows and smoke coverage.
Chrome DevTools is a debugging surface, not the primary test framework.
Manual QA and ad hoc scripts do not replace executable automated tests.

## Principle 14 — MCP tooling is optional and bounded

MCP servers are optional developer and operator tooling surfaces. They
assist with automation, debugging, reference lookup, and platform
validation. They must never own workflow state, business logic, or
approval truth.

Allowed roles:

- Playwright MCP for browser automation
- Chrome DevTools MCP for debugging
- Azure MCP Server for platform/runtime validation
- Microsoft Learn MCP for documentation lookup

Prohibited role: MCP as the primary owner of workflow or business state.

## Principle 15 — Experimental MCP integrations are non-critical

Experimental or preview MCP integrations (e.g., Azure AI Foundry MCP)
must not be on the MVP critical path. They may be evaluated and adopted
when stable, but must not block delivery or become implicit dependencies.

## Principle 16 — Foundry Project Connections Are Optional and Minimum-Necessary

The Foundry project (`ipai-copilot`) supports attachable connections (Azure OpenAI,
AI Search, Cosmos DB, Storage, Fabric, etc.). These are optional enrichments, not
mandatory baseline dependencies.

- Do not assume any connection is already configured unless explicitly proven.
- For the AvaTax connector / tax intelligence surface: attach Azure OpenAI only
  where AI-assisted tax explanation or confidence scoring is explicitly required;
  omit AI Search unless RAG over a compliance corpus is in scope; access Document
  Intelligence via the AI Services endpoint, not a separate project connection.
- Add only the minimum connections required for MVP.
- Microsoft Fabric is preview and must not be on the MVP critical path.
- Document every new project connection before implementation depends on it.

## Principle 17 — API edge replacement is facade-only

FastAPI or external API layers may replace the public/mobile API edge,
but they must not replace Odoo/OCA as the owner of workflow, approvals,
accounting, tax, or ERP state. The FastAPI edge may package, orchestrate,
proxy, or expose workflows, but Odoo remains the authoritative write path
for all ERP business objects.
