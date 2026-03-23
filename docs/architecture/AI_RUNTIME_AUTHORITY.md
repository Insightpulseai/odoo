# AI Runtime Authority — Odoo Copilot

> Blunt status block. Do not soften or overstate.

## Current Stage: Stage 1 — Internal Beta (Advisory Only)

| Attribute | Value |
|-----------|-------|
| **Release stage** | `internal_beta` |
| **Capability mode** | `advisory_read_only` |
| **Write actions** | **Disabled** (fail-closed, config-gated) |
| **Grounding** | Partial (KB defined, retrieval not wired e2e) |
| **Tenant safety** | Single-company only |
| **Allowed users** | Internal / trusted only |
| **Publishable** | Yes, narrowly |
| **GA-ready** | No |

## What is supported

- Read-only advisory responses
- Chat via systray (OWL widget)
- SSE streaming
- Conversation persistence with audit trail
- Per-user rate limiting (20 req/60s)
- Request validation (8000 char, context sanitization)
- Company-scoped conversation access
- Dual backend (Azure OpenAI direct + custom gateway)

## What is NOT supported — do not claim otherwise

| Claim | Status | Blocker |
|-------|--------|---------|
| Production write-capable | **No** | `action_execute()` fail-closed; `write_actions_enabled=False` |
| Multi-tenant safe | **No** | Company scoping added but not multi-tenant tested |
| Public rollout | **No** | No eval pack, no privacy docs, no Partner Center listing |
| Enterprise GA | **No** | Entra identity not wired, no SLO baseline |
| Grounded retrieval | **Partial** | KB spec + skill + workflow defined; Azure AI Search index not populated |
| Action execution | **No** | Handlers implemented but gated behind fail-closed flag |
| Marketplace listing | **No** | 13-item gap matrix unresolved |

## Stage 2 completions (2026-03-23)

1. Audit model (`ipai.copilot.audit`) — 15 event types, append-only
2. Action dispatch — 6 per-type handlers with JSON payload parsing
3. Fail-closed write gate — `ipai.copilot.write_actions_enabled` config parameter
4. Rate limiting — per-user sliding window on `/chat` and `/stream`
5. Request validation — message length, context field sanitization
6. Company scoping — user + company access check on conversations
7. Streaming disconnect handling — `GeneratorExit` caught, partial content persisted
8. `mail.thread` on conversations — chatter audit trail
9. SQL constraints — `gateway_correlation_id` unique, `request_id` unique
10. ACLs for action_queue and audit models
11. Version bump to `19.0.2.0.0`

## Stage 3 Authority Boundary

Stage 3 = Marketplace Readiness. The copilot's approved retrieval lanes post-Stage-3:

1. **Odoo runtime context** (Lane 1) — active record, company, user role, locale
2. **Odoo docs KB** (Lane 2) — curated Odoo 19 docs in `odoo-docs-kb` Azure AI Search index
3. **Bounded web retrieval** (Lane 3) — allowed domains only (`odoo.com`), max 3 uses per query

The copilot is no longer a static wrapper. Grounded retrieval is live via the `odoo-docs-kb` index (26 chunks, vector-enabled, HNSW cosine).

### Stage 3 completions (2026-03-23)

| Item | Status | Evidence |
|------|--------|----------|
| Model contract | **Resolved** | `gpt-4.1` deployed to `oai-ipai-dev` (Standard, 10 TPM) |
| `odoo-docs-kb` index | **Created** | 26 chunks, vector search (1536d, HNSW), `odoo-docs` scope |
| RBAC | **Assigned** | Project + endpoint identities → Search Reader + OpenAI User |
| Foundry connections | **Created** | `srch-ipai-dev-connection` (CognitiveSearch) + `oai-ipai-dev-connection` (AzureOpenAI) |
| Foundry endpoint | **Live** | `ipai-copilot-endpoint` → `https://ipai-copilot-endpoint.eastus2.inference.ml.azure.com/score` |
| Gateway deployed | **Live** | `ipai-copilot-gateway` (internal, port 8088, `gpt-4.1` deployment) |
| Retrieval smoke test | **Pass** | "Philippine withholding tax BIR" → 3 grounded results (score 7.33) |

### Stage 3 remaining blockers

1. Teams/M365 app package not created
2. Evaluation pack not created (no formal quality suite with thresholds)
3. Privacy/data handling documentation missing
4. Partner Center submission assets not prepared
5. SLO baseline not established
6. Full Odoo docs corpus expansion (26 seed chunks → target 7000+)

## Release gate order (updated)

1. ~~Model contract~~ — **Done** (gpt-4.1 deployed)
2. ~~Retrieval grounding~~ — **Done** (odoo-docs-kb index, vector search)
3. ~~RBAC~~ — **Done** (project + endpoint → Search + OpenAI)
4. ~~Foundry connections~~ — **Done** (Search + OpenAI)
5. ~~Foundry endpoint~~ — **Done** (ipai-copilot-endpoint live)
6. ~~Gateway wired~~ — **Done** (env vars → gpt-4.1)
7. Create eval pack — formal pass/fail quality thresholds
8. Expand Odoo docs corpus — full documentation crawl + index
9. Enable write actions (flip config flag) — only after full test
10. Package for Teams — M365 manifest
11. Submit to Partner Center — 4-week review cycle

## Foundry Template Adoption Map

Product surfaces map to specific Foundry templates in sequence. Multi-agent templates are deferred until single-agent/workflow surfaces are stable.

| Product Surface | Foundry Template | Phase |
|----------------|------------------|-------|
| `landing_public_assistant` | Get Started with AI Chat | Phase 1 |
| `odoo_copilot_internal_beta` | Get started with AI agents | Phase 2 |
| `odoo_copilot_workflow_control` | Build your conversational agent | Phase 2 |
| `document_intelligence_lane` | Multi-modal content processing | Phase 3 |
| `production_hardening` | Deploy your AI application in production | Phase 4 |

**Deferred** (not first-wave go-live):
- Multi-Agent Workflow Automation
- Create a multi-agent Release Manager Assistant
- Agentic applications for unified data foundation

These are deferred until: eval pack exists, docs corpus is broad, SLO baseline exists, and write gates are policy-safe.

## Model Tiering Policy

Model selection is explicit per assistant surface. Groundedness is enforced through retrieval, routing, and evaluation policy, not model choice alone.

| Surface | Primary Model | Escalation / Secondary | Rationale |
|---------|--------------|----------------------|-----------|
| Public landing assistant | `gpt-5-mini` | `gpt-5.4` | High-throughput public advisory |
| Internal Odoo Copilot | `gpt-5.2` | `gpt-5.4` | Best product-quality / latency / cost |
| Coding / release assistant | `gpt-5.4` | `gpt-5.2-codex` | Top coding + strong reasoning fallback |
| Data intelligence assistant | `gpt-5.2` | `gpt-5-mini` (batch) | Governed Q&A + cheap triage |
| Judge / eval lane | `gpt-5.4` | `gpt-5-pro` (benchmark only) | Evaluation-first, not inline traffic |

**Note:** `gpt-4.1` remains the currently deployed model on `oai-ipai-dev`. The tiering policy above is the target state — migration to GPT-5 tier models happens as deployments become available on the Foundry runtime.

## Foundry Go-Live Tool Envelope

Four tool profiles, each with explicit enabled tools, auth mode, and action policy.

### `landing_public_assistant`

- **Enabled tools:** None (no direct MCP action tools)
- **Action mode:** None
- **Tenant scope:** None
- **Policy:** Docs-grounded only, public advisory mode, no tenant access, no actions

### `odoo_copilot_internal_beta`

- **Enabled tools:** Foundry MCP Server (preview), GitHub, Vercel, Azure DevOps MCP Server (preview), Azure Managed Grafana
- **Action mode:** Fail-closed
- **Tenant scope:** Trusted internal
- **Auth:** OAuth for human-scoped tools, managed identity for Azure-native

### `data_intelligence_assistant`

- **Enabled tools:** Azure Databricks Genie, Azure Database for PostgreSQL, Supabase, Azure Managed Grafana
- **Action mode:** Read-only
- **Tenant scope:** Governed data
- **Auth:** Managed identity for Azure-native

### `ops_release_assistant`

- **Enabled tools:** GitHub, Vercel, Azure DevOps MCP Server (preview), Azure MCP Server, Azure Managed Grafana, Foundry MCP Server (preview)
- **Action mode:** Controlled
- **Tenant scope:** Ops internal
- **Auth:** OAuth for dev tools, managed identity for Azure-native

### Deferred tools (not first-wave go-live)

- Work IQ (Mail, Calendar, Teams, SharePoint, Word, OneDrive, Copilot)
- Microsoft 365 Admin Center
- Dataverse, Pipedream, ClickUp, Atlassian
- Infobip channels, Morningstar, Marketnode, MiHCM
- Azure Managed Redis (enable after first-wave stability)

### Auth policy

- **Managed identity:** Azure-native local MCP servers, platform/resource context
- **OAuth:** Human-scoped work tools (GitHub, Vercel, Azure DevOps MCP)
- **Avoid key-based:** For first-wave go-live unless unavoidable

## Secondary Provider Policy

Gemini API is allowed as a secondary provider for public, advisory-only, non-tenant-aware surfaces (landing-page assistants, prototype research helpers). It is not the primary runtime/control plane for authenticated Odoo Copilot, governed ops assistants, or production release workflows. Those remain on the Foundry-first path.

## SSOT references

- Module: `addons/ipai/ipai_odoo_copilot/` (v19.0.2.0.0)
- Agent SSOT: `ssot/agents/diva_copilot.yaml`
- Stage 3 contract: `ssot/ai/foundry_stage3.yaml`
- Model contract: `ssot/ai/models.yaml`
- Spec bundle: `spec/ipai-odoo-copilot-azure/`
- Target state: `ssot/agents/copilot_agents_target_state.yaml`
- Build plan: `ssot/agents/copilot_agents_build_plan.yaml`

---

*Last updated: 2026-03-23*
