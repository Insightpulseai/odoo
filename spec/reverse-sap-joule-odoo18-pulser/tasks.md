# Tasks — Reverse SAP Joule for Odoo 18 Pulser

## MVP Wave 1 — Assistant Contract

- [x] Define transactional / navigational / informational behavior taxonomy — `pulser.intent` model (pulser_intent.py)
- [x] Define action classes: advisory / approval-gated / auto-routable — `pulser.action.class` model (pulser_action_class.py)
- [x] Define action gate configuration model (per company/role/domain) — `pulser.action.class` + security groups; per-company scope is promotion-lane
- [ ] Build copilot shell with intent detection — DEFERRED: FastAPI/OWL shell layer, not addon data model
- [x] Build Odoo RPC tool bindings (read-only: projects, expenses, invoices, employees) — `pulser.tool.binding` model with model_name/method_name/is_read_only fields
- [x] Implement interaction tracing (intent, routing, tools, result, latency) — `pulser.interaction` + `pulser.action.log` models (duration_ms, tools_invoked, session_id)
- [x] Define explanation template (rationale, inputs, confidence, policy reference) — fields on `pulser.action.log`: rationale, inputs_summary, confidence, policy_reference

## MVP Wave 2 — Agent Routing

- [x] Define intent router (classify user intent, select domain agent) — `pulser.domain.agent.domain` key + `supported_intent_ids` M2M enables routing contract
- [x] Define domain-agent contract (tool bindings, security context, explanation template) — `pulser.domain.agent` with security_group_id + tool_binding_ids
- [x] Build Expense Agent (query expense status, submit reports, liquidation review) — domain agent record scaffold: models support `domain='expense'` agents with hr.expense tool bindings
- [x] Build Project Agent (query project status, budget, tasks, timeline) — domain agent record scaffold: models support `domain='project'` agents with project.project tool bindings
- [x] Define tool-binding boundaries per domain agent — `pulser.tool.binding` per agent with model_name, method_name, action_class_id, is_read_only, domain_filter
- [x] Implement action gate evaluation pipeline — `pulser.action.class` + `requires_approval` computed field + validation constraints enforce gate contract
- [x] Wire domain agents to Odoo security groups (inherit user permissions) — `security_group_id` on `pulser.domain.agent` + record rules in pulser_security.xml

## MVP Wave 3 — Grounding and Knowledge

- [ ] Define RAG-only knowledge sources (company policies, SOPs, Odoo documentation)
- [ ] Define live-state retrieval from Odoo (direct RPC, never cached index)
- [ ] Define citation/evidence behavior (link to source Odoo record or document)
- [ ] Evaluate Azure AI Search for policy corpus indexing
- [ ] Build knowledge grounding pipeline (if governed mode selected)
- [ ] Define boundaries: knowledge grounding supplements, never replaces, live state

## Deferred Wave 4 — Runtime Promotion (Post-MVP)

- [ ] Define pilot runtime baseline (ACA shell, bounded tools, App Insights tracing)
- [ ] Define governed runtime requirements (Foundry Agent Service, managed identity, search)
- [ ] Define tracing, evaluation, and observability gates
- [ ] Define promotion criteria (agent count, action volume, compliance, networking)
- [ ] Build promotion automation (pilot to governed)
- [ ] Define rollback path (governed to pilot)

## Deferred — Domain Agent Expansion (Post-MVP)

- [ ] Build HR Agent (leave requests, attendance, employee info)
- [ ] Build Tax Agent (tax computation review, withholding, compliance)
- [ ] Build Accounting Agent (invoice status, payment, reconciliation)
- [ ] Build Admin Agent (settings, users, module configuration)

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

- [x] Add `TransactionCase` tests for intent classification (informational/navigational/transactional) — tests/test_intent.py (9 tests)
- [x] Add `TransactionCase` tests for action gate evaluation (advisory/approval-gated/auto-routable) — tests/test_action_class.py (12 tests)
- [x] Add `TransactionCase` tests for domain-agent routing contract — tests/test_domain_agent.py (14 tests)
- [ ] Add `Form` tests for Pulser review/approval form flows — DEFERRED: requires live Odoo environment with module installed
- [ ] Add `HttpCase` only for copilot shell browser interactions requiring tour coverage — DEFERRED: no shell UI yet
- [x] Tag all tests with `@tagged('pulser', 'joule')` for explicit execution control — all test files tagged `@tagged('pulser', 'joule', 'post_install', '-at_install')`

## Wave — Browser-Critical End-to-End Coverage

- [ ] Identify browser-critical Pulser shell UI flows requiring Playwright
- [ ] Add Playwright tests for copilot shell chat interface interactions
- [ ] Add Playwright tests for action preview and confirmation flows
- [ ] Capture traces for browser-critical test failures

## Wave — Debugging and Triage Support

- [ ] Use Chrome DevTools for copilot shell runtime debugging
- [ ] Use Chrome DevTools for agent response/network inspection
- [ ] Do not treat DevTools as an automated test framework

## Wave — Optional MCP Tooling Enablement

- [ ] Identify which MCP servers are useful for Pulser development
- [ ] Enable Playwright MCP for copilot shell browser automation
- [ ] Enable Azure MCP Server for runtime/config validation
- [ ] Enable Microsoft Learn MCP for Foundry/platform reference
- [ ] Keep Azure AI Foundry MCP off MVP critical path unless explicitly justified

## Wave — API Edge Strategy

- [ ] Identify which endpoints must stay Odoo-native
- [ ] Identify which external/mobile/agent endpoints can be exposed through FastAPI
- [ ] Ensure FastAPI write paths go through Odoo-owned services/controllers, not direct DB writes
- [ ] Keep accounting/approval/tax logic in Odoo
- [ ] Use FastAPI only for edge concerns, orchestration, and async workloads

## Wave — Azure API Edge Selection

- [ ] Use FastAPI ACA template as the default edge baseline for assistant shell and agent-facing APIs
- [ ] Use AI chat/agent templates for Pulser experimentation and shell baseline
- [ ] Keep Odoo as write-path owner for ERP business objects
- [ ] Define which endpoints remain Odoo-native
- [ ] Define which endpoints are exposed through FastAPI facade
- [ ] Prevent direct FastAPI writes to Odoo business tables
- [ ] Use managed identity for Azure AI/OpenAI access
- [ ] Keep OCR/multimodal templates out of MVP unless explicitly required

## Release Gates

- [ ] All transactional actions classified (advisory / approval-gated / auto-routable)
- [ ] Zero unclassified transactional actions in test suite
- [ ] Domain agents respect Odoo security groups and record rules
- [ ] Every Pulser action emits rationale, inputs, confidence, audit trace
- [ ] Knowledge grounding does not replace live Odoo state queries
- [ ] Copilot shell works in pilot mode without Foundry/Search dependencies
- [ ] Tracing pipeline operational with interaction-level telemetry
