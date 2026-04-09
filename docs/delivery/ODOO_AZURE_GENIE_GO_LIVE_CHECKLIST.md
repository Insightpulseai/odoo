# Odoo + Azure AI + Genie — Go-Live Checklist

> Version: 1.0.0
> Last updated: 2026-03-23
> Launch tier: **Internal beta / trusted users / read-only advisory**
> Parent: `docs/delivery/GO_LIVE_ACCELERATION_PLAN.md`
> SSOT: `ssot/delivery/go_live_plan.yaml`

---

## Audit Baseline (2026-03-23)

| Surface | State | Blocker? |
|---------|-------|----------|
| Odoo Copilot module | Installed, systray + Discuss bot live | No |
| Foundry agent | `asst_45er4aG28tFTABadwxEhODIf`, gpt-4.1, temp 0.4 | No |
| System prompt | v2.1.0 — 3-lane retrieval, truthfulness rules | No |
| Tool executor | 15 handlers (14 read-only + 1 bounded web search) | No |
| `action_execute()` | **Stub — not implemented** | **Yes** |
| `ipai.copilot.audit` model | **Missing — audit writes silently fail** | **Yes** |
| Rate limiting | **Not enforced** (2s Discuss only, HTTP unthrottled) | **Yes** |
| Request validation | **Incomplete** (envelope not validated server-side) | **Yes** |
| Company scoping | **Too loose** (no entity-boundary enforcement) | **Yes** |
| AI Search (`srch-ipai-dev`) | 1 index, 331 docs; `odoo-docs` **missing** | **Yes** |
| Vector/semantic search | **Not configured** | **Yes** |
| Foundry connections | **None** (no Search, no OpenAI) | **Yes** |
| Foundry online endpoint | **None deployed** | **Yes** |
| Gateway → Foundry wiring | **Not wired** | **Yes** |
| Model contract | Spec says `gpt-4.1`; deployed is `gpt-4.1` (confirmed remote-state) | No |
| App Insights | **Not configured** | **Yes** |
| Entra app roles | **Not registered** | **Yes** |
| Eval corpus | 30/30 advisory; **0 retrieval evals** | **Yes** |

**Bottom line**: Module is wired. Retrieval chain, production hardening, and observability are unwired.

---

## A. Launch Scope

### Must be true before any launch

- [ ] Launch label is **internal beta**, not GA
  - File: `docs/architecture/ODOO_COPILOT_PUBLISHABLE_STATE.md`
- [ ] User scope is **trusted internal users only**
  - File: `docs/operations/ODOO_COPILOT_RUNBOOK.md` §Access
- [ ] Copilot is **read-only advisory by default** (`read_only_mode = ON`)
  - File: `addons/ipai/ipai_odoo_copilot/data/ir_config_parameter.xml`
- [ ] Any write/action path is disabled or hard fail-closed
  - File: `addons/ipai/ipai_odoo_copilot/models/tool_executor.py` — `action_execute()` must raise `NotImplementedError` or return error
- [ ] Genie is positioned as **analytics Q&A**, not ERP transaction execution
  - File: `docs/architecture/DATABRICKS_BUNDLES_BASELINE.md` §Genie
- [ ] Document Intelligence is positioned as **extract + review assist**, not autonomous posting
  - File: `docs/architecture/COPILOT_TARGET_STATE.md` §Document Processing Plane

---

## B. Identity and Access

### B.1 Odoo / Entra SSO

| Check | File target | Status |
|-------|-------------|--------|
| Odoo login app is single-tenant | Entra portal → App registrations | [ ] |
| Redirect URI set to Odoo OAuth callback (`/auth_oauth/signin`) | Entra portal | [ ] |
| Graph delegated `User.Read` configured | Entra portal | [ ] |
| Odoo `auth_oauth` provider fields wired | `addons/ipai/ipai_odoo_copilot/data/ir_config_parameter.xml` | [ ] |
| Emergency admin / break-glass access documented | `docs/operations/ODOO_COPILOT_RUNBOOK.md` §Break Glass | [ ] |

### B.2 Foundry / Azure runtime identity

| Check | File target | Status |
|-------|-------------|--------|
| Foundry project identity has `Search Index Data Reader` on `srch-ipai-dev` | `az role assignment create` / Bicep | [ ] |
| Foundry project identity has `Cognitive Services OpenAI User` on `oai-ipai-dev` | `az role assignment create` / Bicep | [ ] |
| Gateway identity and secrets/env ownership documented | `agents/foundry/.../runtime-contract.md` §Auth Chain | [ ] |
| No runtime depends on manual portal-only secrets | `agents/foundry/.../env-modes.md` | [ ] |

### B.3 Azure DevOps automation identity

| Check | File target | Status |
|-------|-------------|--------|
| `sp-ipai-azdevops` added to Azure DevOps org | `ssot/azure/azure_devops.yaml` | [ ] |
| License/access level assigned | ADO portal | [ ] |
| Project group membership is least-privilege | ADO portal | [ ] |
| PAT-free path preferred for automation | `ssot/governance/ai-consolidation-foundry.yaml` | [ ] |

---

## C. Odoo Copilot Runtime — Production Hardening

### C.1 Blockers (must fix before internal beta)

| Blocker | Fix | File target | Status |
|---------|-----|-------------|--------|
| `action_execute()` is a stub | Implement as hard fail-closed (raise error, log audit) or remove | `addons/ipai/ipai_odoo_copilot/models/tool_executor.py` | [ ] |
| `ipai.copilot.audit` model missing | Create model with fields: user_id, prompt, response_excerpt, environment_mode, blocked, reason, source, surface | `addons/ipai/ipai_odoo_copilot/models/copilot_audit.py` | [ ] |
| Rate limiting not enforced | Add HTTP rate limiting (10 req/min per user) to gateway controller | `addons/ipai/ipai_odoo_copilot/controllers/main.py` | [ ] |
| Request validation incomplete | Validate context envelope schema server-side before dispatch | `addons/ipai/ipai_odoo_copilot/models/tool_executor.py` §execute_tool | [ ] |
| Company scoping too loose | Enforce `company_id` from context envelope on all record reads | `addons/ipai/ipai_odoo_copilot/models/tool_executor.py` §_validate_company_scope | [ ] |
| Assistant claims capabilities it lacks | System prompt v2.1.0 addresses this — verify at runtime | `agents/foundry/.../system-prompt.md` | [x] |

### C.2 Retrieval contract

| Check | File target | Status |
|-------|-------------|--------|
| Retrieval lane order defined: (1) Odoo context → (2) KB docs → (3) bounded web | `agents/workflows/odoo_docs_assist.yaml` | [x] |
| If retrieval unavailable, assistant says "runtime not wired" not "I can't search" | `agents/foundry/.../system-prompt.md` §Retrieval Truthfulness | [x] |
| Citations/source indicators visible in UI | `addons/ipai/ipai_odoo_copilot/static/src/xml/copilot_systray.xml` — needs citation rendering | [ ] |

---

## D. Foundry Stage 3 Wiring

### D.1 Retrieval / Knowledge — `odoo-docs` index

| Step | Action | Resource | Status |
|------|--------|----------|--------|
| D.1.1 | Decide: dedicated `odoo18-docs` index vs shared `ipai-knowledge-index` | `agents/foundry/.../retrieval-grounding-contract.md` | [ ] |
| D.1.2 | Create AI Search index with schema | `infra/azure/modules/ai-search-index.bicep` | [ ] |
| D.1.3 | Configure vector search (semantic ranker + embedding field) | Index schema | [ ] |
| D.1.4 | Wire embedding model (`text-embedding-3-small` via `oai-ipai-dev`) | `agents/knowledge/registry.yaml` §shared | [ ] |
| D.1.5 | Run ingestion: `odoo/documentation@19.0` → chunk RST → embed → push | `apps/odoo-docs-kb/service.py` | [ ] |
| D.1.6 | Verify chunk count (target >= 100 for GROUNDED_ADVISORY gate) | `scripts/ai-search/validate-index.py` | [ ] |
| D.1.7 | Run retrieval smoke test (>= 80% hit rate) | `agents/tests/` pattern | [ ] |

**Exit**: `odoo-docs` indexed, queryable, semantic search decision explicit.

### D.2 Foundry connections and endpoint

| Step | Action | Resource | Status |
|------|--------|----------|--------|
| D.2.1 | Create Foundry → AI Search connection | Foundry portal or SDK | [ ] |
| D.2.2 | Create Foundry → Azure OpenAI connection (for embeddings) | Foundry portal or SDK | [ ] |
| D.2.3 | Attach `odoo18-docs` index as knowledge source on agent | Foundry portal | [ ] |
| D.2.4 | Publish one Foundry **online endpoint** | Foundry portal or SDK | [ ] |
| D.2.5 | Wire gateway env/config to Foundry endpoint URL | `addons/ipai/ipai_odoo_copilot/data/ir_config_parameter.xml` | [ ] |
| D.2.6 | Verify gateway calls the endpoint (not just deployed, actually serving) | `foundry_service.py` §test_connection | [ ] |

**Exit**: Foundry endpoint exists, gateway is wired, end-to-end call verified.

### D.3 Model contract reconciliation

| Property | Spec (`metadata.yaml`) | Azure Reality | Decision | Status |
|----------|----------------------|---------------|----------|--------|
| Model | `gpt-4.1` | `gpt-4.1` (remote-state 2026-03-15) | Verify current state | [ ] |
| Search index | `ipai-knowledge-index` | empty (0 indexes with `odoo-docs`) | Must populate | [ ] |
| Search connection | `srchipaidev8tlstu` | Connection exists, no active index | Must wire | [ ] |

- [ ] If deployed model is `gpt-4.1-mini`, update `metadata.yaml` and `runtime-contract.md`
- [ ] Record decision in `ssot/governance/ai-consolidation-foundry.yaml`

**Launch rule**: Do NOT call Odoo Copilot "grounded" until D.1-D.2 entire chain is live.

---

## E. Databricks + Genie

### E.1 Semantic / data prerequisites

| Check | File target | Status |
|-------|-------------|--------|
| All exposed datasets are curated and business-safe | `databricks/bundles/sql_warehouse/src/sql/marts/` | [ ] |
| Unity Catalog ownership/permissions correct | `databricks/bundles/foundation_python/databricks.yml` | [ ] |
| SQL warehouse backing Genie defined and cost-owned | `infra/azure/modules/databricks.bicep` | [ ] |
| Sample queries / business definitions / field descriptions completed | `databricks/bundles/sql_warehouse/` | [ ] |
| Only approved datasets exposed to end users | UC grants: `databricks/bundles/lakeflow_ingestion/resources/permissions/uc_grants.yml` | [ ] |
| KPI names match business language, not raw technical names | Gold mart column names | [ ] |

### E.2 Functional gates

| Check | Evidence | Status |
|-------|----------|--------|
| Genie answers top 20 finance/ops questions correctly | `docs/evidence/<stamp>/genie/` | [ ] |
| Answers trace back to approved datasets | Query audit | [ ] |
| No raw transactional writeback implied | Genie config | [ ] |
| Dashboards and Genie scopes aligned | Power BI + Genie scope audit | [ ] |

### E.3 Positioning gate

- [ ] Users understand: **Genie = analytics assistant**, **Odoo Copilot = process/transactional assistant**
  - File: `docs/operations/ODOO_COPILOT_RUNBOOK.md` §Scope Boundaries

---

## F. Document Intelligence Assistant

### F.1 Input pipeline

| Check | File target | Status |
|-------|-------------|--------|
| Document ingress paths fixed (email, upload, OCR drop, API) | `docs/architecture/COPILOT_TARGET_STATE.md` §Document Processing | [ ] |
| Supported document classes enumerated (invoices, receipts, BIR forms, statements, contracts) | `agents/foundry/.../tooling-matrix.md` | [ ] |
| Confidence thresholds and human review rules defined | `agents/foundry/.../guardrails.md` | [ ] |

### F.2 Extraction + review

| Check | File target | Status |
|-------|-------------|--------|
| Extracted fields map to canonical business objects | Odoo field mapping doc | [ ] |
| Review queue exists for low-confidence docs | Odoo workflow | [ ] |
| Duplicates and malformed docs handled | Controller validation | [ ] |
| Storage/retention policy defined | `ssot/governance/` | [ ] |
| Sensitive data handling defined | `agents/foundry/.../guardrails.md` | [ ] |

### F.3 Posting/automation safety

- [ ] No auto-posting to accounting without review
- [ ] Approval path exists for exceptions
- [ ] Evidence and source document links preserved

---

## G. Business Acceptance

### G.1 Odoo Copilot — top operator scenarios

| Scenario | Expected behavior | Pass? |
|----------|-------------------|-------|
| Explain a process | Cites Odoo docs or KB, structured answer | [ ] |
| Answer record-aware question | Uses Lane 1 (read_record/search_records) | [ ] |
| Cite docs/runtime source | Response includes citation from KB or web | [ ] |
| Refuse unsupported write | Returns advisory-mode message, no mutation | [ ] |
| Route a proposal safely | Surfaces as draft/proposal, no direct write | [ ] |

Evidence: `docs/evidence/<stamp>/copilot-beta/`

### G.2 Genie — top analytics scenarios

| Scenario | Expected behavior | Pass? |
|----------|-------------------|-------|
| Cash position | Returns current AP/AR/cash from gold marts | [ ] |
| AR aging trend | Returns aging buckets over time | [ ] |
| Spend by vendor | Returns vendor spend ranked | [ ] |
| Project margin | Returns project profitability from gold mart | [ ] |
| Close readiness | Returns close task completion status | [ ] |
| Collections risk | Returns overdue AR with risk indicators | [ ] |

Evidence: `docs/evidence/<stamp>/genie-beta/`

### G.3 Document Intelligence — top document scenarios

| Scenario | Expected behavior | Pass? |
|----------|-------------------|-------|
| Invoice extraction | Fields extracted, mapped to `account.move` | [ ] |
| Receipt extraction | Fields extracted, linked to expense | [ ] |
| BIR form extraction | Form type identified, fields mapped | [ ] |
| Low-confidence handoff | Routed to review queue, not auto-posted | [ ] |
| Duplicate handling | Detected and flagged, not double-posted | [ ] |

Evidence: `docs/evidence/<stamp>/docai-beta/`

---

## H. Observability, Rollback, and Support

### H.1 Observability

| Check | File target | Status |
|-------|-------------|--------|
| Structured logs for gateway, Foundry, OCR, retrieval | `infra/azure/modules/app-insights.bicep` | [ ] |
| Trace IDs across request path | `agents/foundry/.../telemetry-contract.md` | [ ] |
| Token, query, and latency metrics captured | App Insights custom metrics | [ ] |
| Error dashboards exist | Power BI or App Insights workbook | [ ] |

### H.2 Rollback

| Feature flag | Mechanism | File target | Status |
|-------------|-----------|-------------|--------|
| Copilot visibility | `ipai_copilot.enabled` ir.config_parameter | `addons/ipai/ipai_odoo_copilot/data/ir_config_parameter.xml` | [x] |
| Retrieval on/off | `ipai_copilot.retrieval_enabled` | ir.config_parameter (to create) | [ ] |
| Foundry endpoint switch | `ipai_copilot.foundry_endpoint` | ir.config_parameter | [x] |
| Document automation on/off | `ipai_copilot.docai_enabled` | ir.config_parameter (to create) | [ ] |

- [ ] Rollback owner named in `docs/operations/ODOO_COPILOT_RUNBOOK.md`
- [ ] Downgrade path tested (disable → verify copilot stops responding → re-enable)

### H.3 Support

- [ ] Known issues doc: `docs/operations/ODOO_COPILOT_RUNBOOK.md` §Common Issues (exists, needs update)
- [ ] Support owner / escalation path: `docs/operations/ODOO_COPILOT_RUNBOOK.md` §Escalation (exists)
- [ ] Evidence pack location: `docs/evidence/<stamp>/copilot-beta/`

---

## I. FinOps and Value Proof

### I.1 Unit economics

| Metric | Formula | File target |
|--------|---------|-------------|
| Cost per copilot session | Total token cost / session count | Dashboard |
| Cost per grounded answer | (Embedding + Search + LLM tokens) / grounded answer count | Dashboard |
| Cost per document processed | (DocAI + storage + review time) / doc count | Dashboard |
| Genie query volume and warehouse cost | Queries × warehouse DBU cost | Databricks cost dashboard |

- [ ] Define in: `ssot/governance/platform-capabilities-unified.yaml` §copilot.economics

### I.2 Business impact metrics

| Metric | Measurement method | Baseline |
|--------|-------------------|----------|
| Time saved on doc lookup | Before/after survey | Establish before launch |
| Answer quality improvement | Eval score delta | Stage 2 eval = baseline |
| ERP user onboarding speed | Time-to-first-task | Establish before launch |
| Repeated support question reduction | Support ticket volume | Establish before launch |
| Document encoding effort reduction | Manual entry time delta | Establish before launch |
| Reporting speed improvement | Time-to-answer for analytics questions | Establish before launch |

### I.3 Adoption metrics

- [ ] Unique users/week (target: >= 5 within 30 days)
- [ ] Sessions/user/week
- [ ] Copilot vs Genie vs DocAI split

### I.4 Model/pricing decision gate

- [ ] Explicit decision: `gpt-4.1` vs `gpt-4.1-mini` for launch quality
  - File: `agents/foundry/.../metadata.yaml` §model_deployment
- [ ] Criteria for when to move to higher-cost model documented
- [ ] Criteria for when to consider PTU/provisioned economics documented
- [ ] Record in: `ssot/governance/platform-capabilities-unified.yaml` §pricing

---

## Go-Live Decision Matrix

### Can go live NOW as internal beta (all must be true)

- [ ] Odoo Copilot remains read-only advisory
- [ ] Write paths stay disabled
- [ ] Trusted users only
- [ ] Audit model exists and persists events (**blocker**)
- [ ] Rate limiting enforced (**blocker**)
- [ ] Request validation enforced (**blocker**)
- [ ] Company scoping enforced (**blocker**)
- [ ] Retrieval is either working or honestly declared absent
- [ ] Genie limited to curated analytics
- [ ] Document Intelligence is human-in-the-loop

### Cannot go live as GA (any of these still true = blocked)

- [ ] No audit model
- [ ] No rate limiting
- [ ] No company scoping
- [ ] No Foundry endpoint
- [ ] No `odoo-docs` indexing
- [ ] No Search/OpenAI Foundry connections
- [ ] No rollback/observability
- [ ] Model contract drift unresolved

---

## Recommended Launch Order

### Phase 1 — Odoo Copilot internal beta

Ship first. Prerequisites:

1. Fix C.1 blockers (audit, rate limit, validation, scoping)
2. Odoo SSO (Entra app registration)
3. Read-only copilot with retrieval over `odoo-docs`
4. No writes
5. Strict monitoring

File targets: `addons/ipai/ipai_odoo_copilot/`, `agents/foundry/.../`

### Phase 2 — Document Intelligence assisted intake

Ship second. Prerequisites:

1. OCR/extraction pipeline wired
2. Review queues in Odoo
3. No autonomous posting to accounting
4. Confidence thresholds enforced

File targets: `addons/ipai/ipai_odoo_copilot/` (DocAI tools), `infra/azure/` (Document Intelligence)

### Phase 3 — Genie analytics rollout

Ship third. Prerequisites:

1. Gold marts populated with curated data
2. Business definitions and sample queries completed
3. Dashboard-adjacent NLQ
4. Clear boundary: Genie = analytics, Copilot = ERP

File targets: `databricks/bundles/`, `docs/architecture/DATABRICKS_BUNDLES_BASELINE.md`

### Phase 4 — Controlled write actions

Only after all of:

1. Audit model operational with retention
2. Rate limiting enforced
3. Company scoping proven
4. Retrieval maturity (>= 80% hit rate)
5. Approval/confirmation flow implemented
6. Rollback proof documented

File targets: `addons/ipai/ipai_odoo_copilot/models/tool_executor.py` §Stage 2 tools

---

## Cross-Reference: File Target Map

| Domain | File | Section |
|--------|------|---------|
| Launch state | `docs/architecture/ODOO_COPILOT_PUBLISHABLE_STATE.md` | A |
| Runtime contract | `agents/foundry/ipai-odoo-copilot-azure/runtime-contract.md` | B, D |
| Agent metadata | `agents/foundry/ipai-odoo-copilot-azure/metadata.yaml` | D.3, I.4 |
| System prompt | `agents/foundry/ipai-odoo-copilot-azure/system-prompt.md` | C.1, C.2 |
| Tool definitions | `agents/foundry/ipai-odoo-copilot-azure/tool-definitions.json` | C.1, D |
| Tool executor | `addons/ipai/ipai_odoo_copilot/models/tool_executor.py` | C.1 |
| Audit model | `addons/ipai/ipai_odoo_copilot/models/copilot_audit.py` | C.1 |
| Gateway controller | `addons/ipai/ipai_odoo_copilot/controllers/main.py` | C.1 |
| Retrieval contract | `agents/foundry/.../retrieval-grounding-contract.md` | D.1 |
| Retrieval workflow | `agents/workflows/odoo_docs_assist.yaml` | C.2 |
| KB registry | `agents/knowledge/registry.yaml` | D.1 |
| KB source | `agents/knowledge/odoo18_docs/source.yaml` | D.1 |
| Eval thresholds | `agents/evals/odoo-copilot/thresholds.yaml` | G |
| Stage 3 thresholds | `agents/evals/odoo-copilot/stage3-retrieval-thresholds.yaml` | G.1 |
| Stage 3 checklist | `docs/architecture/COPILOT_STAGE3_CHECKLIST.md` | D |
| Runbook | `docs/operations/ODOO_COPILOT_RUNBOOK.md` | B.1, H |
| Go-live plan | `docs/delivery/GO_LIVE_ACCELERATION_PLAN.md` | Parent |
| SSOT governance | `ssot/governance/platform-capabilities-unified.yaml` | I |
| SSOT AI | `ssot/governance/ai-consolidation-foundry.yaml` | D.3 |
| Genie / Databricks | `databricks/bundles/` | E |
| Gold marts | `databricks/bundles/sql_warehouse/src/sql/marts/` | E.1 |
| UC grants | `databricks/bundles/lakeflow_ingestion/resources/permissions/uc_grants.yml` | E.1 |
| DocAI | `infra/azure/modules/` (Document Intelligence) | F |
| Guardrails | `agents/foundry/.../guardrails.md` | F.1, F.2 |
| Telemetry | `agents/foundry/.../telemetry-contract.md` | H.1 |
| App Insights | `infra/azure/modules/app-insights.bicep` | H.1 |
| Config params | `addons/ipai/ipai_odoo_copilot/data/ir_config_parameter.xml` | A, H.2 |
| UX (systray) | `addons/ipai/ipai_odoo_copilot/static/src/xml/copilot_systray.xml` | C.2 |
| Evidence | `docs/evidence/<stamp>/copilot-beta/` | G, H.3 |

---

*Last updated: 2026-03-23*
