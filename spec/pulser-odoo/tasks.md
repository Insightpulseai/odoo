# Tasks — Pulser Assistant: Odoo Adapter

## Phase 1 — Embedded UI

- [ ] Create `ipai_pulser_assistant` module scaffold (manifest, models, views, controllers, static)
- [ ] Implement PulserSystray OWL component (systray icon, click to open panel)
- [ ] Implement PulserRecordPanel OWL component (contextual panel with model/record awareness)
- [ ] Implement PulserRecommendation OWL component (action/suggestion card rendering)
- [ ] Add QWeb templates for all UI components
- [ ] Register systray component in Odoo web client

## Phase 2 — Record Context

- [ ] Define record context schema (model, id, display fields, related records, permissions)
- [ ] Implement context assembly for `account.move` (invoices, journal entries)
- [ ] Implement context assembly for `res.partner` (contacts, customers, vendors)
- [ ] Implement context assembly for `purchase.order` (procurement)
- [ ] Implement context assembly for `project.task` (close tasks, service delivery)
- [ ] Add company context and user permission context to all assemblies

## Phase 3 — Safe Action Modes

- [ ] Define action mode classification (read-only, suggest-only, approval-required, direct-execution)
- [ ] Implement action mode resolver (action type + user trust + module config)
- [ ] Implement approval dialog component for approval-required mode
- [ ] Implement suggestion card rendering for suggest-only mode
- [ ] Implement direct-execution handler with chatter logging
- [ ] Add finance-specific safety overrides (JE, payment, tax = always approval-required)

## Phase 4 — Telemetry and Evidence

- [ ] Define telemetry event schema (action, result, mode, user, timestamp, correlation_id)
- [ ] Implement PulserEvidenceEmitter model (buffer and send events to platform)
- [ ] Wire telemetry emission to all action execution paths
- [ ] Add chatter logging for all assistant interactions
- [ ] Verify telemetry reaching platform evidence store

## Phase 5 — Tool Endpoints

- [ ] Implement `/api/v1/pulser/context/{model}/{id}` (record context)
- [ ] Implement `/api/v1/pulser/action` (execute approved action)
- [ ] Implement `/api/v1/pulser/search/{model}` (search with domain)
- [ ] Implement `/api/v1/pulser/recommend/{model}/{id}` (contextual recommendations)
- [ ] Add auth_api_key authentication to all endpoints
- [ ] Register endpoints as tool bindings in agents tool catalog

## Phase 6 — Preview/Production Configuration

- [ ] Add `pulser.config` model for per-company assistant configuration
- [ ] Implement preview/prod channel selection in configuration
- [ ] Add environment ribbon integration (visual indicator for preview mode)
- [ ] Implement config-based action mode overrides per channel
- [ ] Verify preview and production channels work independently

## Verification Gates

- [ ] Systray assistant accessible from all major Odoo views
- [ ] Record context correct for account.move, res.partner, purchase.order
- [ ] Safety modes enforced (finance actions = approval-required)
- [ ] Activity logging in chatter for all interactions
- [ ] Telemetry reaching platform evidence store
- [ ] FastAPI tool endpoints operational and authenticated
- [ ] Preview/prod configuration separation verified

### Phase O5 — Tax Guru Odoo Adapter

- [ ] O5.1 — Implement ipai.pulser.tax_context model with partner_tax_profile_json, line_tax_context_json, document_refs_json
- [ ] O5.2 — Implement tax context builders for account.move (invoices/bills), purchase.order, hr.expense
- [ ] O5.3 — Implement ipai.pulser.tax_action_request model with action_mode enum (read_only/suggest_only/approval_required/direct_execution)
- [ ] O5.4 — Implement ipai.pulser.tax_exception_event model with platform sync emission
- [ ] O5.5 — Add FastAPI endpoint: GET /api/v1/pulser/tax/context/{model}/{id} (tax context retrieval)
- [ ] O5.6 — Add FastAPI endpoint: POST /api/v1/pulser/tax/action (tax action proposal submission)
- [ ] O5.7 — Add FastAPI endpoint: POST /api/v1/pulser/tax/exception (tax exception event emission)
- [ ] O5.8 — Wire safe execution modes: suggest_only default, approval_required for mutations, direct_execution only for reversible low-risk
