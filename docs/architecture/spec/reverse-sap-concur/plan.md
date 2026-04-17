# Implementation Plan — Reverse SAP Concur on Odoo 18

## 1. Strategy

Productize and augment Odoo CE 18 Finance as a unified spend control plane.

**Not**: build a greenfield autonomous spend OS.
**Instead**: compose CE + OCA + Azure bridges + thin IPAI delta.

Odoo already covers more of the Concur core than the reverse PRD originally
made explicit. The expense, accounting, budgets, analytic accounting,
withholding taxes, bank sync/reconciliation, and multi-currency surfaces
are native. The work is augmentation, not invention.

## 2. Capability Allocation

### CE-native (install and configure)

- Expense submission/reporting/reimbursement
- Accounting posting
- Analytic distribution
- Budgets / analytic accounting
- Withholding tax support
- Bank sync / reconciliation
- Receipt attachment / upload / email ingestion
- Multi-currency / multi-company

### OCA-native / composable (install and wire)

- Cash advance / clearing lifecycle
- Multi-tier approval routing
- Payment management and sequencing
- AI bridge modules (OCA `ai_oca_bridge*`)
- Document archival (`dms`, `dms_field`)
- Audit trails (`auditlog`)
- Async processing (`queue_job`)
- Budget reporting (`mis_builder`)
- Document/approval surfaces (`document_page_approval`)

### External bridge (build adapter)

- Azure Document Intelligence for OCR / classification / extraction
- Confidence-scored outputs feeding Odoo review queues

### Thin IPAI delta (keep / extend)

- PH liquidation lifecycle (`ipai_hr_expense_liquidation`)
- PH compliance/BIR (`ipai_expense_ops`)
- Country compliance packs (future `ipai_expense_<country>`)
- Card feed adapter (future, if bank statement import insufficient)

## 3. Workstreams

### Workstream 1 — CE Finance Baseline Mapping

1. Map Odoo CE 18 expense/accounting native coverage to SAP Concur capability families
2. Document proven vs declared coverage
3. Identify configuration needed to activate native capabilities

### Workstream 2 — OCA Composition Wiring

1. Inventory required OCA bridge/composition modules
2. Wire expense-adjacent OCA modules (DMS, audit, queue, MIS)
3. Evaluate OCA AI bridge modules for expense AI ingress
4. Verify per-module maturity on 18.0

### Workstream 3 — Azure Document Intelligence Bridge

1. Define adapter contract for receipt/invoice ingestion
2. Define confidence thresholds and human-review routing
3. Wire `queue_job` as async orchestration substrate
4. Build `ipai_document_intelligence` expense adapter

### Workstream 4 — AI Bridge Contract

1. Define AI bridge prompt/payload contract using OCA bridge pattern
2. Define which actions are advisory vs blocking vs auto-routable
3. Keep posting/reimbursement/accounting transitions inside Odoo workflow
4. Build explainability and audit logging for AI actions

### Workstream 5 — Policy Engine

1. Design policy-as-code model extending Odoo approval controls
2. Build PH country pack (BIR, receipt rules, liquidation policies)
3. Define country pack versioning and deployment model
4. Wire policy evaluation into pre-submit, submit, and post-payment stages

### Workstream 6 — Card and AP Convergence

1. Evaluate bank statement import surfaces for card feed composition
2. Define virtual card integration pattern
3. Design AP/invoice convergence on same spend graph
4. Define merchant/category control model

## 4. Azure Implementation Lanes

### Lane A — Expense intelligence pilot

- Targeted Azure accelerator/template
- Azure Container Apps-hosted review/agent surface
- Azure Document Intelligence bridge for receipt extraction
- Managed identity for model access
- Minimal search/index layer only if needed
- No Fabric, Purview, or landing-zone submodule wiring

### Lane B — Governed production platform

- Microsoft "Deploy Your AI Application In Production" accelerator
- `azd`-driven environment provisioning
- AI Landing Zone-aligned topology
- Azure AI Foundry + Azure AI Search
- Optional Fabric / Purview (disabled unless prerequisites exist)
- Private networking
- Managed identities with landing-zone controls
- Post-deployment validation flow

### Recommendation

For reverse-SAP-Concur expense delivery:

- Start with Lane A for OCR/review/policy-assist flows
- Promote to Lane B only when governance, private networking, or wider
  enterprise data integration become required

### Promotion criteria (Lane A to Lane B)

- Workload requires private networking or VNet integration
- Workload requires Azure AI Search for policy/evidence retrieval
- Workload requires Foundry-centered agent hosting
- Enterprise compliance mandates landing-zone controls
- Data foundation scope expands beyond expense domain

## 5. MVP Architecture Boundary

### Odoo-owned (MVP truth)

- Expense lifecycle and workflow state
- Cash advance request / approval / release state
- Liquidation state and settlement computation
- Accounting posting truth
- Approval routing and permissions
- Document attachments

### Addon-owned (MVP behavior)

- TBWA cash advance request form fields and workflow
- TBWA itemized expense / liquidation form fields and workflow
- Settlement totals and balance logic
- Printable QWeb report templates
- Cash advance monitoring views and queues

### Mobile companion (MVP surface)

- Read-only and limited-action companion
- Reads/writes only through Odoo-owned workflows
- Not a separate workflow engine or system of record

### Optional bridge-owned (deferred / promotion lane)

- OCR extraction (Azure Document Intelligence)
- AI review assistance (OCA bridge + Foundry)
- Corporate card feeds
- External tax enrichment
- Governed Azure runtime

## 6. Current AI Resource Baseline

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
where required (for example Document Intelligence, Speech).

Use this existing resource as the default AI baseline for MVP unless a
missing capability is explicitly proven. Do not introduce a second
copilot/AI resource for MVP by default.

## 7. Mobile Companion / AI Boundary

If the mobile companion or cash-advance monitoring features require AI
assistance, they must reuse `ipai-copilot-resource`.

Allowed uses:

- Reminder generation
- Status summarization
- Bounded assistant responses
- Optional extraction/review support

Not allowed:

- Parallel workflow truth
- Separate approval logic
- Independent accounting state

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

For this bundle (SAP Concur / mobile companion), MVP connections:

- attach Azure OpenAI only where the mobile companion or bounded assistant requires
  inference (reminders, status summarization, bounded responses)
- Azure AI Search is not required for the expense MVP — omit unless policy retrieval
  or evidence grounding is explicitly declared in scope
- Azure Document Intelligence is accessed via the AI Services endpoint, not a
  separate Foundry project connection
- keep Cosmos DB, Bing grounding, Fabric, and Serverless Model connections off the
  MVP critical path by default
- document every required project connection before implementation depends on it

## 8. Anti-Patterns

Do not:

- Put OCR logic inside accounting/expense modules
- Let AI directly mutate posted accounting state without explicit workflow gates
- Treat OCA AI as the source of truth for spend decisions
- Rebuild native Odoo expense/report/reimbursement flows as custom modules
- Embed opaque AI logic deep inside expense/accounting models
- Select the full production accelerator as the initial baseline for a
  narrowly scoped expense intelligence feature set

## 9. Current Azure MVP Baseline

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

## 10. MVP Deployment Mode

The Reverse SAP Concur MVP must deploy onto the existing Azure dev runtime footprint.

Use existing components first:

- existing Container Apps in `rg-ipai-dev-odoo-runtime`
- existing PostgreSQL in `rg-ipai-dev-odoo-data`
- existing Key Vault in `rg-ipai-dev-platform`
- existing VNet / private endpoint topology
- existing Front Door WAF policy

Do not introduce a new standalone expense platform, new landing zone, or parallel workflow service for MVP.
The mobile companion is a subordinate surface over Odoo-owned workflows and may reuse existing runtime/container surfaces.

## 11. SaaS / Multitenancy Guidance

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

## 12. Infrastructure Non-Goals

MVP does not require:

- a new Azure landing zone
- a separate database for cash advance / liquidation truth
- a separate mobile backend with independent workflow ownership
- mandatory AI Search / Fabric / Purview
- new governance-heavy runtime unless explicitly required later

## 13. Testing Strategy

Use Odoo-native backend testing as the default strategy.

Preferred layers:

- `TransactionCase` for business logic and model behavior
- `Form` for onchange/default/form-flow fidelity
- `HttpCase` for end-to-end web/tour flows only when the workflow truly requires browser coverage
- `@tagged(...)` and `--test-tags` for explicit execution control

Use Playwright only for browser-critical flows that need cross-browser
verification, end-to-end UI validation, or companion/mobile shell testing.

Use Chrome DevTools for DOM/CSS inspection, console/network debugging,
and runtime triage. Do not rely on ad hoc scripts or manual QA as the
primary correctness gate.

## 14. MCP Tooling Boundary

Allowed MCP tooling roles:

- Playwright MCP for browser automation
- Chrome DevTools MCP for debugging
- Azure MCP Server for platform/runtime validation
- Microsoft Learn MCP for trusted Microsoft documentation lookup
- Azure DevOps MCP only if work-item sync is explicitly in scope

Prohibited role: using MCP as the primary owner of workflow or business state.

Azure AI Foundry MCP is experimental and not part of the MVP critical path
by default.

## 15. Review and Go-Live Inputs

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

## 14. API Replacement Strategy

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

## 15. Azure API Edge Baseline

The default external API edge for mobile, public, partner, and async
workloads is a thin FastAPI layer on Azure Container Apps.

Preferred accelerator baseline:

- FastAPI Membership API Template for Azure Container Apps

Allowed responsibilities:

- external/mobile API surface (mobile companion, cash advance monitoring)
- webhook ingestion
- async orchestration
- notifications/reminders
- bounded AI-assisted facade behavior
- optional edge-local cache/session/job state

Prohibited responsibilities:

- owning ERP transactional truth
- direct writes to Odoo PostgreSQL business tables
- duplicate approval/accounting/tax logic outside Odoo

## 16. AI Template Baseline

Where AI companion surfaces are required, prefer lightweight Azure
AI/chat/agent templates and managed identity patterns. Do not make heavy
OCR/multimodal templates part of MVP unless extraction is explicitly
required.

## 17. Proof Gates

### Phase 1 gate

- CE expense baseline proven functional
- OCA expense modules wired and tested
- Azure Document Intelligence adapter passing receipts into Odoo
- AI bridge pattern demonstrated with audit logging

### Phase 2 gate

- Card feed ingestion working via bank statement or dedicated adapter
- Pre-spend budget checks operational
- Policy-as-code engine evaluating rules at submission time

### Phase 3 gate

- PH country pack deployed and tested
- Continuous audit scoring operational
- Recovery/remediation workflows demonstrated

### Phase 4 gate

- AP/invoice convergence on same spend graph
- Operator console functional
- Success metrics measurable
