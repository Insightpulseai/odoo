# Tasks — Reverse SAP Concur on Odoo 18

## MVP Wave 0 — Baseline Mapping

- [x] Map Odoo CE 18 expense/accounting native coverage to SAP Concur capability families
- [x] Inventory required OCA bridge/composition modules
- [ ] Verify OCA AI bridge modules (`ai_oca_bridge*`) on 18.0 branch
- [x] Document proven vs declared vs candidate coverage matrix
- [x] Confirm existing custom delta modules (`ipai_hr_expense_liquidation`, `ipai_expense_ops`) as justified

## MVP Wave 1 — Cash Advance + Liquidation + Monitoring

- [ ] Configure CE expense baseline (categories, analytic, budgets, withholding)
- [ ] Wire OCA expense modules (advance clearing, tier validation, payment, sequence)
- [ ] Define Azure Document Intelligence adapter contract for receipt/invoice ingestion
- [ ] Define confidence thresholds and human-review routing for OCR outputs
- [ ] Build `ipai_document_intelligence` expense adapter with `queue_job` orchestration
- [ ] Define AI bridge prompt/payload contract using OCA bridge pattern
- [ ] Define which actions are advisory vs blocking vs auto-routable
- [x] Keep posting/reimbursement/accounting transitions inside Odoo-owned workflow state
- [ ] Wire `dms_field` for receipt archival on expense reports
- [ ] Wire `auditlog` rules for expense sheet and cash advance models
- [ ] Build explainability and audit logging for AI actions
- [x] Add form/tree/kanban views for spend case workflow

## MVP Wave 2 — Mobile Companion

- [ ] Define mobile companion as read/limited-action surface subordinate to Odoo workflows
- [ ] Build mobile views for request status, approval status, advance monitoring
- [ ] Build mobile liquidation reminder notifications
- [ ] Ensure mobile companion reads/writes only through Odoo-owned workflows
- [ ] Verify mobile companion does not introduce parallel workflow state

## MVP Wave 3 — Printable Outputs and Audit

- [x] Implement QWeb report for cash advance request form
- [x] Implement QWeb report for itemized expense / liquidation form
- [x] Verify printed output preserves operational field order and finance signoff blocks
- [ ] Wire `auditlog` rules for cash advance and liquidation models

## Deferred — Card and Request Control Plane (Post-MVP)

- [ ] Evaluate `account_bank_statement_import` + OCA statement modules for card feeds
- [ ] Define virtual card integration pattern
- [ ] Build pre-spend budget checks using Odoo analytic + `mis_builder`
- [ ] Build merchant/category control model
- [ ] Wire card-to-trip and card-to-request linkage
- [ ] Build budget envelope model on Odoo analytic accounts

## Deferred — Audit and Local Compliance (Post-MVP)

- [ ] Design policy-as-code model extending Odoo approval controls
- [ ] Build PH country pack (BIR, receipt rules, liquidation policies, mileage rates)
- [ ] Define country pack versioning and deployment model
- [ ] Build continuous anomaly detection (duplicates, merchant, timing, splits)
- [ ] Build risk scoring pipeline on Odoo data via bridge AI
- [ ] Wire `helpdesk_mgmt` for expense dispute case management
- [ ] Build recovery/remediation workflows

## Deferred — Full Spend Control Plane (Post-MVP)

- [ ] Build AP/invoice convergence on same spend graph
- [ ] Build unified operator console (spend queue, exceptions, risk, reimbursement)
- [ ] Add sourcing/procurement hooks
- [ ] Add benchmarking and simulation capabilities
- [ ] Measure success metrics (adoption, control, data quality, platform)

## Deferred — Azure Delivery Path Selection (Promotion Lane)

- [ ] Classify target deployment as Lane A (pilot) or Lane B (governed production)
- [ ] Map required Azure services to the minimum viable delivery path
- [ ] Define Azure Document Intelligence adapter contract for receipts/invoices
- [ ] Define whether Azure AI Search is actually required for the expense lane
- [ ] Define managed-identity auth path for model and document services
- [ ] Define promotion criteria from Lane A to Lane B
- [ ] If Lane B is selected, document required azd / pwsh / submodule / parameter prerequisites
- [ ] If Lane B is selected, explicitly decide whether Fabric and Purview stay disabled for first governed deployment

### Lane A evaluation (if pilot path selected)

- [ ] Evaluate focused agent accelerator as baseline agent shell
- [ ] Evaluate multimodal content processing template for receipt/invoice extraction
- [ ] Evaluate managed-identity sample patterns for keyless model access

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

- [x] Add `TransactionCase` tests for cash advance request/approval/release logic
- [x] Add `TransactionCase` tests for liquidation settlement computation (due to / refundable)
- [x] Add `TransactionCase` tests for cash advance creation, amount computation, overdue detection
- [x] Add `TransactionCase` tests for advance-to-liquidation linkage
- [x] Add `TransactionCase` tests for liquidation line totals and bucket aggregation
- [ ] Add `Form` tests for cash advance request and liquidation form flows
- [ ] Add `Form` tests for approval routing and finance review entry
- [ ] Add `HttpCase` only for browser-critical expense submission flows
- [x] Tag all tests with `@tagged('expense', 'concur')` for explicit execution control

## Wave — Browser-Critical End-to-End Coverage

- [ ] Identify browser-critical mobile companion flows requiring Playwright
- [ ] Add Playwright tests for mobile companion status/approval views
- [ ] Add Playwright tests for critical cash advance monitoring operator paths
- [ ] Capture traces for browser-critical test failures

## Wave — Debugging and Triage Support

- [ ] Use Chrome DevTools for mobile companion browser debugging
- [ ] Use Chrome DevTools for expense form DOM/network inspection
- [ ] Do not treat DevTools as an automated test framework

## Wave — Optional MCP Tooling Enablement

- [ ] Identify which MCP servers are useful for expense/concur development
- [ ] Enable Playwright MCP for mobile companion browser automation
- [ ] Enable Azure MCP Server for runtime validation
- [ ] Keep Azure AI Foundry MCP off MVP critical path unless explicitly justified

## Wave — API Edge Strategy

- [ ] Identify which endpoints must stay Odoo-native
- [ ] Identify which external/mobile/agent endpoints can be exposed through FastAPI
- [ ] Ensure FastAPI write paths go through Odoo-owned services/controllers, not direct DB writes
- [ ] Keep accounting/approval/tax logic in Odoo
- [ ] Use FastAPI only for edge concerns, orchestration, and async workloads

## Wave — Azure API Edge Selection

- [ ] Use FastAPI ACA template as the default edge baseline for mobile companion and cash advance monitoring APIs
- [ ] Keep Odoo as write-path owner for ERP business objects
- [ ] Define which endpoints remain Odoo-native
- [ ] Define which endpoints are exposed through FastAPI facade
- [ ] Prevent direct FastAPI writes to Odoo business tables
- [ ] Use managed identity for Azure AI access where AI assistance is in scope
- [ ] Keep OCR/multimodal templates out of MVP unless explicitly required

## Release Gates

- [x] No CE/OCA-covered capability reimplemented in custom code
- [x] AI enters only through bridge pattern, never direct accounting mutation
- [x] OCR stays in external bridge, Odoo owns workflow/review/posting
- [ ] All AI actions emit rationale, policy reference, confidence, audit log
- [ ] Known gaps documented in SSOT parity matrix
- [ ] PH country pack tested with BIR compliance scenarios
