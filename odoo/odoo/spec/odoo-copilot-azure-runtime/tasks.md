# Tasks — Odoo Copilot on Azure Runtime

## Phase 1 — Advisory Runtime (COMPLETE)

- [x] Create provider SSOT
- [x] Define Azure AI Foundry env contract
- [x] Define deployment-name requirement
- [x] Define timeout/auth/persona requirements
- [x] Create runtime contract doc (C-30 v1.3.0)
- [x] Document canonical runtime path
- [x] Document repo ownership split
- [x] Document Azure-native secret/runtime assumptions
- [x] Identify canonical Copilot controller/route
- [x] Verify authenticated request path
- [x] Verify Azure AI Foundry agent bridge call path
- [x] Execute end-to-end Copilot request
- [x] Capture success evidence (30/30 eval pass)
- [x] Verify `/web/health` remains healthy
- [x] Verify logs distinguish route vs provider failures
- [x] Release decision: ADVISORY_RELEASE_READY

**GATE: Phase 1 COMPLETE — Advisory release ready**

---

## Phase 2A — Identity & Context

- [x] Create Entra app roles manifest (15 roles, UUID v5 IDs)
- [x] Create role registration script (`scripts/entra/register-app-roles.sh`)
- [x] Create role assignment script (`scripts/entra/assign-app-role.sh`)
- [x] Create role-to-tool mapping table (`infra/entra/role-tool-mapping.yaml`)
- [x] Create Entra app roles operations doc
- [x] Implement `_build_context_envelope()` in `foundry_service.py`
- [x] Implement Odoo group → app_role mapping (placeholder for Entra token)
- [x] Compute `permitted_tools` from roles + mode
- [x] Compute `retrieval_scope` from roles
- [x] Inject envelope as `[CONTEXT_ENVELOPE]` prefix in thread messages
- [x] Update `chat_completion()` to accept and propagate envelope
- [x] Enrich audit model: `context_envelope`, `app_roles`, `surface`, `company_id`
- [x] Update HTTP controller to build and pass envelope
- [x] Update docs widget `server.ts` with `ContextEnvelope` interface
- [x] Update `chatViaFoundry()` to inject minimal docs envelope
- [ ] Execute Entra role registration against live app registration
- [ ] Validate role claims appear in token after assignment
- [ ] Run audit query confirming envelope fields populated

**GATE: Every chat request carries normalized envelope, audit rows show role/context**

---

## Phase 2B — Grounding & Retrieval

- [x] Define knowledge base source set (5 KB scopes)
- [x] Create AI Search index schema with `group_ids` field
- [x] Author knowledge base content (general, finance, BIR, marketing, ops)
- [x] Create index population script (`scripts/ai-search/populate-index.py`)
- [x] Create index validation script (`scripts/ai-search/validate-index.py`)
- [ ] Execute population script against `srch-ipai-dev`
- [ ] Validate index has ≥ 100 chunks across 5+ scopes
- [ ] Implement retrieval injection path in `chat_completion()`
- [ ] Implement query-time security trimming from `retrieval_scope`
- [ ] Add source provenance to response metadata
- [ ] Author "grounded answer" eval cases
- [ ] Run eval: grounded answers vs ungrounded baseline

**GATE: Non-empty corpus, security trimming works, grounded answers beat baseline**

---

## Phase 2C — Observability

- [x] Create telemetry model (`ipai.copilot.telemetry`)
- [x] Create App Insights configuration spec
- [ ] Wire App Insights connection string from env
- [ ] Add correlation ID (request_id) to request flow
- [ ] Propagate correlation ID: UI → controller → Foundry thread
- [ ] Capture latency, token usage, failure codes
- [ ] Capture safety event dimensions (blocked, redirected)
- [ ] Capture retrieval hit count
- [ ] Add App Insights to docs widget `server.ts`
- [ ] Create Grafana/App Insights dashboard for latency/error/safety
- [ ] Update release promotion runbook with telemetry gates

**GATE: Traces visible end-to-end, dashboard exists, runbook references telemetry**

---

## Phase 2D — Read-Only Tooling

- [x] Define tool schemas (OpenAI function-calling format)
- [x] Create tool executor model (`ipai.copilot.tool.executor`)
- [x] Implement `requires_action` handling in `chat_completion()`
- [x] Implement tool permission check from `permitted_tools`
- [ ] Wire `read_record` tool to Odoo ORM
- [ ] Wire `search_records` tool to Odoo ORM
- [ ] Wire `search_docs` tool to AI Search API
- [ ] Wire `get_report` tool to Odoo report engine
- [ ] Wire `read_finance_close` tool
- [ ] Wire `view_campaign_perf` tool
- [ ] Wire `view_dashboard` tool
- [ ] Wire `search_strategy_docs` tool
- [ ] Validate tool execution respects read_only_mode
- [ ] Validate scope check (company + entity) per tool
- [ ] Author tool eval cases (success + refusal)
- [ ] Run tool eval suite
- [ ] Register tools on live Foundry agent

**GATE: Read-only tools work, permission check enforced, tool evals pass**

---

## Phase 2E — Eval Expansion

- [x] Create expanded dataset structure (v2 format with pass_criteria)
- [x] Author safety cases (30): action refusal, PII, system exposure, prompt injection
- [x] Author role/context cases (30): RBAC, entity scope, retrieval scope, tool policy
- [x] Author retrieval grounding cases (30): source accuracy, empty search, stale docs
- [x] Author product/advisory cases (30): scope, mode, CTA, disclaimers
- [x] Author tool behavior cases (30): success, refusal, scope violation
- [x] Define thresholds for new categories
- [ ] Execute full 150+ eval run against live agent
- [ ] Review and correct scoring (manual review pass)
- [ ] Commit results as evidence
- [ ] Release decision: GROUNDED_ADVISORY_READY or higher

**GATE: 150+ cases pass thresholds, results committed**

---

## Phase 2F — Publish / CTA Surface

- [x] Create advisory-mode product copy template
- [x] Create CTA behavior matrix
- [x] Define banned CTAs (no false sign-up, no fake trial)
- [ ] Marketing review of product copy
- [ ] Legal review of disclaimers
- [ ] Validate all CTA URLs return HTTP 200
- [ ] Accessibility review (WCAG 2.2 AA)
- [ ] Publish copy to production web surface

**GATE: All CTAs route to working destinations, advisory mode clearly communicated**

---

## Phase 2 — Overall Gate

Phase 2 is complete when ALL sub-gates pass:

- [ ] 2A: Identity & context active
- [ ] 2B: Retrieval grounding live
- [ ] 2C: Observability dashboard live
- [ ] 2D: Read-only tools evaluated
- [ ] 2E: 150+ eval corpus passes
- [ ] 2F: Web advisory copy published

**Release class promotion: ADVISORY_RELEASE_READY → GROUNDED_ADVISORY_READY**
