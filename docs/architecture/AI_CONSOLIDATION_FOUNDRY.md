# AI Consolidation — Microsoft Foundry Gateway

> One Foundry agent. One Odoo bridge module. Four capability modes.
> SSOT: `ssot/governance/ai-consolidation-foundry.yaml`

## Problem

16 AI-related Odoo modules with overlapping capabilities, multiple inference backends (OpenAI direct, Azure OpenAI, Gemini, Supabase Edge Functions), and no unified gateway. This creates:

- Inconsistent AI behavior across surfaces (Ask AI vs Copilot vs Channel Actions)
- Multiple API key management paths
- No centralized rate limiting, guardrails, or telemetry
- Difficult to audit AI usage across the platform

## Solution

Consolidate all AI capabilities through **Microsoft Foundry** (`data-intel-ph` project) using the existing `ipai-odoo-copilot-azure` agent as the single entry point.

## Architecture

```
                    ┌─────────────────────────────────┐
                    │     Microsoft Foundry            │
                    │     (data-intel-ph)              │
                    │                                  │
                    │  ipai-odoo-copilot-azure (v7)    │
                    │  ┌─────────┬──────────────────┐  │
                    │  │ Ask     │ search, read,    │  │
                    │  │         │ knowledge        │  │
                    │  ├─────────┼──────────────────┤  │
                    │  │Author   │ draft creation   │  │
                    │  ├─────────┼──────────────────┤  │
                    │  │Livechat │ visitor Q&A      │  │
                    │  ├─────────┼──────────────────┤  │
                    │  │Transact │ bounded CRUD     │  │
                    │  └─────────┴──────────────────┘  │
                    │                                  │
                    │  Model: gpt-4.1                  │
                    │  Search: srch-ipai-dev            │
                    │  Auth: Managed Identity           │
                    └──────────────┬────────────────────┘
                                  │
                                  │ Azure AI Agent API
                                  │
                    ┌──────────────┴────────────────────┐
                    │  Odoo CE 19                        │
                    │                                    │
                    │  ipai_odoo_copilot                 │
                    │  (single bridge module)            │
                    │  ├── FoundryService                │
                    │  ├── ToolExecutor                  │
                    │  ├── CopilotBot (mail.bot)         │
                    │  └── App Insights telemetry        │
                    │                                    │
                    │  ipai_enterprise_bridge            │
                    │  (Foundry provider config)         │
                    └────────────────────────────────────┘
```

## Four Capability Modes

| Mode | Purpose | Write Access | Replaces |
|------|---------|-------------|----------|
| **Ask** | Answer questions, search records, RAG retrieval | None (read-only) | `ipai_ai_widget`, `ipai_ask_ai_azure` |
| **Authoring** | Draft documents, reports, emails | Draft only | `ipai_ai_copilot` (deprecated), `ipai_ai_prompts` |
| **Livechat** | Website visitor Q&A via chat | None (read-only) | `ipai_ai_channel_actions`, `ipai_ai_livechat` |
| **Transaction** | Bounded CRUD with approval gates | Whitelisted models | `ipai_ai_tools`, `ipai_ai_automations` |

## Module Consolidation

### Canonical (keep)

| Module | Role |
|--------|------|
| `ipai_odoo_copilot` | Odoo-side bridge to Foundry (single entry point) |
| `ipai_enterprise_bridge` | Foundry provider config + EE stubs |

### Retained Infrastructure (keep, internal use)

| Module | Role | Why Retained |
|--------|------|-------------|
| `ipai_ai_core` | Provider registry models | Internal model layer for bridge |
| `ipai_ai_agent_builder` | Agent/topic/tool builder | Agent definitions sync to Foundry |
| `ipai_ai_rag` | RAG pipeline | Feeds Foundry search index |
| `ipai_agent_skills` | Skill registry | Skills consumed by Foundry instructions |

### Deprecated by Foundry

| Module | Replacement | Phase |
|--------|-------------|-------|
| `ipai_ai_widget` | Foundry ask mode | 2 |
| `ipai_ask_ai_azure` | Foundry ask mode | 2 |
| `ipai_ai_platform` | Foundry API | 2 |
| `ipai_llm_supabase_bridge` | Foundry gateway | 2 |
| `ipai_ai_oca_bridge` | Foundry gateway | 2 |
| `ipai_ai_channel_actions` | Foundry livechat mode | 3 |
| `ipai_ai_tools` | Foundry transaction mode | 3 |

### Already Deprecated

| Module | Status |
|--------|--------|
| `ipai_ai_copilot` | Superseded by `ipai_odoo_copilot` |
| `ipai_copilot_ui` | Superseded by design system SDK |
| `ipai_ai_livechat` | Migrated to enterprise bridge |
| `ipai_ai_automations` | Migrated to enterprise bridge |
| `ipai_ai_fields` | Retired |

## Foundry Tools (Odoo-side)

| Tool | Description | Write | Mode |
|------|-------------|-------|------|
| `search_records` | Search Odoo records by model + domain | No | All |
| `read_record` | Read specific record by ID | No | All |
| `search_knowledge` | Search RAG index | No | All |
| `create_draft` | Create record in draft state | Yes (draft) | Authoring |
| `create_record` | Create record | Yes (bounded) | Transaction |
| `update_record` | Update record fields | Yes (bounded) | Transaction |
| `execute_action` | Execute server action | Yes (approved) | Transaction |

## Safety Controls

- **Read-only by default**: write access requires explicit mode selection
- **Audit all tool calls**: every Foundry tool invocation logged to App Insights
- **Rate limiting**: 60 requests/minute per user
- **PII redaction**: sensitive fields masked before sending to Foundry
- **Model allowlist**: only `gpt-4.1` and `gpt-4.1-mini`
- **No direct LLM calls**: all inference routes through Foundry — no OpenAI/Gemini/Supabase bypass

## Migration Phases

| Phase | Scope | Status |
|-------|-------|--------|
| 1 | Foundry ask + authoring modes active | **Active** |
| 2 | Deprecate direct-call AI modules (5 modules) | Planned |
| 3 | Livechat + transaction modes verified | Planned |
| 4 | Set `installable=False` on all deprecated modules | Planned |

## Foundry Coordinates

| Setting | Value |
|---------|-------|
| Resource | `data-intel-ph-resource.services.ai.azure.com` |
| Project | `data-intel-ph` |
| Agent | `ipai-odoo-copilot-azure` |
| Model | `gpt-4.1` |
| API Version | `2024-12-01-preview` |
| Search | `srch-ipai-dev` |
| Auth | Managed Identity (primary), API Key (fallback) |
| Secrets | Azure Key Vault (`kv-ipai-dev`) |

---

*SSOT: `ssot/governance/ai-consolidation-foundry.yaml`*
*Agent policy: `infra/ssot/agents/prod_policy.yaml`*
*Last updated: 2026-03-15*
