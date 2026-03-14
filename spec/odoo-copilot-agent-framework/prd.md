# PRD — Odoo Copilot Agent Framework

## Problem

The current AI consolidation (PRs #594-#598) established one Foundry agent with five capability modes. But the single-agent/five-mode split conflates user-facing advisory with internal ops, and read-only with write-capable flows. This creates:

- No isolation between customer-facing and internal-only contexts
- Write access modes (Transaction, Creative) share instruction space with read-only modes
- No deterministic routing — mode selection relies on prompt classification
- Capability packs (Databricks, fal, Marketing) have no defined attachment points
- No evaluation framework per agent role

## Solution

Split the single agent into **three logical agents + one deterministic router**, each with bounded scope, dedicated evaluation criteria, and clear tool/write boundaries.

## Architecture

```
                    ┌──────────────────────────────────────────────┐
                    │  Microsoft Foundry (data-intel-ph)            │
                    │  Physical agent: ipai-odoo-copilot-azure      │
                    │                                                │
                    │  ┌─────────────────────────────────────────┐  │
                    │  │ Router (deterministic, no LLM)          │  │
                    │  │ Rules: channel + model + role + intent   │  │
                    │  └────┬──────────┬──────────┬──────────────┘  │
                    │       │          │          │                  │
                    │  ┌────▼────┐ ┌───▼────┐ ┌──▼──────────┐     │
                    │  │Advisory │ │  Ops   │ │  Actions    │     │
                    │  │(user)   │ │(internal│ │(controlled  │     │
                    │  │read-only│ │read-only│ │writes)      │     │
                    │  └─────────┘ └────────┘ └─────────────┘     │
                    │                                                │
                    │  Capability Packs (attached inside agents):    │
                    │  ├── Databricks Intelligence (Advisory+Ops)    │
                    │  ├── fal Creative Production (Actions)         │
                    │  └── Marketing Strategy (Advisory)             │
                    └──────────────────────────────────────────────┘
                                       │
                           Responses API (/openai/v1/)
                                       │
          ┌────────────────────────────┼────────────────────────┐
          │                            │                        │
    ┌─────▼──────┐          ┌─────────▼────────┐     ┌────────▼──────┐
    │ SDK Direct │          │ REST Direct      │     │ APIM Gateway  │
    │ (internal  │          │ (n8n, adapters)  │     │ (enterprise   │
    │  services) │          │                  │     │  front door)  │
    └────────────┘          └──────────────────┘     └───────────────┘
```

## Target top-level components

| Component | Form | Purpose |
|---|---|---|
| `ipai-odoo-copilot-advisory` | Foundry prompt agent | user-facing grounded Q&A, guidance, strategy |
| `ipai-odoo-copilot-ops` | Agent Framework agent | internal diagnostics, read-only operational inspection |
| `ipai-odoo-copilot-actions` | Agent Framework agent | controlled execution and bounded writes |
| `ipai-odoo-copilot-router` | Agent Framework workflow | deterministic routing, approvals, checkpoints, handoffs |

## Agent matrix

| Component | Primary responsibility | Core tools / packs | Allowed actions | Hard blocks | Required evaluations |
|---|---|---|---|---|---|
| `ipai-odoo-copilot-advisory` | user-facing Q&A, grounded explanation, strategy guidance | Azure AI Search / Foundry knowledge, Marketing Strategy & Insight Pack, Databricks Intelligence Pack | explain, summarize, recommend, compare, hand off | no writes, no admin/security changes, no direct publish/export, no finance execution | Task Completion, Task Adherence, Intent Resolution, Relevance, Groundedness where applicable |
| `ipai-odoo-copilot-ops` | internal diagnostics, read-only operational inspection | read-only Odoo tools, Databricks monitoring/health, infra/runtime reads | inspect, diagnose, compare state, summarize incidents, propose remediation | no record mutation, no secret changes, no role changes, no uncontrolled job execution | Task Completion, Task Adherence, Tool Selection, Tool Call Success, Tool Output Utilization |
| `ipai-odoo-copilot-actions` | controlled execution and bounded writes | approved Odoo write tools, approved Databricks job/app actions, fal Creative Production Pack actions | create/update allowed records, trigger approved jobs, launch approved creative runs, prepare exports, write evidence | no unrestricted writes, no destructive ops, no policy bypass, no silent batch execution | Tool Selection, Tool Input Accuracy, Tool Call Success, approval compliance, unauthorized-action refusal |
| `ipai-odoo-copilot-router` | deterministic routing, approvals, handoffs, checkpointing | workflow graph, approval steps, evidence correlation | route, pause for approval, resume, hand off, checkpoint, collect trace context | no free-form business reasoning, no broad vendor logic, no direct domain mutation | routing correctness, handoff success, approval compliance, end-to-end task completion |

## Three Agents

### 1. Advisory Agent (User-Facing, Read-Only)

| Attribute | Value |
|-----------|-------|
| **Audience** | End users, portal visitors, livechat |
| **Write access** | None |
| **Foundry tools** | `search_records`, `read_record`, `search_knowledge`, `web_search` |
| **Memory** | `user_profile` (personalization) |
| **Replaces modes** | Ask, Livechat |
| **Capability packs** | Databricks Intelligence, Marketing Strategy |
| **Evaluation** | Groundedness ≥ 0.8, Relevance ≥ 0.85, Citation accuracy ≥ 0.9 |
| **Guardrails** | No PII in responses, no financial advice disclaimers, cite sources |

### 2. Ops Agent (Internal, Read-Only)

| Attribute | Value |
|-----------|-------|
| **Audience** | Internal staff, admin, finance team |
| **Write access** | None |
| **Foundry tools** | `search_records`, `read_record`, `search_knowledge`, `code_interpreter`, `file_search` |
| **Memory** | `chat_summary` (session continuity) |
| **Replaces modes** | Authoring (read/analysis portion) |
| **Capability packs** | Databricks Intelligence |
| **Evaluation** | Groundedness ≥ 0.85, Coherence ≥ 0.9, Data accuracy ≥ 0.95 |
| **Guardrails** | No external data leakage, internal-only context, audit all queries |

### 3. Actions Agent (Controlled Writes)

| Attribute | Value |
|-----------|-------|
| **Audience** | Authorized users with write roles |
| **Write access** | Bounded CRUD (model allowlist + field allowlist + state constraints) |
| **Foundry tools** | All read tools + `create_draft`, `create_record`, `update_record`, `execute_action`, `image_generation`, `code_interpreter` |
| **Memory** | `chat_summary` (multi-step transaction continuity) |
| **Replaces modes** | Authoring (draft creation), Transaction, Creative |
| **Capability packs** | fal Creative Production |
| **Evaluation** | Action correctness ≥ 0.95, Safety (no unauthorized writes) = 1.0 |
| **Guardrails** | Approval gates, undo support, draft-first default, model/field allowlists |

## Deterministic Router

Routes requests to the correct agent without LLM inference:

| Signal | Advisory | Ops | Actions |
|--------|----------|-----|---------|
| Channel = livechat/portal | Yes | — | — |
| Channel = internal + intent = read | — | Yes | — |
| Channel = internal + intent = write | — | — | Yes |
| User role ∉ write_roles | Yes | Yes | Blocked |
| Model in write_allowlist | — | — | Yes |
| Explicit mode override | Honored | Honored | Honored |

## Capability packs (cross-agent attachment)

| Capability pack | Advisory | Ops | Actions | Router |
|---|---:|---:|---:|---:|
| Databricks Intelligence Pack | Yes | Yes | Yes | Yes |
| fal Creative Production Pack | Yes | Yes | Yes | Yes |
| Marketing Strategy & Insight Pack | Yes | Yes | Light | No |

## Foundry + Agent Framework split

- Foundry is the control plane for prompt agents, datasets, evaluations, tracing, and project-scoped resources.
- Agent Framework is the execution plane for graph workflows, checkpointing, middleware, and multi-agent orchestration.
- Do not add more than 3 agents + 1 workflow until eval coverage and tracing are stable.

## Capability Packs (Detail)

### Databricks Intelligence Pack

| Attribute | Value |
|-----------|-------|
| **Attaches to** | Advisory, Ops |
| **Tools** | `databricks_sql_query`, `databricks_unity_search`, `databricks_dashboard_embed` |
| **Credentials** | `DATABRICKS_HOST`, `DATABRICKS_TOKEN` (Key Vault) |
| **Degrades** | Pack disabled if credentials absent; agents still work |
| **Source refs** | Databricks SQL Connector, Unity Catalog, Genie, Lakeview |

### fal Creative Production Pack

| Attribute | Value |
|-----------|-------|
| **Attaches to** | Actions |
| **Tools** | `fal_image_generate`, `fal_video_generate`, `fal_style_transfer` |
| **Credentials** | `FAL_KEY` (Key Vault) |
| **Degrades** | Falls back to Foundry built-in `image_generation` (DALL-E 3) |
| **Source refs** | fal.ai model catalog, UGC generation patterns |

### Marketing Strategy & Insight Pack

| Attribute | Value |
|-----------|-------|
| **Attaches to** | Advisory |
| **Tools** | `web_search` (existing), `search_knowledge` (brand guidelines RAG) |
| **Credentials** | None (uses existing Foundry built-ins) |
| **Degrades** | N/A (no external credentials needed) |
| **Source refs** | Smartly (creative automation), Quilt.AI (cultural intelligence), LIONS Marketing Assistant (effectiveness), Data Intelligence (analytics) |

## Integration Modes

| Mode | Surface | Auth | When |
|------|---------|------|------|
| **SDK Direct** | `azure-ai-projects` 2.x + `OpenAI()` | `DefaultAzureCredential` | Internal services (Odoo bridge, MCP server) |
| **REST Direct** | `POST /openai/v1/responses` | API key via project connection | n8n workflows, lightweight adapters |
| **APIM Gateway** | `apim-ipai-dev` → Foundry | OAuth2 / subscription key | Third-party callers, enterprise ingress |

## Endpoints

| Endpoint | URL Pattern | Client |
|----------|-------------|--------|
| Project | `https://data-intel-ph-resource.services.ai.azure.com/api/projects/data-intel-ph` | AIProjectClient |
| OpenAI-compatible | `https://data-intel-ph-resource.openai.azure.com/openai/v1/` | OpenAI() |
| APIM (future) | `https://apim-ipai-dev.azure-api.net/foundry/v1/` | Any HTTP client |

## Acceptance Criteria

1. Router correctly classifies 95%+ of test requests to the right agent
2. Advisory agent passes groundedness ≥ 0.8 on Foundry evaluation suite
3. Ops agent returns no PII to unauthorized callers (100% pass rate)
4. Actions agent refuses writes outside model/field allowlist (100% pass rate)
5. Capability packs degrade gracefully when credentials absent
6. All agent invocations produce App Insights telemetry with user, mode, tools, tokens, latency
7. Multi-agent workflow (expense approval) completes end-to-end with OTel trace
8. No additional Foundry agents created — all modes use `ipai-odoo-copilot-azure`
