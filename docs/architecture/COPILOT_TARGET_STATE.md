# Odoo Copilot — Target State Architecture

> One Odoo Copilot system. 3 agents + 1 router workflow.
> Foundry = control plane. Agent Framework = execution plane.
> APIM = production ingress. Capability packs, not vendor agents.
>
> SSOT: `ssot/agents/agent_capability_matrix.yaml`
> SSOT: `ssot/platform/agent_ingress_matrix.yaml`
> Spec: `spec/odoo-copilot-agent-framework/`

---

## Topology

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         APIM AI Gateway (apim-ipai-dev)                     │
│                         ═══════════════════════════════                     │
│                         Production front door for all callers               │
│                         Auth · Quotas · Throttling · Observability          │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Microsoft Foundry (data-intel-ph)                         │
│                    ════════════════════════════════                          │
│                    Physical agent: ipai-odoo-copilot-azure                   │
│                                                                              │
│  ┌─────────────────────── CONTROL PLANE ──────────────────────────────────┐ │
│  │                                                                         │ │
│  │  Foundry Runtime                                                        │ │
│  │  ├── Prompt agent hosting (Advisory)                                    │ │
│  │  ├── Datasets + evaluation runs                                         │ │
│  │  ├── Tracing + App Insights correlation                                 │ │
│  │  └── Project-scoped resources                                           │ │
│  │                                                                         │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  ┌─────────────────────── EXECUTION PLANE ────────────────────────────────┐ │
│  │                                                                         │ │
│  │  Agent Framework Runtime                                                │ │
│  │  ├── Ops agent (graph-based, checkpointed)                              │ │
│  │  ├── Actions agent (graph-based, approval-gated)                        │ │
│  │  └── Router workflow (deterministic, no LLM)                            │ │
│  │                                                                         │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  ┌─────────────────────── ROUTER ─────────────────────────────────────────┐ │
│  │                                                                         │ │
│  │  ipai-odoo-copilot-router (Agent Framework workflow)                    │ │
│  │  ┌──────────────────────────────────────────────────────────────┐      │ │
│  │  │  Rules: channel + model + user_role + intent                 │      │ │
│  │  │                                                              │      │ │
│  │  │    livechat/portal ──────────► Advisory                      │      │ │
│  │  │    internal + read ──────────► Ops                           │      │ │
│  │  │    internal + write ─────────► Actions                       │      │ │
│  │  │    explicit override ────────► Honored                       │      │ │
│  │  │                                                              │      │ │
│  │  │  Also: approval gates · checkpoints · handoffs · tracing     │      │ │
│  │  └──────────────────────────────────────────────────────────────┘      │ │
│  │                                                                         │ │
│  └─────────────┬───────────────────┬──────────────────┬───────────────────┘ │
│                │                   │                  │                      │
│       ┌────────▼────────┐ ┌───────▼───────┐ ┌───────▼────────┐             │
│       │    ADVISORY     │ │     OPS       │ │    ACTIONS     │             │
│       │  ┌───────────┐  │ │ ┌───────────┐ │ │ ┌───────────┐ │             │
│       │  │ Foundry   │  │ │ │ Agent     │ │ │ │ Agent     │ │             │
│       │  │ prompt    │  │ │ │ Framework │ │ │ │ Framework │ │             │
│       │  │ agent     │  │ │ │ agent     │ │ │ │ agent     │ │             │
│       │  └───────────┘  │ │ └───────────┘ │ │ └───────────┘ │             │
│       │                 │ │               │ │               │             │
│       │  Read-only      │ │ Read-only     │ │ Bounded CRUD  │             │
│       │  User-facing    │ │ Internal      │ │ Approval-gated│             │
│       │                 │ │               │ │               │             │
│       │  PACKS:         │ │ PACKS:        │ │ PACKS:        │             │
│       │  ├ Databricks   │ │ ├ Databricks  │ │ ├ Databricks  │             │
│       │  ├ Marketing    │ │ ├ Marketing   │ │ ├ fal Creative│             │
│       │  └ fal (read)   │ │ └ fal (read)  │ │ └ Marketing*  │             │
│       │                 │ │               │ │   (* = light)  │             │
│       └─────────────────┘ └───────────────┘ └───────────────┘             │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
                                     │
                          Responses API (/openai/v1/)
                                     │
              ┌──────────────────────┼──────────────────────┐
              │                      │                      │
     ┌────────▼─────────┐  ┌────────▼─────────┐  ┌────────▼─────────┐
     │  SDK Direct       │  │  REST Direct      │  │  MCP Servers     │
     │  (Odoo bridge,    │  │  (n8n, adapters,  │  │  (Odoo tools,    │
     │   eval runner)    │  │   webhooks)       │  │   Databricks,    │
     │                   │  │                   │  │   fal endpoints) │
     └───────────────────┘  └───────────────────┘  └──────────────────┘
```

---

## Component Count

| Metric | Value |
|--------|-------|
| Logical components | 4 |
| Actual agents | 3 |
| Actual workflows | 1 |
| Physical Foundry agents | 1 (`ipai-odoo-copilot-azure`) |
| Capability packs | 3 |
| Ingress paths | 5 |

---

## Agent Matrix

| Component | Form | Write | Guardrails | Packs |
|-----------|------|-------|------------|-------|
| `ipai-odoo-copilot-advisory` | Foundry prompt agent | None | No writes, no admin changes, cite sources | Databricks, Marketing, fal (read) |
| `ipai-odoo-copilot-ops` | Agent Framework agent | None | No mutation, no secrets, no role changes | Databricks, Marketing, fal (read) |
| `ipai-odoo-copilot-actions` | Agent Framework agent | Bounded CRUD | Approved writes only, no destructive ops | Databricks, fal Creative, Marketing (light) |
| `ipai-odoo-copilot-router` | Agent Framework workflow | None | No free-form reasoning, no domain mutation | Databricks, fal (routing context) |

---

## Capability Packs

| Pack | Advisory | Ops | Actions | Router |
|------|:--------:|:---:|:-------:|:------:|
| Databricks Intelligence | Yes | Yes | Yes | Yes |
| fal Creative Production | Yes | Yes | Yes | Yes |
| Marketing Strategy & Insight | Yes | Yes | Light | No |

Packs are **not agents**. They are tool sets + prompt segments attached inside existing agents.

---

## Plane Split

```
┌──────────────────────────────┐    ┌──────────────────────────────┐
│       CONTROL PLANE          │    │      EXECUTION PLANE          │
│       (Foundry)              │    │      (Agent Framework)        │
│                              │    │                               │
│  • Advisory prompt agent     │    │  • Ops agent                  │
│  • Datasets                  │    │  • Actions agent              │
│  • Evaluation runs           │    │  • Router workflow            │
│  • Tracing                   │    │  • Checkpointing              │
│  • Project-scoped resources  │    │  • Graph orchestration        │
│  • Model deployments         │    │  • Middleware pipelines        │
│                              │    │  • OTel distributed tracing   │
└──────────────────────────────┘    └──────────────────────────────┘
```

---

## Ingress Matrix

| Path | Purpose | Who | Governance |
|------|---------|-----|-----------|
| Foundry Project Client | config, connections, tracing | internal control plane | Foundry RBAC + project scope |
| OpenAI-compatible client | agents, evals, model calls | agent runtime calls | project scope + deployment policy |
| Direct REST | adapters, n8n, bridges | automation layer | APIM or service auth |
| **APIM AI gateway** | **production front door** | **all production clients** | **auth, quotas, throttling, telemetry** |
| Foundry Playgrounds | prototyping, validation | builders/operators only | **non-production only** |

---

## Evaluation Target

```
┌─────────────────────────────────────────────────────────────┐
│                     EVALUATION LAYERS                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Layer 1: SYSTEM EVALS                                       │
│  ├── Task Completion                                         │
│  ├── Task Adherence                                          │
│  ├── Intent Resolution                                       │
│  ├── Relevance                                               │
│  └── Groundedness (where applicable)                         │
│                                                              │
│  Layer 2: PROCESS EVALS                                      │
│  ├── Tool Selection                                          │
│  ├── Tool Call Success                                       │
│  ├── Tool Output Utilization                                 │
│  ├── Tool Input Accuracy                                     │
│  └── Task Navigation Efficiency (ground truth paths)         │
│                                                              │
│  Layer 3: SAFETY EVALS                                       │
│  ├── Advisory: content risk + jailbreak + human review       │
│  ├── Ops: leakage/refusal + red-team scenarios               │
│  ├── Actions: policy tests + approval-path + human review    │
│  └── Router: approval compliance + routing correctness       │
│                                                              │
│  ⚠ Safety evals are NOT sufficient alone.                    │
│  Must pair with policy tests + human review.                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Observability Target

```
┌─────────────────────────────────────────────────────────┐
│                   OBSERVABILITY STACK                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Foundry Tracing ──► App Insights ──► Correlation IDs    │
│       │                   │                │              │
│       ▼                   ▼                ▼              │
│  Per-agent traces   Aggregated metrics  End-to-end IDs   │
│  (advisory/ops/     (tokens, latency,  across all 4      │
│   actions/router)    tool calls)       components         │
│                                                          │
│  Agent Framework OTel ──► VS Code Foundry Visualizer     │
│  (workflow steps, checkpoints, handoffs)                  │
│                                                          │
└─────────────────────────────────────────────────────────┘

Every invocation logs: user, mode, tools called, tokens consumed,
latency, safety flags, correlation ID.
```

---

## Coordinates

| Setting | Value |
|---------|-------|
| Foundry Resource | `data-intel-ph-resource.services.ai.azure.com` |
| Foundry Project | `data-intel-ph` |
| Physical Agent | `ipai-odoo-copilot-azure` |
| Model | `gpt-4.1` |
| API | Responses API (Agents v2) — `/openai/v1/` |
| SDK | `azure-ai-projects>=2.0.0` |
| APIM | `apim-ipai-dev` (future) |
| Key Vault | `kv-ipai-dev` |
| Search | `srch-ipai-dev` |

---

## What This Is NOT

- **NOT** separate vendor agents (Databricks agent, fal agent, Marketing agent)
- **NOT** an LLM-based router (router is deterministic code)
- **NOT** multiple physical Foundry agents (one agent, instruction-switched)
- **NOT** a replacement for human review (safety evals complement, not replace)
- **NOT** using Playgrounds in production (sandbox only)

---

*SSOT: `ssot/agents/agent_capability_matrix.yaml`, `ssot/platform/agent_ingress_matrix.yaml`*
*Spec: `spec/odoo-copilot-agent-framework/{constitution,prd,plan,tasks}.md`*
*Parent: `ssot/governance/ai-consolidation-foundry.yaml`*
*Last updated: 2026-03-15*
