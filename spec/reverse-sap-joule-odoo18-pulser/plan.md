# Plan — Reverse SAP Joule for Odoo 18 Pulser

## Runtime Split

### Copilot/UI layer

- Conversational shell (chat interface)
- Navigational guidance (Odoo menu/view routing)
- Informational responses (live Odoo data queries)
- Action previews (show what will happen before execution)

### Agent/runtime layer

- Intent routing (informational / navigational / transactional)
- Domain-agent orchestration (select and invoke domain agent)
- Tool invocation (Odoo RPC calls with security context)
- Action gate evaluation (advisory / approval-gated / auto-routable)
- Tracing and evaluation (per-interaction telemetry)
- Managed runtime where selected (Foundry Agent Service)

### Odoo layer

- Record access (model queries with user's security context)
- Permissions (security groups, record rules, field-level access)
- Workflow transitions (approval, posting, state changes)
- Transactional truth (accounting, HR, project, expense)

## Deployment Modes

### Pilot mode

- Lightweight agent shell on Azure Container Apps
- Bounded tool set (read-only + limited approval-gated actions)
- Direct Odoo RPC for data access
- Application Insights for tracing
- No AI Search, no Foundry Agent Service, no private networking

### Governed mode

- Foundry Agent Service for managed agent runtime
- Managed identities for all service-to-service auth
- Azure AI Search for knowledge grounding (policies, SOPs)
- Full tracing and evaluation pipeline
- Private networking where required
- Landing-zone controls

### Promotion criteria (pilot to governed)

- Domain agent count exceeds 3
- Transactional action volume requires managed runtime
- Enterprise compliance mandates private networking
- Knowledge grounding requires indexed search over policy corpus
- Tracing/evaluation requirements exceed Application Insights baseline

## MVP Architecture Boundary

### Odoo-owned (MVP truth)

- All record state (invoices, expenses, projects, employees)
- Approval workflow transitions
- Permission and security group enforcement
- Accounting posting truth
- Audit trail for business actions

### Pulser-owned (MVP behavior)

- Copilot shell with tri-modal intent detection
- Domain-agent routing (Expense + Project agents)
- Action gate evaluation (advisory / approval-gated / auto-routable)
- Explanation generation and audit logging
- Interaction tracing

### Optional bridge-owned (deferred / promotion lane)

- Azure AI Search for policy corpus indexing
- Foundry Agent Service for managed runtime
- Full domain agent expansion
- Proactive background operations

### Deployment mode

- **MVP**: Lightweight pilot lane (ACA shell, bounded tools, App Insights)
- **Promotion**: Governed lane (Foundry Agent Service, managed identity, search, private networking)

## Architecture Boundaries

### Pulser may

- Query Odoo models using authenticated RPC
- Propose actions with classification and rationale
- Execute auto-routable actions with audit logging
- Present approval-gated actions for human confirmation
- Retrieve knowledge from indexed policy/SOP sources

### Pulser must not

- Bypass Odoo security groups or record rules
- Directly write to Odoo database (must use ORM/RPC)
- Execute unclassified transactional actions
- Store operational state outside Odoo
- Replace live Odoo data with cached search index results

## Implementation Waves

### Wave 1 — Assistant contract

1. Define tri-modal behavior (informational, navigational, transactional)
2. Define action classes (advisory, approval-gated, auto-routable)
3. Build copilot shell with intent detection
4. Build Odoo RPC tool bindings (read-only)
5. Implement tracing for all interactions

### Wave 2 — Agent routing

1. Define intent router (classify and route to domain agent)
2. Define domain-agent contract (tools, security context, explanation template)
3. Build first domain agents (Expense Agent, Project Agent)
4. Define tool-binding boundaries per domain
5. Implement action gate evaluation

### Wave 3 — Grounding and knowledge

1. Define RAG-only knowledge sources (policies, SOPs, documentation)
2. Define live-state retrieval from Odoo (never cache as truth)
3. Define citation/evidence behavior (link to source record/document)
4. Wire Azure AI Search for policy corpus (if governed mode)
5. Build knowledge grounding pipeline

### Wave 4 — Runtime promotion

1. Define pilot runtime baseline (ACA, bounded tools, App Insights)
2. Define governed runtime requirements (Foundry, managed identity, search)
3. Define tracing, evaluation, and observability gates
4. Build promotion automation (pilot → governed)
5. Define rollback path (governed → pilot if needed)

## Current AI Resource Baseline

Resource:

- name: `ipai-copilot-resource`
- project: `ipai-copilot`
- region: `eastus2`

Endpoint families:

### Foundry project endpoint

`https://ipai-copilot-resource.services.ai.azure.com/api/projects/ipai-copilot`

Use for:

- Foundry SDK
- agents
- evaluations
- project-native capabilities

### Azure OpenAI inference endpoint

`https://ipai-copilot-resource.openai.azure.com/openai/v1/`

Use for:

- OpenAI SDK
- chat completions
- embeddings
- audio/image inference
- deployment-scoped REST inference

### AI Services endpoint

`https://ipai-copilot-resource.services.ai.azure.com/`

Use for:

- bounded AI services/tool integrations as exposed by this Foundry resource
- service-specific endpoints where required (for example Speech / Translator)

Use this existing resource as the default AI baseline for MVP unless a
missing capability is explicitly proven. Do not introduce a second
copilot/AI resource for MVP by default.

## Runtime Binding

Pulser Assistant MVP binds to the existing `ipai-copilot-resource` baseline.

Use:

- Foundry project endpoint for agent/project capabilities, evaluations, and
  managed runtime features where selected
- Azure OpenAI endpoint for deployment-scoped inference calls
- AI Services endpoint for non-OpenAI AI services when needed

Pulser business logic must remain Odoo-first even when the runtime uses
this Azure AI resource.

## Endpoint Discipline

Do not treat `ipai-copilot-resource` as a single generic endpoint.

Use the correct surface by capability:

- Foundry project operations:
  `https://ipai-copilot-resource.services.ai.azure.com/api/projects/ipai-copilot`

- Azure OpenAI inference:
  `https://ipai-copilot-resource.openai.azure.com/openai/v1/`
  or deployment-scoped REST under:
  `https://ipai-copilot-resource.openai.azure.com/openai/deployments/<deployment-id>/...`

- AI Services / tools:
  use the resource's AI Services / tool-specific endpoint surface as
  appropriate for Document Intelligence, Language, Speech, Translation,
  or related services

MVP must reuse this existing resource and choose the endpoint family
based on workload, not convenience.

## Azure Bridge Policy

Use Azure services as the intelligence and runtime substrate:

- AI Foundry for model hosting
- AI Search for knowledge grounding (governed mode only)
- Document Intelligence for document extraction (where applicable)
- Container Apps for copilot shell and agent runtime (pilot mode)

Do not move Odoo operational truth into Azure services. Odoo remains the
system of record for all business state.

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

## Runtime Target

Pulser Assistant MVP targets the existing Azure runtime estate.

Preferred baseline:

- existing Container App surfaces in `rg-ipai-dev-odoo-runtime`
- existing Key Vault and private networking
- existing Log Analytics for observability

Heavy governed runtime remains a promotion lane.
Do not require new Foundry-heavy infrastructure for MVP if the assistant shell, routing, and auditability can run on the current dev footprint.

## Promotion Lane

Use Foundry Agent Service or broader governed AI runtime only when the MVP shell is proven and a managed-agent runtime is explicitly required.

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

## Testing Strategy

Use Odoo-native backend testing as the default strategy.

Preferred layers:

- `TransactionCase` for business logic and model behavior
- `Form` for onchange/default/form-flow fidelity
- `HttpCase` for end-to-end web/tour flows only when the workflow truly requires browser coverage
- `@tagged(...)` and `--test-tags` for explicit execution control

Use Playwright only for critical assistant shell UI flows that need
cross-browser verification or end-to-end validation.

Use Chrome DevTools for shell/runtime debugging and triage.

## MCP Tooling Boundary

Allowed MCP tooling roles:

- Playwright MCP for browser automation
- Chrome DevTools MCP for debugging
- Azure MCP Server for platform/runtime validation
- Microsoft Learn MCP for trusted Microsoft documentation lookup
- Azure DevOps MCP only if work-item sync is explicitly in scope

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
- orchestration endpoints
- async job handling
- webhook ingestion
- API auth/rate-limit/productization

Prohibited:

- direct writes from FastAPI to Odoo PostgreSQL tables
- duplicate business rules in FastAPI
- parallel transactional truth outside Odoo

## Azure API Edge Baseline

The default external API edge for mobile, public, partner, and async
workloads is a thin FastAPI layer on Azure Container Apps.

Preferred accelerator baseline:

- FastAPI Membership API Template for Azure Container Apps

Allowed responsibilities:

- external/mobile API surface
- assistant shell / agent-facing API surface
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
AI/chat/agent templates and managed identity patterns:

- Get started with AI agents
- Get Started with Chat
- Build Your Own Copilot Solution Accelerator
- Securely authenticate and access your GenAI app with managed identity

Do not make heavy OCR/multimodal templates part of MVP unless extraction
is explicitly required.

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

For this bundle (Pulser assistant / agent runtime), MVP connections:

- attach Azure OpenAI where assistant inference or agent reasoning is required
- attach Application Insights for tracing when App Insights is the observability target
- attach Azure AI Search only when knowledge grounding over a policy/SOP corpus is
  explicitly required (governed mode, not pilot mode)
- keep Cosmos DB, Bing grounding, Fabric, and Serverless Model connections off the
  MVP critical path by default
- document every required project connection before implementation depends on it

## Anti-Patterns

Do not:

- Embed AI logic directly in Odoo Python models
- Let agents bypass Odoo approval workflows
- Cache Odoo state in a search index and serve it as truth
- Build a general-purpose chatbot without domain-agent structure
- Skip action gate classification for transactional operations
- Select governed runtime for pilot-scope deployments
