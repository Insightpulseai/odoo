# AI Consolidation — Microsoft Foundry Gateway

> One Foundry agent. One Odoo bridge module. Five capability modes.
> SSOT: `ssot/governance/ai-consolidation-foundry.yaml`
>
> **Rebrand**: Azure AI Studio → Azure AI Foundry → **Microsoft Foundry** (2025-11)
> **API**: Assistants API → **Responses API (Agents v2)**
> **SDK**: Multiple packages → **`azure-ai-projects` 2.x + `OpenAI()`**

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
                    ┌─────────────────────────────────────┐
                    │     Microsoft Foundry                │
                    │     (data-intel-ph)                  │
                    │                                      │
                    │  ipai-odoo-copilot-azure (v7)        │
                    │  ┌──────────┬───────────────────┐    │
                    │  │ Ask      │ search, read, RAG │    │
                    │  ├──────────┼───────────────────┤    │
                    │  │ Author   │ draft creation    │    │
                    │  ├──────────┼───────────────────┤    │
                    │  │ Livechat │ visitor Q&A       │    │
                    │  ├──────────┼───────────────────┤    │
                    │  │ Transact │ bounded CRUD      │    │
                    │  ├──────────┼───────────────────┤    │
                    │  │ Creative │ image gen, copy   │    │
                    │  └──────────┴───────────────────┘    │
                    │                                      │
                    │  ┌── Platform ────────────────────┐  │
                    │  │ Tool Catalog (1,400+ tools)    │  │
                    │  │ Memory (user_profile + chat)   │  │
                    │  │ Workflows (multi-agent)        │  │
                    │  │ MCP / OpenAPI / A2A connectors │  │
                    │  └───────────────────────────────┘  │
                    │                                      │
                    │  Model: gpt-4.1                      │
                    │  API: Responses API (Agents v2)      │
                    │  SDK: azure-ai-projects 2.x          │
                    │  Search: srch-ipai-dev                │
                    │  Auth: Managed Identity               │
                    └──────────────┬────────────────────────┘
                                  │
                                  │ Responses API (/openai/v1/)
                                  │
                    ┌──────────────┴────────────────────────┐
                    │  Odoo CE 19                            │
                    │                                        │
                    │  ipai_odoo_copilot                     │
                    │  (single bridge module)                │
                    │  ├── FoundryService                    │
                    │  ├── ToolExecutor (MCP-registered)     │
                    │  ├── CopilotBot (mail.bot)             │
                    │  └── App Insights telemetry            │
                    │                                        │
                    │  ipai_enterprise_bridge                │
                    │  (Foundry provider config)             │
                    └────────────────────────────────────────┘
```

## Five Capability Modes

| Mode | Purpose | Write Access | Foundry Built-ins | Replaces |
|------|---------|-------------|-------------------|----------|
| **Ask** | Answer questions, search records, RAG | None (read-only) | Web Search, Memory (user_profile) | `ipai_ai_widget`, `ipai_ask_ai_azure` |
| **Authoring** | Draft documents, reports, emails | Draft only | Code Interpreter, File Search, Memory (chat_summary) | `ipai_ai_copilot`, `ipai_ai_prompts` |
| **Livechat** | Website visitor Q&A via chat | None (read-only) | Web Search, Memory (user_profile) | `ipai_ai_channel_actions`, `ipai_ai_livechat` |
| **Transaction** | Bounded CRUD with approval gates | Whitelisted models | Memory (chat_summary) | `ipai_ai_tools`, `ipai_ai_automations` |
| **Creative** | Image gen, campaign copy, email templates | Draft only | Image Generation, Code Interpreter, File Search | `ipai_marketing_agency_pack` |

## Foundry Platform Capabilities

### Tool Catalog (1,400+ tools)

| Category | Tools | Status |
|----------|-------|--------|
| **Built-in** | Web Search, Code Interpreter, File Search, Function Calling, Azure AI Search | GA |
| **Built-in (Preview)** | Image Generation, Browser Automation, Computer Use, Fabric, SharePoint | Preview |
| **Custom** | MCP servers, OpenAPI specs, Agent-to-Agent (A2A) | GA (MCP/OpenAPI), Preview (A2A) |

### Memory (Long-term, Cross-session)

| Type | Description | Use Case |
|------|-------------|----------|
| **User Profile** | Static preferences (name, language, role) | Personalize Ask/Livechat responses |
| **Chat Summary** | Distilled topic summaries per session | Continue Authoring/Transaction across sessions |

### Workflow Orchestration

| Pattern | Description | ERP Application |
|---------|-------------|-----------------|
| **Sequential** | Agent pipeline (A → B → C) | Multi-step approval workflows |
| **Group Chat** | Dynamic agent handoff by context | Expert escalation (Sales → Finance) |
| **Human-in-the-Loop** | Approval/clarification gates | PO approval, expense review |

## Terminology Migration

| Old (Assistants API) | New (Responses API) |
|---------------------|---------------------|
| Thread | Conversation |
| Message | Item |
| Run | Response |
| Assistant | Agent Version |
| `azure-ai-inference` SDK | `azure-ai-projects` 2.x |
| Monthly `api-version` params | `v1` stable routes (`/openai/v1/`) |
| Hub + Azure OpenAI resource | Single Foundry resource |

## Agent Workflows (Phase 5)

Two authoring paths for multi-agent workflows:

| Path | Tool | Best For |
|------|------|----------|
| **Declarative (low-code)** | YAML in Foundry portal or VS Code for Web | Simple sequential flows, non-developers |
| **Pro-code (hosted)** | Python/C# with Agent Framework SDK | Complex orchestration, custom logic, OTel tracing |

**Low-code → Pro-code bridge**: GitHub Copilot can convert YAML workflows to Agent Framework code (`Generate Code` button in VS Code). This lets you prototype in YAML, then customize in Python.

## Pro-Code Hosted Workflows

Multi-agent ERP workflows built with the Agent Framework SDK, deployed as hosted agents to Foundry.

### Setup

```bash
# Python — hosted agent framework package
pip install azure-ai-agentserver-agentframework

# VS Code extension (required for visualization + deployment)
# Install: TeamsDevApp.vscode-ai-foundry
```

### Project Structure

```
erp-workflow/
├── .env                    # AZURE_AI_PROJECT_ENDPOINT + MODEL_DEPLOYMENT_NAME
├── workflow.py             # Orchestration logic + agent definitions
├── container.py            # Containerized deployment entry point
├── main.py                 # Local dev entry point
└── requirements.txt        # azure-ai-agentserver-agentframework
```

### Observability (OpenTelemetry)

```python
from agent_framework.observability import setup_observability
setup_observability(vs_code_extension_port=4319)  # traces to VS Code visualizer
```

### Deployment Stages

| Stage | Command | Purpose |
|-------|---------|---------|
| Local interactive | F5 in VS Code | Dev + debug with breakpoints |
| Local container | `Microsoft Foundry: Open Container Agent Playground Locally` | Test containerized |
| Cloud deploy | `Microsoft Foundry: Deploy Hosted Agent` | Production in Foundry workspace |

### ERP Workflow Examples

**Expense Approval (Human-in-the-Loop):**
```
[Expense Agent] → classify expense → [Manager Agent] → approve/reject → [Finance Agent] → post to GL
         ↑                                    ↑
    human input                          human approval
```

**Month-End Close (Sequential):**
```
[GL Agent] → reconcile → [AP Agent] → match invoices → [AR Agent] → age receivables → [Tax Agent] → compute
```

**Sales Inquiry (Group Chat):**
```
[CRM Agent] ←→ [Inventory Agent] ←→ [Pricing Agent]
     dynamic handoff based on customer question
```

### Auth Requirements

- `Azure AI User` role on Foundry project
- `AcrPull` role for container deployment
- `DefaultAzureCredential` (az login or managed identity)

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

| Tool | Description | Write | Mode | Connection |
|------|-------------|-------|------|------------|
| `search_records` | Search Odoo records by model + domain | No | All | MCP server |
| `read_record` | Read specific record by ID | No | All | MCP server |
| `search_knowledge` | Search RAG index | No | All | Foundry built-in |
| `web_search` | Real-time web grounding | No | Ask, Livechat, Creative | Foundry built-in |
| `code_interpreter` | Python sandbox (charts, analysis) | No | Authoring, Creative | Foundry built-in |
| `file_search` | Vector search on uploaded docs | No | Authoring, Creative | Foundry built-in |
| `image_generation` | DALL-E 3 image creation | Yes (draft) | Creative | Foundry built-in |
| `create_draft` | Create record in draft state | Yes (draft) | Authoring | MCP server |
| `create_record` | Create record | Yes (bounded) | Transaction | MCP server |
| `update_record` | Update record fields | Yes (bounded) | Transaction | MCP server |
| `execute_action` | Execute server action | Yes (approved) | Transaction | MCP server |

## Safety Controls

- **Read-only by default**: write access requires explicit mode selection
- **Audit all tool calls**: every Foundry tool invocation logged to App Insights
- **Rate limiting**: 60 requests/minute per user
- **PII redaction**: sensitive fields masked before sending to Foundry
- **Model allowlist**: only `gpt-4.1` and `gpt-4.1-mini`
- **No direct LLM calls**: all inference routes through Foundry
- **MCP auth**: Managed Identity preferred (Entra token rotation), key-based and OAuth passthrough supported
- **Content Safety**: Azure AI Content Safety with prompt injection detection

## Migration Phases

| Phase | Scope | Status |
|-------|-------|--------|
| 1 | Foundry ask + authoring modes active | **Active** |
| 2 | Deprecate direct-call AI modules (5 modules) | Planned |
| 3 | Livechat + transaction modes verified | Planned |
| 4 | Set `installable=False` on all deprecated modules | Planned |
| 5 | Microsoft Foundry native (Responses API v2, Memory, MCP catalog, Workflows) | Planned |

## Microsoft Agent Stack (Upstream Repos)

Three complementary layers power the Foundry agent ecosystem. We consume these as SDK dependencies — never fork.

```
┌─────────────────────────────────────────────────────────┐
│                  Microsoft Agent Stack                   │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────────────────────────────────────────────┐    │
│  │ CHANNEL LAYER (microsoft/Agents)                │    │
│  │ M365 Agents SDK — deploy to Teams, BizChat, web │    │
│  │ SDKs: C#, JavaScript, Python                    │    │
│  └──────────────────────┬──────────────────────────┘    │
│                         │                                │
│  ┌──────────────────────┴──────────────────────────┐    │
│  │ ORCHESTRATION LAYER (microsoft/agent-framework) │    │
│  │ Multi-agent workflows, graph-based, OTel        │    │
│  │ SDKs: Python, .NET                              │    │
│  └──────────────────────┬──────────────────────────┘    │
│                         │                                │
│  ┌──────────────────────┴──────────────────────────┐    │
│  │ FOUNDRY PLATFORM (Microsoft Foundry)            │    │
│  │ Agent runtime, tools, memory, publishing        │    │
│  │ SDK: azure-ai-projects 2.x + OpenAI()          │    │
│  └─────────────────────────────────────────────────┘    │
│                                                          │
│  ┌─────────────────────────────────────────────────┐    │
│  │ DEV TOOLING (github/copilot-sdk)                │    │
│  │ Copilot CLI engine, JSON-RPC, auto-planning     │    │
│  │ SDKs: Node, Python, Go, .NET (Preview)          │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

### How Each Layer Maps to Our Platform

| Layer | Repo | Our Usage | Status |
|-------|------|-----------|--------|
| **Orchestration** | `microsoft/agent-framework` | Foundry workflow orchestration for multi-step ERP tasks (expense approval, month-end close, sequential GL/AP/AR) | Planned |
| **Channel** | `microsoft/Agents` | Publish `ipai-odoo-copilot-azure` to Teams, surface ERP in BizChat, web channel for livechat | Planned |
| **Dev Tooling** | `github/copilot-sdk` | Internal: module scaffolding, CI auto-fix, code review gates | Evaluate (Preview) |

### Agent Framework Workflow Patterns for ERP

| Pattern | Agent Framework Feature | ERP Application |
|---------|------------------------|-----------------|
| Sequential | Graph-based pipeline | Month-end close: GL → AP → AR → Tax → Consolidation |
| Human-in-the-Loop | Checkpoint + approval | Expense: Agent draft → Manager approve → Finance review |
| Group Chat | Dynamic handoff | Sales inquiry: CRM agent → Inventory agent → Pricing agent |
| Streaming | Real-time progress | Live dashboard of close progress across all entities |
| Time-travel Debug | Checkpoint replay | Audit trail: replay agent decisions for compliance |

## Foundry Coordinates

| Setting | Value |
|---------|-------|
| Brand | **Microsoft Foundry** (formerly Azure AI Foundry) |
| Portal | `https://ai.azure.com` |
| Resource | `data-intel-ph-resource.services.ai.azure.com` |
| Project | `data-intel-ph` |
| Agent | `ipai-odoo-copilot-azure` |
| Model | `gpt-4.1` |
| API | Responses API (Agents v2) — `/openai/v1/` |
| SDK | `azure-ai-projects` 2.x |
| Search | `srch-ipai-dev` |
| Auth | Managed Identity (primary), API Key (fallback) |
| Secrets | Azure Key Vault (`kv-ipai-dev`) |

## Upstream Repos

| Repo | Install | Purpose |
|------|---------|---------|
| [`microsoft/agent-framework`](https://github.com/microsoft/agent-framework) | `pip install agent-framework --pre` | Multi-agent orchestration |
| [`microsoft/Agents`](https://github.com/microsoft/Agents) | Language-specific (C#/JS/Python) | M365 channel deployment |
| [`github/copilot-sdk`](https://github.com/github/copilot-sdk) | `pip install github-copilot-sdk` | Dev tooling (Preview) |

---

*SSOT: `ssot/governance/ai-consolidation-foundry.yaml`*
*Agent policy: `infra/ssot/agents/prod_policy.yaml`*
*Last updated: 2026-03-15*
