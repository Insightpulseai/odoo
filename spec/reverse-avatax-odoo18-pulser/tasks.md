# Tasks — Reverse AvaTax for Odoo 18 Pulser

## MVP Wave 1 — Truth Boundaries

- [x] Define Odoo-owned tax/accounting states (`account.tax`, `account.fiscal.position`, tax groups, tax reports)
- [x] Define connector contract schema (address validation, jurisdiction lookup, rate enrichment, exemption verification)
- [x] Define Pulser review objects (tax exception model, review state machine, evidence assembly)
- [x] Map Odoo CE 18 native tax capabilities and identify proven vs candidate coverage
- [ ] Map Odoo CE 18 withholding tax support (native + OCA)
- [ ] Confirm OCA `account_tax_balance` as baseline tax reporting surface

## MVP Wave 2 — Validation and Review Flow

- [x] Map draft invoice/bill/expense pre-posting tax validation flow
- [ ] Build address/jurisdiction adapter contract
- [ ] Build rate enrichment adapter contract
- [x] Define exception lifecycle (detection, review, resolution, audit)
- [x] Build Pulser review UI for tax exceptions (form/tree views)
- [ ] Wire `queue_job` for async connector calls
- [x] Define confidence thresholds for auto-accept vs human-review routing
- [x] Build explainability output (rationale, source inputs, confidence, policy reference)

## MVP Wave 3 — Local Compliance Packs

- [x] Define pack model (versioned, inheritable, overridable per company/country)
- [x] Build PH BIR pack (withholding tax tables, VAT rules, percentage tax, EWT rates)
- [ ] Define evidence hooks (receipt requirements, withholding certificates)
- [ ] Define pack deployment and upgrade workflow
- [x] Wire `auditlog` for tax computation audit trail
- [ ] Define inheritance/override semantics for multi-entity scenarios

## Deferred Wave 4 — Governed Runtime (Post-MVP)

- [ ] Classify target deployment as Lane A (pilot) or Lane B (governed production)
- [ ] Define optional Foundry runtime/search integration
- [ ] Define tracing/evaluation requirements for tax computation pipeline
- [ ] Define promotion path from pilot to governed deployment
- [ ] Define continuous accuracy monitoring pipeline (rate drift, jurisdiction changes)
- [ ] Define tax reconciliation reporting (computed vs posted vs declared)

## Wave — Review and Go-Live Readiness

- [ ] Map MVP architecture against relevant Azure review-checklists domains
- [ ] Record any promotion-lane findings for multitenancy, WAF, AI, cost, and networking
- [ ] Derive a finance go-live checklist from the Odoo 18 checklist
- [ ] Adapt the Odoo checklist for target localization and actual enabled modules
- [ ] Validate opening entries, receivable/payable balances, inventory setup, and payment/reconciliation readiness before go-live
- [ ] Keep review findings and go-live checks as validation artifacts, not as replacements for feature specs

## Wave — SaaS Architecture Normalization

- [ ] Define tenant meaning for this feature
- [ ] Define shared vs isolated components
- [ ] Define control-plane responsibilities
- [ ] Confirm MVP is a viable horizontal slice
- [ ] Mark deployment stamps / advanced rollout / feature-flag operations as promotion-lane unless explicitly required now

## Wave — Foundry Project Connection Validation

- [ ] Confirm current connected resources on `ipai-copilot`
- [ ] Record only actually attached project connections as baseline dependencies
- [ ] Add Azure OpenAI connection only where AI inference is required
- [ ] Add Azure AI Search only where RAG/grounding is explicitly required
- [ ] Keep Cosmos DB / Fabric / Bing grounding off MVP critical path unless justified
- [ ] Document every new Foundry project connection before implementation depends on it

## Wave — Existing Azure Footprint Alignment

- [ ] Map MVP runtime surfaces to existing resources in `rg-ipai-dev-odoo-runtime`
- [ ] Confirm Odoo / app services reuse `pg-ipai-odoo` and existing private endpoint topology
- [ ] Store all runtime secrets/config in `kv-ipai-dev`
- [ ] Reuse existing Log Analytics workspaces for MVP observability
- [ ] Reuse existing WAF / network boundary for exposed surfaces
- [ ] Explicitly document any missing resource before proposing new Azure infrastructure

## Wave — Azure AI Baseline Alignment

- [ ] Bind MVP AI-assisted behaviors to existing `ipai-copilot-resource`
- [ ] Record authoritative endpoints for Foundry, Azure OpenAI, and AI Services in the plan
- [ ] Use Azure OpenAI endpoint for deployment-scoped inference calls
- [ ] Use Foundry / AI Services endpoint only for capabilities that require those surfaces
- [ ] Verify no duplicate AI/copilot resource is introduced for MVP
- [ ] Keep Odoo as workflow/accounting truth even when Azure AI assists

## Wave — Odoo-Native Test Coverage

- [x] Add `TransactionCase` tests for pre-posting tax validation flow
- [x] Add `TransactionCase` tests for tax exception model and review state machine
- [x] Add `TransactionCase` tests for PH BIR compliance pack (withholding/VAT/EWT)
- [ ] Add `Form` tests for tax exception review and resolution entry
- [ ] Add `HttpCase` only for browser-critical tax review operator paths
- [x] Tag all tests with `@tagged('tax', 'avatax')` for explicit execution control

## Wave — Browser-Critical End-to-End Coverage

- [ ] Identify browser-critical tax review flows requiring Playwright
- [ ] Add Playwright tests for identified critical flows only
- [ ] Capture traces for browser-critical test failures

## Wave — Debugging and Triage Support

- [ ] Use Chrome DevTools for tax review UI debugging
- [ ] Do not treat DevTools as an automated test framework

## Wave — Optional MCP Tooling Enablement

- [ ] Identify which MCP servers are useful for tax intelligence development
- [ ] Enable Azure MCP Server for runtime/config validation
- [ ] Enable Microsoft Learn MCP for Azure/tax platform reference
- [ ] Keep Azure AI Foundry MCP off MVP critical path unless explicitly justified

## Wave — API Edge Strategy

- [ ] Identify which endpoints must stay Odoo-native
- [ ] Identify which external/mobile/agent endpoints can be exposed through FastAPI
- [ ] Ensure FastAPI write paths go through Odoo-owned services/controllers, not direct DB writes
- [ ] Keep accounting/approval/tax logic in Odoo
- [ ] Use FastAPI only for edge concerns, orchestration, and async workloads

## Wave — Azure API Edge Selection

- [ ] Use FastAPI ACA template as the default edge baseline for connector/review facade
- [ ] Keep Odoo as write-path owner for tax/accounting business objects
- [ ] Define which endpoints remain Odoo-native
- [ ] Define which endpoints are exposed through FastAPI facade
- [ ] Prevent direct FastAPI writes to Odoo business tables
- [ ] Use managed identity for Azure AI access where AI assistance is in scope
- [ ] Keep OCR/multimodal templates out of MVP unless explicitly required

## Release Gates

- [x] No tax truth stored outside Odoo
- [x] Connectors are swappable adapters with defined contracts
- [x] Every Pulser tax action includes rationale, inputs, confidence, audit trace
- [x] PH BIR pack tested with withholding/VAT/EWT scenarios
- [x] No direct posting from external systems (draft-first always)
- [ ] Known gaps documented in SSOT parity matrix
