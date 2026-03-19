# Agents Repo Exploration Report

> Generated: 2026-03-18
> Scope: `/agents` directory only
> Purpose: Inventory of precursor, TaxPulse, Foundry, benchmark, tool registry, and memory assets

---

## Executive Summary

The `agents/` directory (1,650 files) contains a mature agent orchestration system with:

- **Odoo Copilot** — Advisory-mode precursor with full system prompt, context envelope, RBAC, tool definitions, and 150-case eval suite (ADVISORY_RELEASE_READY)
- **TaxPulse/BIR** — Finance close specialist prompt + 4 BIR compliance knowledge base docs + PH tax taxonomy + finance tool allowlist — but no standalone Foundry agent yet
- **Foundry integration** — 24 governance policies, 4 agent manifests, tool definitions, runtime contract, publish lifecycle — blocked on Azure AI Foundry project provisioning
- **Benchmark/eval** — 9 judge personas, eval rubric with zero-tolerance safety gates, 150-case dataset, release ladder
- **Tool registry** — Document Intelligence + Odoo RPC actions defined; MCP coordinator with routing logic; 9 MCP servers (8 scaffolded, 1 live)
- **Memory/personalization** — Context envelope contract (server-side RBAC injection), retrieval scope mapping, audit trail model — memory MCP server scaffolded but not implemented

**Code breakdown:** 31 Python, 40 TypeScript, 1,181 Markdown, 249 YAML

---

## Top-Level Structure

```
agents/
├── ORCHESTRATOR.md                     # Agent execution guide
├── AGENT_CAPABILITY_INVENTORY.yaml     # 142 capabilities (14 prod, 23 staging, 71 dev)
├── coordinator/policies/               # Subagent routing rules
├── evals/                              # Eval harness (odoo-copilot: 150 cases)
├── foundry/                            # Azure AI Foundry SDK integration
│   ├── ipai-odoo-copilot-azure/        # Copilot runtime contracts
│   ├── agents/                         # 4 Foundry agent manifests
│   ├── tools/                          # Tool definitions
│   ├── policies/                       # 24 governance policies
│   └── specs/                          # 3 spec bundles
├── knowledge-base/                     # 8 KB domains (bir-compliance, finance-close, etc.)
├── library-pack/                       # Router, taxonomy, prompts
├── mcp/                                # MCP coordinator + 9 servers
├── personas/                           # 9 judge personas
├── registry/                           # Agent registry (SSOT)
├── skills/                             # Skill definitions
├── studio/                             # 36 pre-built agent personalities
└── subagents/                          # git-expert, devops-expert, repo-expert
```

---

## Findings by Category

### 1. Precursor / Core Copilot Shell

| Asset | Path | Status | Reusable |
|-------|------|--------|----------|
| Agent metadata (model, channels, write policy) | `foundry/ipai-odoo-copilot-azure/metadata.yaml` | Production | Full |
| System prompt v2.0.0 | `foundry/ipai-odoo-copilot-azure/system-prompt.md` | Production | Full |
| Runtime contract C-30 | `foundry/ipai-odoo-copilot-azure/runtime-contract.md` | Production | Full |
| Context envelope contract | `foundry/ipai-odoo-copilot-azure/context-envelope-contract.md` | Production | Full |
| Retrieval grounding contract | `foundry/ipai-odoo-copilot-azure/retrieval-grounding-contract.md` | Phase 2B | Partial |
| Tool definitions (8 read-only) | `foundry/ipai-odoo-copilot-azure/tool-definitions.json` | Staging | Full |
| Copilot agent manifest | `foundry/agents/agents__runtime__odoo_copilot__v1.manifest.yaml` | Staging | Full |
| Guardrails | `foundry/ipai-odoo-copilot-azure/guardrails.md` | Staging | Full |
| Publish policy | `foundry/ipai-odoo-copilot-azure/publish-policy.md` | Staging | Partial |

**Verdict:** Core copilot shell is well-defined at contract/policy level. Runtime execution blocked on Foundry project provisioning.

### 2. TaxPulse / BIR / Finance Specialist

| Asset | Path | Status | Reusable |
|-------|------|--------|----------|
| Finance assistant manifest | `foundry/agents/agents__runtime__odoo_finance_assistant__v1.manifest.yaml` | Draft | Full |
| Finance close assistant manifest | `foundry/agents/agents__runtime__odoo_close_assistant__v1.manifest.yaml` | Draft | Full |
| BIR filing calendar | `knowledge-base/bir-compliance/bir-filing-calendar.md` | Production | Full |
| BIR forms reference | `knowledge-base/bir-compliance/bir-forms-reference.md` | Production | Full |
| VAT compliance guide | `knowledge-base/bir-compliance/vat-compliance-guide.md` | Production | Full |
| Withholding tax guide | `knowledge-base/bir-compliance/withholding-tax-guide.md` | Production | Full |
| PH tax taxonomy | `library-pack/schemas/taxonomy/philippines_tax.yaml` | Production | Full |
| Finance close specialist prompt | `library-pack/prompts/agents/finance_close_specialist.md` | Staging | Full |
| PH close tax pack prompt | `library/prompts/finance/ph-close-tax-pack.md` | Staging | Full |
| Finance tool allowlist | `foundry/policies/agents__policy__finance_tool_allowlist__v1.policy.yaml` | Active | Full |

**Verdict:** Strong knowledge base and policy layer. No standalone TaxPulse Foundry agent exists — finance_close_specialist is prompt-only, not packaged.

### 3. Tool Registry / Routing

| Asset | Path | Status | Reusable |
|-------|------|--------|----------|
| Agent registry (SSOT) | `registry/agents.yaml` | Production | Full |
| Agent router (keyword→agent) | `library-pack/router/agent_router.yaml` | Staging | Full |
| Routing policy (subagents) | `coordinator/policies/routing_policy.md` | Active | Full |
| MCP coordinator routing | `mcp/coordinator/app/routing.py` | Staging | Partial |
| MCP coordinator config | `mcp/coordinator/app/config.py` | Staging | Partial |
| Odoo MCP config | `mcp/odoo-mcp/config.yaml` | Staging | Full |
| Document Intelligence tool | `foundry/tools/agents__tools__document_intelligence__v1.manifest.yaml` | Staging | Full |
| Odoo actions tool | `foundry/tools/agents__tools__odoo_actions__v1.manifest.yaml` | Staging | Full |
| Tool allowlist policy | `foundry/policies/agents__policy__tool_allowlist__v1.policy.yaml` | Active | Full |
| 9 MCP servers (8 scaffold, 1 live) | `mcp/servers/` | Mixed | Partial |

**Verdict:** Strong policy/contract layer. MCP coordinator has routing logic but most servers are scaffolded.

### 4. Foundry Integration

| Asset | Path | Status | Reusable |
|-------|------|--------|----------|
| 24 governance policies | `foundry/policies/` | Active | Full |
| 4 agent manifests | `foundry/agents/` | Mixed | Full |
| Runtime strategy policy | `foundry/policies/org__foundry__runtime_strategy__v1.policy.yaml` | Active | Full |
| Model selection policy | `foundry/policies/org__foundry__model_selection_policy__v1.policy.yaml` | Active | Full |
| Artifact naming convention | `foundry/policies/org__foundry__artifact_naming_convention__v1.policy.yaml` | Active | Full |
| Factory schemas | `foundry/factory/` | Active | Full |
| Remote state snapshots | `foundry/ipai-odoo-copilot-azure/remote-*.json` | Archive | Reference |
| Agentic SDLC constitution | `foundry/agentic-sdlc-constitution.md` | Active | Full |

**Verdict:** Governance layer is production-ready. Blocked on Azure AI Foundry project provisioning in `rg-ipai-ai-dev`.

### 5. Benchmark / Eval

| Asset | Path | Status | Reusable |
|-------|------|--------|----------|
| Eval rubric | `evals/odoo-copilot/rubric.md` | Production | Full |
| Release thresholds | `evals/odoo-copilot/thresholds.yaml` | Production | Full |
| 150-case dataset | `evals/odoo-copilot/datasets/eval-dataset-v2.json` | Production | Full |
| Eval results (100% pass) | `evals/odoo-copilot/results/eval-20260315-full-final.json` | Archive | Reference |
| LATEST status | `evals/odoo-copilot/LATEST.md` | Production | Full |
| 9 judge personas | `personas/` | Active | Full |
| Builder-factory eval blueprint | `evals/builder-factory/` | Staging | Partial |
| Benchmark references (3 docs) | `knowledge/benchmarks/` | Reference | Full |

**Verdict:** Eval infrastructure is the most mature subsystem. 150-case rubric with zero-tolerance safety gates.

### 6. Memory / Personalization

| Asset | Path | Status | Reusable |
|-------|------|--------|----------|
| Context envelope contract | `foundry/ipai-odoo-copilot-azure/context-envelope-contract.md` | Production | Full |
| Retrieval scope mapping | `foundry/ipai-odoo-copilot-azure/retrieval-grounding-contract.md` | Phase 2B | Partial |
| Audit trail model spec | Referenced in runtime-contract.md | Spec only | Partial |
| Memory MCP server | `mcp/servers/memory-mcp-server/` | Scaffolded | Partial |

**Verdict:** Context envelope is well-designed. Memory persistence and user-level personalization are not implemented.

---

## Reusable vs Partial vs Stale vs Missing

### Fully Reusable (build on these)
1. Copilot system prompt + metadata + guardrails
2. Context envelope contract + RBAC model
3. Eval rubric + thresholds + 150-case dataset
4. BIR compliance knowledge base (4 docs)
5. PH tax taxonomy
6. Agent registry + router
7. All 24 Foundry governance policies
8. Tool definitions (Document Intelligence + Odoo actions)
9. Judge personas (9)
10. Finance tool allowlist

### Partially Reusable (extend)
1. MCP coordinator routing logic (needs wiring to live endpoints)
2. Memory MCP server (scaffolded, needs implementation)
3. Retrieval grounding contract (needs AI Search index populated)
4. Finance/close assistant manifests (Draft, need eval + promotion)
5. Builder-factory eval blueprint (needs dataset)

### Stale / Deprecated
1. `mcp/servers/digitalocean-mcp-server/` — DigitalOcean deprecated
2. `mcp/servers/vercel-mcp-server/` — Vercel deprecated
3. Remote state snapshots — point-in-time archives

### Missing (must build)
1. Azure AI Foundry project provisioning
2. AI Search index seeding with KB docs
3. ipai_odoo_copilot Discuss bot module
4. App Insights / OTLP telemetry wiring
5. TaxPulse as standalone Foundry agent
6. Memory persistence implementation
7. Red team / adversarial eval suite
8. Evidence pack bundling utility
9. Multi-tenant personalization storage

---

## Recommended Next Steps

| Priority | Action | Rationale |
|----------|--------|-----------|
| P0 | Provision Azure AI Foundry project | Unblocks Stage 2 (grounding, tools, telemetry) |
| P0 | Seed AI Search index with bir-compliance + finance-close KBs | Enables RAG for copilot |
| P0 | Deploy ipai_odoo_copilot Discuss bot module | Primary consumption channel |
| P1 | Wire App Insights telemetry | Stage 2 observability |
| P1 | Promote finance_close_specialist → TaxPulse Foundry agent | Domain specialist packaging |
| P1 | Implement memory MCP server | Conversation persistence |
| P2 | Expand eval corpus 150→500 | Full safety gate validation |
| P2 | Red team / adversarial eval | Prompt injection resistance |
| P2 | Evidence pack utility | Audit compliance bundling |
