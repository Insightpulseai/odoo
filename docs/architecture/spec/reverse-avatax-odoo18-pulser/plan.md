# Plan — Reverse AvaTax for Odoo 18 Pulser

## Architecture Boundaries

### Odoo-owned

- Invoices and invoice tax lines
- Vendor bills and bill tax computation
- Expenses and expense tax allocation
- Journal postings and accounting entries
- Fiscal positions and tax mappings
- Approval state and workflow transitions
- Tax reports and declarations

### Connector-owned

- Address normalization and validation
- Jurisdiction lookup and determination
- External rate table enrichment
- Exemption certificate verification

### Pulser-owned

- Tax exception review and explanation
- Exception routing and escalation
- Computation rationale generation
- Audit trace and evidence assembly
- Continuous accuracy monitoring

## MVP Architecture Boundary

### Odoo-owned (MVP truth)

- Invoices, vendor bills, expenses, and their tax lines
- Journal postings and accounting entries
- Fiscal positions and tax mappings
- Approval state and workflow transitions
- Tax reports and declarations

### Addon-owned (MVP behavior)

- Pre-posting tax validation flow
- Tax exception model and review state machine
- Explainability output (rationale, inputs, confidence, policy reference)
- PH BIR compliance pack (withholding, VAT, EWT)
- Audit trail for tax computation and review actions

### Optional bridge-owned (deferred / promotion lane)

- External address validation connector
- External jurisdiction lookup connector
- External rate enrichment connector
- Azure Document Intelligence for invoice OCR
- Foundry runtime for tax intelligence agents

### Deployment mode

- **MVP**: Odoo addons + lightweight pilot lane (no external engine required)
- **Promotion**: Connectors + governed runtime when enterprise scope demands it

## Current AI Resource Baseline

Resource:

- name: `ipai-copilot-resource`
- project: `ipai-copilot`
- region: `eastus2`

Endpoint families:

### Foundry project endpoint

`https://ipai-copilot-resource.services.ai.azure.com/api/projects/ipai-copilot`

Use for Foundry SDK, agents, evaluations, project-native capabilities.

### Azure OpenAI inference endpoint

`https://ipai-copilot-resource.openai.azure.com/openai/v1/`

Use for OpenAI SDK, chat completions, embeddings, deployment-scoped REST inference.

### AI Services endpoint

`https://ipai-copilot-resource.services.ai.azure.com/`

Use for bounded AI services/tool integrations; service-specific endpoints
where required (for example Document Intelligence, Language).

Use this existing resource as the default AI baseline for MVP unless a
missing capability is explicitly proven. Do not introduce a second
copilot/AI resource for MVP by default.

## AI-Assisted Tax Review Runtime

Where AI-assisted validation or exception explanation is used, the MVP
must reuse `ipai-copilot-resource`.

Use:

- Azure OpenAI inference endpoint for model inference (tax rationale
  generation, exception explanation, confidence scoring)
- AI Services endpoint only for bounded AI capabilities that support
  review, extraction, or orchestration (e.g., Document Intelligence)
- Foundry project endpoint only if agent hosting is explicitly required

Tax/accounting truth remains Odoo-owned. The Azure AI resource is an
intelligence surface, not a tax system of record.

## Azure Bridge Policy

Use Azure Document Intelligence for document extraction where applicable
(e.g., vendor invoice OCR feeding tax classification).

Use agent/runtime/search services only as bounded external intelligence
surfaces. Do not move accounting or tax truth out of Odoo.

Azure delivery follows the two-lane model from `spec/reverse-sap-concur/plan.md`:

- **Lane A** (pilot): targeted accelerator, ACA-hosted, Doc Intelligence bridge
- **Lane B** (governed): Foundry, AI Search, private networking, landing-zone controls

Start with Lane A for tax intelligence pilot. Promote to Lane B when
governance or enterprise data integration requirements emerge.

## Implementation Waves

### Wave 1 — Truth boundaries

1. Define Odoo-owned tax/accounting states (which models, which fields)
2. Define connector contract (input/output schema, auth, retry)
3. Define Pulser review objects (exception model, review state machine)
4. Map Odoo CE 18 native tax capabilities (`account.tax`, fiscal positions,
   withholding, tax groups, tax reports)

### Wave 2 — Connector and review flow

1. Map draft invoice/bill/expense validation flow
2. Build address/jurisdiction adapter (connector contract)
3. Build rate enrichment adapter (connector contract)
4. Define exception lifecycle (detection → review → resolution → audit)
5. Build Pulser review UI for tax exceptions
6. Wire `queue_job` for async connector calls

### Wave 3 — Local compliance packs

1. Define pack model (versioned, inheritable, overridable)
2. Build PH BIR pack (withholding tax, VAT, percentage tax, EWT)
3. Define evidence and withholding hooks
4. Define pack deployment and upgrade workflow
5. Wire `auditlog` for tax computation audit trail

### Wave 4 — Governed runtime

1. Define optional Foundry runtime/search integration
2. Define tracing/evaluation requirements
3. Define promotion path from pilot to governed deployment
4. Define continuous accuracy monitoring pipeline
5. Define tax reconciliation reporting

## Current Azure MVP Baseline

The MVP targets the existing Azure dev footprint and should prefer reuse over new infrastructure.

Current baseline includes:

- runtime RG: `rg-ipai-dev-odoo-runtime`
- data RG: `rg-ipai-dev-odoo-data`
- platform RG: `rg-ipai-dev-platform`
- network: `vnet-ipai-dev`
- WAF: `wafipaidev`
- PostgreSQL Flexible Server: `pg-ipai-odoo`
- Key Vault: `kv-ipai-dev`
- private endpoints / private DNS for Key Vault and PostgreSQL
- Log Analytics workspaces already provisioned
- Container Apps already provisioned in the runtime RG

MVP work must assume this footprint is the default target unless a missing capability is explicitly proven.

## SaaS / Multitenancy Guidance

Treat SaaS as the business model and multitenancy as an architecture decision.
Document:

- tenant definition
- shared vs isolated components
- control-plane responsibilities
- operational rollout strategy

### Promotion-lane SaaS controls

The following are promotion-lane capabilities unless explicitly required in MVP:

- deployment stamps
- advanced tenant isolation automation
- safe deployment rings
- feature flag operations
- live-site automation at scale

## Connector Runtime Boundary

Reverse AvaTax MVP must run against the current Odoo/Azure estate:

- Odoo remains tax/accounting truth
- PostgreSQL remains primary transactional data store
- Key Vault stores connector secrets/config
- runtime services should reuse the current Container App and private-network footprint

Do not introduce a separate tax platform backend or separate tax database as MVP baseline.

## Testing Strategy

Use Odoo-native backend testing as the default strategy.

Preferred layers:

- `TransactionCase` for business logic and model behavior
- `Form` for onchange/default/form-flow fidelity
- `HttpCase` for end-to-end web/tour flows only when the workflow truly requires browser coverage
- `@tagged(...)` and `--test-tags` for explicit execution control

Avoid UI-heavy testing unless there is a real operator path requiring
browser coverage.

## MCP Tooling Boundary

Allowed MCP tooling roles:

- Azure MCP Server for runtime/config validation
- Microsoft Learn MCP for platform/reference support
- Playwright MCP only for thin browser-critical flows
- Chrome DevTools MCP for debugging

Prohibited role: using MCP as the primary owner of workflow or business state.

Azure AI Foundry MCP is experimental and not part of the MVP critical path
by default.

## Review and Go-Live Inputs

### Azure review-checklists

Use Azure review-checklists as a structured architecture review input for:

- multitenancy
- WAF / perimeter controls
- AI landing zone
- cost
- application delivery/networking

Treat these as review aids, not architecture sign-off.

### Odoo 18 go-live checklist

Use the Odoo 18 community go-live checklist as a cutover/readiness input for:

- opening entries import
- inventory readiness
- receivable/payable balancing
- payment and reconciliation checks
- finance go-live validation

Treat this as an operational checklist seed that must be adapted to the
target localization and workflow.

## API Replacement Strategy

Do not replace Odoo/OCA 18 as the owner of business workflow or accounting truth.

Allowed replacement:

- replace only the external API edge with a thin FastAPI facade or sidecar

Odoo-owned:

- business objects
- approvals
- accounting/tax/expense state
- final write-path integrity

FastAPI-owned:

- external/mobile/public API surface
- connector/review facade
- orchestration endpoints
- async job handling
- webhook ingestion
- API auth/rate-limit/productization

Prohibited:

- direct writes from FastAPI to Odoo PostgreSQL tables
- duplicate business rules in FastAPI
- parallel transactional truth outside Odoo
- standalone tax ledger in FastAPI

## Azure API Edge Baseline

The default external API edge for mobile, public, partner, and async
workloads is a thin FastAPI layer on Azure Container Apps.

Preferred accelerator baseline:

- FastAPI Membership API Template for Azure Container Apps

Allowed responsibilities:

- external/mobile API surface
- exception/review/orchestration APIs
- webhook ingestion
- async orchestration
- bounded AI-assisted facade behavior
- optional edge-local cache/session/job state

Prohibited responsibilities:

- owning ERP transactional truth
- direct writes to Odoo PostgreSQL business tables
- duplicate approval/accounting/tax logic outside Odoo

## AI Template Baseline

Where AI companion surfaces are required, prefer lightweight Azure
AI/chat/agent templates and managed identity patterns. Do not make heavy
OCR/multimodal templates part of MVP unless extraction is explicitly
required.

## Foundry Project Baseline

Confirmed Foundry project baseline:

- project: `ipai-copilot`
- parent resource: `ipai-copilot-resource`
- resource group: `rg-data-intel-ph`
- region: `eastus2`
- project endpoint: `https://ipai-copilot-resource.services.ai.azure.com/api/projects/ipai-copilot`

## Connected Resources Strategy

The Foundry project uses attachable connections. Do not assume Azure AI Search,
Azure OpenAI, Cosmos DB, Storage, Application Insights, Bing grounding, or Fabric
are already attached unless explicitly verified.

For this bundle (AvaTax connector / tax intelligence), MVP connections:

- attach Azure OpenAI only where AI-assisted tax explanation or confidence scoring
  is explicitly required
- Azure AI Search is not required for the tax connector MVP — omit unless RAG over
  a compliance corpus is explicitly declared in scope
- Azure Document Intelligence is accessed via the AI Services endpoint, not a
  separate Foundry project connection
- keep Cosmos DB, Bing grounding, Fabric, and Serverless Model connections off the
  MVP critical path by default
- document every required project connection before implementation depends on it

## Anti-Patterns

Do not:

- Replace Odoo's `account.tax` engine with external computation
- Store tax truth outside Odoo (no parallel tax ledger)
- Embed connector logic inside accounting modules
- Let Pulser directly post tax entries without approval workflow
- Treat jurisdiction data as static (must be refreshable via connector)
- Select the full production accelerator as the initial baseline for
  a narrowly scoped tax intelligence pilot
