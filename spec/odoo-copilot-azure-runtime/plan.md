# Plan — Odoo Copilot on Azure Runtime

## Phase 1 — Advisory Runtime (COMPLETE)

### Delivered

1. Provider SSOT defined (Azure AI Foundry, Assistants API)
2. Route/controller contract verified (`/ipai/copilot/chat`, `/chat/service`)
3. Azure AI Foundry runtime wired (threads/runs pattern, gpt-4.1)
4. End-to-end validated (Odoo Discuss + HTTP API + docs widget)
5. Runtime contract committed (C-30 v1.3.0)
6. Evaluation evidence committed (30/30 pass, eval-20260315-full-final)
7. Release decision: **ADVISORY_RELEASE_READY**

### Phase 1 acceptance: MET

- Route is live
- Azure-backed response proven
- Provider SSOT committed
- Runtime doc committed
- Evidence artifacts confirm success
- Safety thresholds all pass

---

## Phase 2 — Governed Advisory Surface

The goal of Phase 2 is to convert the safe advisory demo into a **governed, observable, grounded, role-aware advisory surface** before enabling tools.

### Execution order is strict

Identity/context → retrieval grounding → telemetry → read-only tools → eval expansion.

Rationale: Without a canonical request envelope, any later retrieval or tool execution is structurally under-scoped. You need identity before grounding. You need grounding before tools. You need observability before wider rollout.

---

### Phase 2A — Identity & Context

**Purpose**: Establish who is asking, from where, with what permissions.

#### Deliverables

1. Register 14+ Entra app roles in app registration manifest
2. Implement context envelope builder in `foundry_service.py`
3. Pass envelope into every request path (Discuss, HTTP API, docs widget)
4. Enrich audit model with role, surface, company, envelope JSON
5. Record role + tenant + org scope in every audit event
6. Create role-to-tool mapping lookup table

#### Exit criteria

- Every chat request carries a normalized envelope
- Role resolution is deterministic (Odoo group → app_role mapping, with Entra token path ready)
- Audit rows show role/context fields populated
- Prompt/runtime path uses the envelope consistently
- Envelope is NEVER sent to client

---

### Phase 2B — Grounding & Retrieval

**Purpose**: Give the assistant factual source material before it answers.

#### Deliverables

1. Define knowledge base source set and chunking contract
2. Create AI Search index with `group_ids` security trimming field
3. Populate index with structured knowledge base content
4. Implement retrieval injection path in `chat_completion()`
5. Implement query-time security trimming from `retrieval_scope`
6. Add retrieval provenance to response metadata
7. Add "answer grounded from sources" eval cases

#### Exit criteria

- Non-empty searchable corpus (≥ 100 chunks across 5+ KB scopes)
- Source provenance included in runtime context
- Role-based document filtering works (query returns 0 results for unauthorized scope)
- Eval cases prove grounded answers beat ungrounded baseline

---

### Phase 2C — Observability

**Purpose**: Make every request traceable end-to-end before wider rollout.

#### Deliverables

1. Wire App Insights telemetry (connection string from env)
2. Add correlation IDs: UI → Odoo controller → Foundry thread
3. Capture dimensions: latency, token usage, failure codes, fallback usage
4. Add safety event dimensions (blocked, redirected, refusal type)
5. Create release dashboard / SLO view
6. Update release promotion runbook with telemetry gates

#### Minimum telemetry dimensions

- request_id (correlation)
- user_id (surrogate)
- channel (discuss/api/widget)
- role (app_roles)
- model/assistant_id
- latency_ms
- prompt_tokens / completion_tokens
- retrieval_hit_count
- fallback_path_used
- blocked / redirected / safety_event flags

#### Exit criteria

- Traces visible end-to-end (UI → Odoo → Foundry → response)
- Failures attributable by stage
- Dashboard exists for latency/error/safety
- Release promotion runbook references telemetry gates

---

### Phase 2D — Read-Only Tooling

**Purpose**: Enable non-mutating tools only, after context + grounding + telemetry.

#### Deliverables

1. Implement tool executor model (`ipai.copilot.tool.executor`)
2. Handle `requires_action` run status in `chat_completion()`
3. Wire Stage 1 read-only tools: `read_record`, `search_records`, `search_docs`, `get_report`, `read_finance_close`, `view_campaign_perf`, `view_dashboard`, `search_strategy_docs`
4. Tool permission check from `permitted_tools` in context envelope
5. Tool execution audit trail
6. Tool-call eval cases (success + refusal)

#### Start with (non-mutating only)

- Knowledge lookup
- Odoo metadata lookup
- Document fetch
- Record summary
- Status inspection
- Policy / playbook retrieval

#### Do NOT start with

- Write/update/create/post actions
- Irreversible operations
- Finance-impacting actions
- Security/admin actions

#### Exit criteria

- Tool contract schema versioned
- Per-tool allowlist exists
- Eval set includes tool refusal and tool success cases
- Audit trail captures tool invocation intent + result
- Read-only mode blocks ALL write tools regardless of role

---

### Phase 2E — Eval Expansion

**Purpose**: Prove the system at 150+ cases before broader publish.

#### Deliverables

1. Expand dataset from 30 to 150+ cases
2. Add RBAC boundary cases (role enforcement, entity scope, retrieval scope, tool policy)
3. Add context-awareness cases (surface, mode, record context)
4. Add prompt injection resistance cases
5. Add retrieval grounding quality cases
6. Add tool behavior cases (success + refusal)

#### Suggested eval buckets

| Bucket | Count |
|--------|-------|
| Safety (action refusal, PII, system exposure, prompt injection) | 30 |
| Role / context (RBAC enforcement, entity scope, retrieval scope) | 30 |
| Retrieval grounding (source accuracy, empty search, stale docs) | 30 |
| Product / advisory (scope, mode, CTA, disclaimers, offerings) | 30 |
| Tool behavior (success, refusal, scope violation) | 30 |

#### Exit criteria

- 150+ cases authored and runnable
- All threshold categories defined with pass/fail criteria
- At least one full run against live agent
- Results committed as evidence

---

### Phase 2F — Publish / CTA Surface

**Purpose**: Finalize the web-facing product copy and CTA routing.

#### Deliverables

1. Advisory-mode product copy reviewed by marketing
2. CTA behavior matrix validated (no broken links, no false claims)
3. Disclaimer copy approved
4. Accessibility review (WCAG 2.2 AA)

#### Exit criteria

- Every CTA routes to a working destination
- No unsupported claims of live capability
- Advisory mode clearly communicated
- Legal disclaimers present

---

## Release Ladder

| Release Class | Required |
|---|---|
| **ADVISORY_RELEASE_READY** (current) | 30/30 eval pass, safety thresholds met, system prompt v2.1.0 |
| **GROUNDED_ADVISORY_READY** | + Entra roles active, context envelope active, search index populated, retrieval injection live, telemetry live |
| **ASSISTED_ACTIONS_READY** | + read-only tools live, tool eval evidence, 150+ eval pass |
| **GA** | + write tools evaluated, security review, SLA defined, AI Gateway governance |

---

## Acceptance criteria (Phase 2 complete)

1. Request payloads carry normalized role/context
2. Audit rows persist role/context/correlation ID
3. AI Search returns non-empty grounded results
4. Retrieval responses are security-trimmed
5. App Insights shows full request trace
6. Tool path remains disabled until read-only tool evals pass
7. 150+ eval corpus includes safety, role, retrieval, and tool buckets
8. Release promotion criteria explicitly updated in runbook
