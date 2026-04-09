# Copilot Stage 3 — Grounded Advisory Checklist

> Version: 1.0.0
> Last updated: 2026-03-23
> Parent: `agents/foundry/ipai-odoo-copilot-azure/runtime-contract.md` (C-30)
> Stage target: GROUNDED_ADVISORY_READY (runtime-contract.md §Publish Gate)

---

## Current Baseline (audited 2026-03-23)

| Surface | State | Evidence |
|---------|-------|----------|
| Foundry project | `data-intel-ph`, `eastus2` | `remote-state/remote-state-summary.md` |
| Foundry agent | `asst_45er4aG28tFTABadwxEhODIf`, gpt-4.1, temp 0.4 | remote-state snapshot 2026-03-15 |
| System prompt | v2.1.0 — 3-lane retrieval policy, truthfulness rules | `agents/foundry/.../system-prompt.md` |
| Tool definitions | v1.1.0 — 9 tools incl. `search_odoo_docs_web` | `agents/foundry/.../tool-definitions.json` |
| Tool executor | 15 handlers incl. bounded web search | `addons/ipai/ipai_odoo_copilot/models/tool_executor.py` |
| AI Search service | `srch-ipai-dev` exists, **0 indexes, 0 documents** | remote-state snapshot |
| Retrieval contract | v1.0.0, Phase 2B — **not yet active** | `agents/foundry/.../retrieval-grounding-contract.md` |
| Eval corpus | 30/30 pass (advisory), no retrieval evals | `evals/odoo-copilot/` |
| Odoo module | `ipai_odoo_copilot` installed, systray + Discuss bot live | `addons/ipai/ipai_odoo_copilot/` |
| KB registry | 7 KBs registered, all runtime.search_index = missing | `agents/knowledge/registry.yaml` |
| Monitoring | No App Insights, no diagnostics | remote-state snapshot |

**Bottom line**: The Odoo-side module, Foundry agent, and tool executor are wired. The retrieval chain (Search index → Foundry connection → grounded response) is **completely unwired**.

---

## Phase 1: Establish AI Foundation

### 1.1 Lock the Stage 3 use case

- [ ] **Use case**: Odoo Copilot grounded answers over Odoo 18 docs + internal knowledge
- [ ] **Business case**: Faster, more accurate ERP/operator answers; reduced manual doc lookup; lower support friction
- [ ] Record in: `spec/copilot-target-state/prd.md` §Stage 3

### 1.2 Define success metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Retrieval hit rate on `odoo18-docs` | >= 80% of docs queries return relevant chunks | Smoke test pass rate |
| Grounded answer rate | >= 70% of responses cite a source | Eval corpus |
| Answer latency (p95) | < 15s end-to-end | App Insights |
| User adoption | >= 5 unique users/week within 30 days | Audit model |
| Task-completion delta | Qualitative improvement on common ERP help tasks | User feedback |

- [ ] Record metrics in: `ssot/governance/platform-capabilities-unified.yaml` under copilot section
- [ ] Create eval threshold file: `evals/odoo-copilot/stage3-thresholds.yaml`

### 1.3 Reconcile the runtime contract

| Property | Spec (metadata.yaml) | Azure Reality (remote-state) | Decision |
|----------|---------------------|------------------------------|----------|
| Model | `gpt-4.1` | `gpt-4.1` (agent) | Accept — model matches |
| Search index | `ipai-knowledge-index` | **empty** (0 indexes) | Must populate |
| Search connection | `srchipaidev8tlstu` | Connection exists, no index | Must create index |
| Endpoint type | OpenAI-compat threads/runs | OpenAI-compat | Accept for Stage 3 |

- [ ] Verify model deployment name in Foundry portal matches `gpt-4.1`
- [ ] If mini is deployed instead, update `metadata.yaml` and `runtime-contract.md`
- [ ] Record decision in: `agents/foundry/ipai-odoo-copilot-azure/metadata.yaml` §model_deployment

### 1.4 Pricing decision

- [ ] Accept standard pay-per-token for Stage 3 validation
- [ ] Defer PTU/provisioned decision until usage data exists (Phase 3)
- [ ] Record in: `ssot/governance/platform-capabilities-unified.yaml` §pricing

### 1.5 Organizational readiness

| Role | Owner | File target |
|------|-------|-------------|
| Product owner | (assign) | `spec/copilot-target-state/tasks.md` |
| Approver | (assign) | `spec/copilot-target-state/tasks.md` |
| Search indexing operator | (assign) | `agents/knowledge/registry.yaml` |
| Foundry endpoint operator | (assign) | `agents/foundry/.../metadata.yaml` |
| Gateway env wiring operator | (assign) | `addons/ipai/ipai_odoo_copilot/` |
| Eval/acceptance owner | (assign) | `evals/odoo-copilot/` |
| Rollback authority | (assign) | `docs/operations/ODOO_COPILOT_RUNBOOK.md` |

- [ ] Assign all roles
- [ ] Record in: `docs/operations/ODOO_COPILOT_RUNBOOK.md` §Roles

### Phase 1 exit criteria

- [ ] One clearly scoped Stage 3 use case documented
- [ ] One approved success-metric set with thresholds
- [ ] One accepted model/pricing contract (no ambiguity)
- [ ] One owner per runtime surface

---

## Phase 2: Build GenAI Solutions Efficiently

### 2.1 Governance and controls

- [ ] Freeze **read-only advisory scope** for Stage 3
  - File: `agents/foundry/.../system-prompt.md` — already enforced in v2.1.0
- [ ] Keep write/action paths disabled (`read_only_mode = ON`)
  - File: `addons/ipai/ipai_odoo_copilot/data/ir_config_parameter.xml`
- [ ] Keep proposal-first behavior in place
  - File: `agents/foundry/.../guardrails.md`
- [ ] Record model/runtime contract in SSOT
  - File: `ssot/governance/ai-consolidation-foundry.yaml`
- [ ] Record retrieval truth policy (do not claim browsing/docs retrieval unless wired)
  - File: `agents/foundry/.../system-prompt.md` — done in v2.1.0 §Retrieval Truthfulness Rules

### 2.2 Retrieval and knowledge — `odoo-docs` index

| Step | Action | File/Resource |
|------|--------|---------------|
| 2.2.1 | Decide: dedicated `odoo18-docs` index vs shared `ipai-knowledge-index` | `agents/foundry/.../retrieval-grounding-contract.md` |
| 2.2.2 | Create Azure AI Search index with schema from retrieval-grounding-contract.md | Azure portal / Bicep: `infra/azure/modules/ai-search-index.bicep` |
| 2.2.3 | Enable **vector search** (semantic ranker + embedding field) | Index schema update |
| 2.2.4 | Wire embedding model (`text-embedding-3-small` via `oai-ipai-dev`) | `agents/knowledge/registry.yaml` §shared.embedding_service |
| 2.2.5 | Run ingestion: clone `odoo/documentation@19.0`, chunk RST, embed, push to index | `agents/knowledge/odoo18_docs/source.yaml` → `apps/odoo-docs-kb/service.py` |
| 2.2.6 | Verify document/chunk counts (target: ~7200 chunks per registry) | `scripts/ai-search/validate-index.py` |
| 2.2.7 | Run retrieval smoke test | `agents/tests/claude_platform/retrieval_smoke.yaml` pattern |

- [ ] 2.2.1 Decision recorded
- [ ] 2.2.2 Index created in `srch-ipai-dev`
- [ ] 2.2.3 Vector search enabled
- [ ] 2.2.4 Embedding model wired
- [ ] 2.2.5 Ingestion run completed
- [ ] 2.2.6 Chunk count verified (>= 100 minimum for GROUNDED_ADVISORY_READY gate)
- [ ] 2.2.7 Smoke test passes (>= 80% hit rate)

### 2.3 Foundry and Azure wiring

| Step | Action | Resource |
|------|--------|----------|
| 2.3.1 | Assign RBAC: Foundry project identity → `Search Index Data Reader` on `srch-ipai-dev` | `az role assignment create` |
| 2.3.2 | Assign RBAC: Foundry project identity → `Cognitive Services OpenAI User` on `oai-ipai-dev` | `az role assignment create` |
| 2.3.3 | Create Foundry project connection: AI Search → `srch-ipai-dev` | Foundry portal or SDK |
| 2.3.4 | Create Foundry project connection: Azure OpenAI → `oai-ipai-dev` (for embeddings) | Foundry portal or SDK |
| 2.3.5 | Attach `odoo18-docs` index as knowledge source on agent `asst_45er4aG28tFTABadwxEhODIf` | Foundry portal |
| 2.3.6 | Publish one Foundry **online endpoint** | Foundry portal or SDK |
| 2.3.7 | Wire gateway env/config to Foundry endpoint URL | `addons/ipai/ipai_odoo_copilot/data/ir_config_parameter.xml` |
| 2.3.8 | Verify gateway calls the endpoint (not just deployed, but actually serving) | `test_connection()` in `foundry_service.py` |

- [ ] 2.3.1 Search RBAC assigned
- [ ] 2.3.2 OpenAI RBAC assigned
- [ ] 2.3.3 Search connection created
- [ ] 2.3.4 OpenAI connection created
- [ ] 2.3.5 Knowledge source attached to agent
- [ ] 2.3.6 Online endpoint published
- [ ] 2.3.7 Gateway config updated
- [ ] 2.3.8 End-to-end call verified

### 2.4 GenAIOps and evaluation

#### Retrieval-aware evals

| Eval | Method | Threshold | File |
|------|--------|-----------|------|
| Groundedness | % of responses citing a retrieval source | >= 70% | `evals/odoo-copilot/stage3-thresholds.yaml` |
| Citation coverage | % of facts with correct citation | >= 85% | `evals/odoo-copilot/stage3-thresholds.yaml` |
| Hallucination rate on docs questions | % of responses with fabricated info | <= 10% | `evals/odoo-copilot/stage3-thresholds.yaml` |
| Fallback correctness | Graceful degradation when retrieval misses | 100% | `evals/odoo-copilot/stage3-thresholds.yaml` |

- [ ] Create `evals/odoo-copilot/stage3-thresholds.yaml`
- [ ] Create retrieval eval corpus (minimum 20 cases)
- [ ] Run evals, record results in `evals/odoo-copilot/results/`

#### Smoke tests (end-to-end)

| Test case | Expected behavior | Pass criteria |
|-----------|-------------------|---------------|
| Paste Odoo docs URL | Copilot searches and returns grounded answer | Response cites the URL or related doc |
| Direct Odoo docs question ("how to configure multi-company") | KB retrieval returns chunks, copilot answers with citation | Response contains module name + citation |
| ERP record question ("show my draft invoices") | Lane 1 tools used (search_records) | Response contains record data |
| No-tool fallback ("tell me a joke") | Politely redirects to scope | No retrieval attempted, scope redirect |
| KB miss ("explain quantum computing in Odoo") | Web search fallback, then graceful "not found" | No hallucination, honest "not found" |

- [ ] All 5 smoke tests pass
- [ ] Results recorded in `docs/evidence/` with evidence pack

#### Safe rollout

- [ ] Staging endpoint exists (or dev endpoint serves as staging)
- [ ] Rollback path documented in `docs/operations/ODOO_COPILOT_RUNBOOK.md`
- [ ] Feature flag or traffic control mechanism identified
  - Current: `ipai_copilot.enabled` ir.config_parameter (boolean kill switch)

### Phase 2 exit criteria

- [ ] `odoo18-docs` indexed and queryable (>= 100 chunks)
- [ ] Vector/semantic retrieval decision implemented (not left implicit)
- [ ] Foundry Search + OpenAI connections exist
- [ ] One online endpoint published
- [ ] Gateway wired to endpoint
- [ ] End-to-end grounded answer path proven in 5 smoke tests
- [ ] Retrieval-aware eval corpus passes thresholds

---

## Phase 3: Manage AI Investments

### 3.1 Unit economics

| Metric | Formula | Target file |
|--------|---------|-------------|
| Cost per copilot session | Total token cost / session count | Dashboard |
| Cost per grounded answer | (Embedding + Search + LLM tokens) / grounded answer count | Dashboard |
| Cost per task assist | Total cost / successful task-completion count | Dashboard |

- [ ] Define unit economics
- [ ] Record in: `ssot/governance/platform-capabilities-unified.yaml` §copilot.economics

### 3.2 Business impact tracking

| Impact | Measurement | Baseline |
|--------|-------------|----------|
| Manual doc lookup time reduction | Before/after survey | Establish baseline |
| Answer quality for Odoo/operator questions | Eval score delta | Stage 2 eval baseline |
| ERP user onboarding speed | Time-to-first-task | Establish baseline |
| Repeated support question reduction | Support ticket volume | Establish baseline |

- [ ] Establish baselines before grounded rollout
- [ ] Track deltas at 30-day and 90-day marks

### 3.3 Usage and cost monitoring

#### Dashboard requirements

| Metric | Source | Visualization |
|--------|--------|---------------|
| Tokens in/out per day | App Insights / Foundry traces | Time series |
| Retrieval calls per day | Audit model + Search metrics | Time series |
| Search query volume | `srch-ipai-dev` metrics | Time series |
| Endpoint latency (p50, p95) | App Insights | Histogram |
| Grounded vs ungrounded answers | Eval pipeline | Ratio chart |
| Failed retrieval rate | Audit model (search returns 0) | Percentage |

- [ ] Create monitoring dashboard
  - Option A: Power BI (preferred per CLAUDE.md §12)
  - Option B: App Insights workbook (interim)
- [ ] File: `infra/azure/modules/app-insights-copilot-dashboard.bicep` or Power BI template

#### Watch list

- [ ] Low-value traffic (generic greetings consuming tokens)
- [ ] Duplicate retrieval calls (same query repeated)
- [ ] Over-broad prompts (long prompts with low retrieval hit rate)
- [ ] Expensive flows that don't improve answer quality

### 3.4 Model optimization

| Scenario | Action |
|----------|--------|
| `gpt-4.1` quality sufficient, cost acceptable | Keep current |
| Quality sufficient but cost too high | Evaluate `gpt-4.1-mini` for non-grounded responses |
| Quality insufficient for grounded answers | Keep `gpt-4.1`, improve retrieval/chunking |
| Adoption rises above cost threshold | Evaluate PTU/provisioned pricing |

- [ ] Monthly review cadence established
- [ ] Decision threshold documented (e.g., "$X/month triggers PTU evaluation")

### 3.5 Retrieval optimization

- [ ] Reduce irrelevant KB scopes (start with `odoo18-docs` only, add others incrementally)
- [ ] Improve chunking/metadata based on retrieval miss analysis
- [ ] Separate Odoo docs from less relevant corpora
- [ ] Track chunk-level hit rates to identify weak coverage areas

### Phase 3 exit criteria

- [ ] Live usage/cost dashboard exists
- [ ] Business-value KPIs are tracked with baselines
- [ ] Pricing-model review has a real threshold (not guesswork)
- [ ] Monthly optimization cadence documented

---

## Execution Priority Order

Given the current audit state (module wired, retrieval chain unwired):

| Priority | Action | Blocked by |
|----------|--------|------------|
| 1 | Runtime contract decision (model + pricing) | Nothing |
| 2 | `odoo18-docs` retrieval/indexing | Nothing |
| 3 | RBAC for Foundry project identity | Nothing |
| 4 | Foundry Search + OpenAI connections | #3 |
| 5 | Foundry online endpoint | #4 |
| 6 | Gateway → Foundry wiring | #5 |
| 7 | Grounded eval + smoke evidence | #6 |
| 8 | Usage/cost/value dashboard | #7 |

Items 1-3 can run in parallel. Items 4-8 are sequential.

---

## What NOT to do yet

- Do not widen the use case beyond Odoo Copilot retrieval
- Do not add more agent surfaces before `odoo-docs` grounding is real
- Do not claim full production if the endpoint/retrieval chain is still unwired
- Do not leave `gpt-4.1` vs `gpt-4.1-mini` ambiguous in SSOT
- Do not skip the eval step — grounded retrieval without eval evidence is unverifiable

---

## Stage 3 Definition of Done

Stage 3 is complete when ALL of these are true:

1. Odoo Copilot can answer **grounded Odoo docs questions** with citations
2. Retrieval is real and visible in behavior (not just wired but unused)
3. The Foundry endpoint exists and is actually in the serving path
4. Gateway is wired to the endpoint (not just configured but calling)
5. Cost and value are measurable (dashboard exists)
6. The runtime contract matches reality (no spec/reality drift)
7. Publish gate: **GROUNDED_ADVISORY_READY** criteria met per `runtime-contract.md`

---

## File Target Map

| Domain | File | Action |
|--------|------|--------|
| Spec | `spec/copilot-target-state/prd.md` | Add Stage 3 use case |
| Spec | `spec/copilot-target-state/tasks.md` | Add Stage 3 task milestones |
| Runtime contract | `agents/foundry/.../runtime-contract.md` | Update current stage + publish gate |
| Runtime contract | `agents/foundry/.../metadata.yaml` | Confirm model_deployment |
| System prompt | `agents/foundry/.../system-prompt.md` | Done (v2.1.0) |
| Tool definitions | `agents/foundry/.../tool-definitions.json` | Done (v1.1.0) |
| Tool executor | `addons/ipai/ipai_odoo_copilot/models/tool_executor.py` | Done (15 tools) |
| Retrieval contract | `agents/foundry/.../retrieval-grounding-contract.md` | Activate Phase 2B |
| KB registry | `agents/knowledge/registry.yaml` | Update runtime status after indexing |
| KB source | `agents/knowledge/odoo18_docs/source.yaml` | No change needed |
| Eval thresholds | `evals/odoo-copilot/stage3-thresholds.yaml` | Create |
| Eval corpus | `evals/odoo-copilot/corpus/stage3-retrieval/` | Create (20+ cases) |
| SSOT | `ssot/governance/platform-capabilities-unified.yaml` | Add copilot metrics + pricing |
| SSOT | `ssot/governance/ai-consolidation-foundry.yaml` | Record runtime contract |
| Runbook | `docs/operations/ODOO_COPILOT_RUNBOOK.md` | Add roles, rollback, Stage 3 ops |
| Workflow | `agents/workflows/odoo_docs_assist.yaml` | Done (3-lane retrieval) |
| Infra | `infra/azure/modules/ai-search-index.bicep` | Create (index definition as IaC) |
| Monitoring | `infra/azure/modules/app-insights-copilot-dashboard.bicep` | Create |
| Evidence | `docs/evidence/<stamp>/copilot-stage3/` | Smoke test results |
| UX | `addons/ipai/ipai_odoo_copilot/static/src/xml/copilot_systray.xml` | Done (v2.1.0) |

---

*Last updated: 2026-03-23*
