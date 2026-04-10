# Tasks — PPM Clarity for Odoo 18

## Phase 0 — Reset and Inventory

- [x] Confirm Odoo CE 18 `project` baseline capabilities used as the execution foundation
- [x] Confirm adopted OCA `project` modules from current workspace inventory
- [x] Build capability map: current `ipai_finance_ppm` feature → CE / OCA / custom delta / delete
- [x] Record known parity gaps that remain outside CE/OCA coverage

## Phase 1 — Architecture Correction

- [x] Rewrite spec language to make CE/OCA the default baseline
- [x] Reclassify `ipai_finance_ppm` as delta-only scope
- [x] Remove any requirement that duplicates hierarchy/stakeholder/role/timeline/pivot/template features already available in CE/OCA
- [x] Add explicit non-goals against monolithic custom PPM implementation

## Phase 2 — Implementation Decomposition

- [x] Remove `project_task_integration.py` (deprecated Supabase webhook event emission) — not present; cleaned in prior pass
- [x] Remove `hr_expense.py` Pulser AI binding (unrelated to PPM) — not present; cleaned in prior pass
- [x] Remove `data/ir_cron_ppm_sync.xml` from manifest (deprecated budget sync cron — removed from data list 2026-04-10)
- [x] Evaluate and clean `data/ir_config_parameter_powerbi.xml` — not in manifest; okr_dashboard_action.xml not loaded
- [x] Remove or rewrite `static/src/js/okr_dashboard_action.js` — JS file absent; okr_dashboard_action.xml excluded from manifest
- [x] Keep `project_project.py` budget/cost-center fields (delta)
- [x] Keep `analytic_account.py` budget sync (delta)
- [x] Add `ppm.budget.line` model (budget/forecast/actual per period)
- [x] Add `ppm.portfolio.health` model (RAG status per project)
- [x] Add `ppm.risk` model (risk register)
- [x] Add `ppm.issue` model (issue register)
- [x] Add `ppm.scoring` model (investment scoring)
- [x] Add `ppm.gate.review` model (phase-gate reviews)
- [x] Update `__manifest__.py` — v18.0.2.0.0, OCA depends comment, deprecated cron removed
- [x] Add form/tree/kanban views for delta models
- [x] Add portfolio dashboard (pivot + graph on delta models)
- [x] Update security CSV for new models

## Phase 3 — Proof and Validation

- [x] Add proof matrix showing CE/OCA coverage vs custom delta coverage (in plan.md and constitution.md)
- [x] Add regression tests for retained delta models only (see Wave — Odoo-Native Test Coverage below)
- [ ] Add installation/contract test for required CE/OCA project baseline
- [x] Add documentation of known gaps (dependency/capacity limitations — in constitution.md §5)

## Phase 4 — Release Gate (MVP)

- [x] Fail release if `ipai_finance_ppm` still owns a CE/OCA-covered capability without documented exception — resolved; delta scope enforced
- [x] Fail release if parity claims omit known project-planning gaps — documented in constitution.md §5
- [x] Fail release if deprecated integration residue remains in PPM core — cron removed from manifest; no Supabase/n8n residue present

## Wave — Review and Go-Live Readiness

- [ ] Map MVP architecture against relevant Azure review-checklists domains
- [ ] Record any promotion-lane findings for multitenancy, WAF, AI, cost, and networking
- [ ] Derive a finance go-live checklist from the Odoo 18 checklist
- [ ] Adapt the Odoo checklist for target localization and actual enabled modules
- [ ] Validate opening entries, receivable/payable balances, inventory setup, and payment/reconciliation readiness before go-live
- [ ] Keep review findings and go-live checks as validation artifacts, not as replacements for feature specs

## Wave — Foundry Project Connection Validation

- [ ] Confirm current connected resources on `ipai-copilot`
- [ ] Record only actually attached project connections as baseline dependencies
- [ ] Add Azure OpenAI connection only where AI inference is required
- [ ] Add Azure AI Search only where RAG/grounding is explicitly required
- [ ] Keep Cosmos DB / Fabric / Bing grounding off MVP critical path unless justified
- [ ] Document every new Foundry project connection before implementation depends on it

## Wave — SaaS Architecture Normalization

- [ ] Define tenant meaning for this feature
- [ ] Define shared vs isolated components
- [ ] Define control-plane responsibilities
- [x] Confirm MVP is a viable horizontal slice
- [ ] Mark deployment stamps / advanced rollout / feature-flag operations as promotion-lane unless explicitly required now

## Wave — Odoo-Native Test Coverage

- [x] Add `TransactionCase` tests for portfolio/project/task business rules
- [x] Add `TransactionCase` tests for budget/forecast/variance computation
- [x] Add `TransactionCase` tests for portfolio health and RAG status entry
- [x] Tag all tests with `@tagged('ppm', 'post_install', '-at_install')` for explicit execution control
- [ ] Add `Form` tests for project creation and milestone entry flows
- [ ] Add `HttpCase` only if a browser-critical operator path exists

## Wave — Browser-Critical End-to-End Coverage

- [ ] Identify any browser-critical PPM operator flows requiring Playwright
- [ ] Add Playwright tests for identified critical flows only
- [ ] Capture traces for browser-critical test failures

## Wave — Debugging and Triage Support

- [ ] Use Chrome DevTools as browser-debugging surface for PPM views
- [ ] Do not treat DevTools as an automated test framework

## Wave — Optional MCP Tooling Enablement

- [ ] Identify which MCP servers are useful for PPM development
- [ ] Enable Playwright MCP and Azure MCP Server where applicable
- [ ] Keep Azure AI Foundry MCP off MVP critical path unless explicitly justified

## Wave — API Edge Strategy

- [ ] Identify which endpoints must stay Odoo-native
- [ ] Identify which external/mobile/agent endpoints can be exposed through FastAPI
- [ ] Ensure FastAPI write paths go through Odoo-owned services/controllers, not direct DB writes
- [ ] Keep accounting/approval/tax logic in Odoo
- [ ] Use FastAPI only for edge concerns, orchestration, and async workloads

## Wave — Azure API Edge Selection

- [ ] Use FastAPI ACA template as the default edge baseline where external/mobile API is required
- [ ] Keep Odoo as write-path owner for ERP business objects
- [ ] Define which endpoints remain Odoo-native
- [ ] Define which endpoints are exposed through FastAPI facade
- [ ] Prevent direct FastAPI writes to Odoo business tables
- [ ] Use managed identity for Azure AI access where AI assistance is in scope
- [ ] Keep OCR/multimodal templates out of MVP unless explicitly required

## Deferred — Post-MVP

- [ ] Advanced enterprise capacity optimization
- [ ] Drag-drop resource optimization (EE parity)
- [ ] Full scenario optimization
- [ ] Azure-hosted portfolio dashboards
- [ ] AI-assisted portfolio review via bridge
- [ ] Governed Azure runtime for PPM analytics
