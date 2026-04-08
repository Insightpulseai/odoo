# AI Consolidation — Microsoft Foundry Gateway

> One Foundry agent. One Odoo bridge module. Three agents + one router workflow.
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

## Three Agents + One Router (Target State)

> Full diagram: [`COPILOT_TARGET_STATE.md`](COPILOT_TARGET_STATE.md)

| Component | Form | Plane | Write | Packs |
|-----------|------|-------|-------|-------|
| `ipai-odoo-copilot-advisory` | Foundry prompt agent | Control | None | Databricks, Marketing, fal (read) |
| `ipai-odoo-copilot-ops` | Agent Framework agent | Execution | None | Databricks, Marketing, fal (read) |
| `ipai-odoo-copilot-actions` | Agent Framework agent | Execution | Bounded CRUD | Databricks, fal Creative, Marketing (light) |
| `ipai-odoo-copilot-router` | Agent Framework workflow | Execution | None | Databricks, fal (routing context) |

### Legacy Mode Migration Map

| Legacy Mode | Target Agent | Notes |
|-------------|-------------|-------|
| Ask | Advisory | Read-only, user-facing |
| Livechat | Advisory | Read-only, user-facing |
| Authoring (read) | Ops | Internal analysis |
| Authoring (write) | Actions | Draft creation |
| Transaction | Actions | Bounded CRUD |
| Creative | Actions | fal pack + Foundry image_generation |

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

## Target State: 3 Agents + 1 Router

> Full diagram: [`docs/architecture/COPILOT_TARGET_STATE.md`](COPILOT_TARGET_STATE.md)

The five capability modes consolidate into three logical agents + one deterministic router:

| Component | Form | Plane | Write | Replaces |
|-----------|------|-------|-------|----------|
| `ipai-odoo-copilot-advisory` | Foundry prompt agent | Control | None | Ask + Livechat modes |
| `ipai-odoo-copilot-ops` | Agent Framework agent | Execution | None | Authoring (read/analysis) |
| `ipai-odoo-copilot-actions` | Agent Framework agent | Execution | Bounded CRUD | Authoring (drafts) + Transaction + Creative |
| `ipai-odoo-copilot-router` | Agent Framework workflow | Execution | None | Mode selection logic |

**Key constraints:**
- All four are logical modes of the single physical agent `ipai-odoo-copilot-azure`
- Capability packs (Databricks, fal, Marketing) attach inside agents — never as standalone agents
- APIM AI gateway is the required production front door
- Safety evals must pair with policy tests + human review
- Router is deterministic code, not LLM inference

**SSOT matrices:**
- Agent capabilities: `infra/ssot/agents/agent_capability_matrix.yaml`
- Ingress paths: `infra/ssot/platform/agent_ingress_matrix.yaml`
- Spec kit: `spec/odoo-copilot-agent-framework/`

---

## Observed Current Foundry Topology

Current platform evidence shows a mixed estate:

- `data-intel-ph-resource` — Foundry resource (canonical candidate)
- `data-intel-ph` — Foundry project under `data-intel-ph-resource`
- `oai-ipai-dev` — standalone Azure OpenAI resource
- `aifoundry-ipai-dev` — legacy hub
- `proj-ipai-claude` — legacy hub-backed project

### Interpretation

The platform currently spans three control-plane lanes:

1. **Resource + project lane** — Forward path and canonical default.
2. **Standalone Azure OpenAI lane** — Conditional lane for direct OpenAI-resource separation.
3. **Legacy hub/project lane** — Transitional lane that must be explicitly tracked until retired or migrated.

## Portal UX vs Runtime Authority

The Microsoft Foundry landing page is not a runtime authority surface.

### Evidence classes

- **UI evidence** — Confirms portal experience and visible features.
- **Control-plane evidence** — Confirms resources, projects, hubs, endpoints, and SDK bindings.
- **Runtime evidence** — Confirms real calls, agent execution, health checks, traces, and active bindings.

### Rule

Do not infer canonical runtime binding from the portal home screen alone.

## Canonical Target State

### Canonical defaults

- **Foundry resource:** `data-intel-ph-resource`
- **Foundry project:** `data-intel-ph`
- **Project endpoint:** `https://data-intel-ph-resource.services.ai.azure.com/api/projects/data-intel-ph`
- **OpenAI compatibility base:** `https://data-intel-ph-resource.openai.azure.com/openai/v1/`

### Rules

- New work targets the resource + project lane by default.
- Hub-backed assets are legacy until explicitly normalized.
- `oai-ipai-dev` remains conditional, not default.
- Model-provider policy must not assume OpenAI-only.

## Python Package Governance

Use three distinct Python lanes:

1. **Foundry project SDK lane** — `azure-ai-projects` + `azure-identity`, optional `openai` companion
2. **OpenAI compatibility lane** — `openai`
3. **Service-specific tools lane** — Speech, Content Safety, Vision, Language, Translator, Document Intelligence, Azure AI Search

### Rules

- Do not label all Python AI dependencies as a single "Foundry SDK".
- Do not use `openai` as the default surface for project-native Foundry operations.
- Do not mix classic and new-portal SDK guidance without an explicit version decision.
- Keep preview/new-portal SDK usage (`azure-ai-projects` 2.x) behind an exception record.
- SSOT: `ssot/foundry/python_sdk_surfaces.yaml`

## Odoo Federation Boundary

Odoo is a federated application workload, not the Foundry control plane.

### Odoo/Entra contract

- Single-tenant web app registration preferred for workforce login
- Redirect URI path: `/auth_oauth/signin`
- Odoo system parameter: `auth_oauth.authorization_header=1`
- Microsoft Graph delegated permission: `User.Read`

### Rule

Keep Odoo login/auth concerns in the Odoo/Entra lane. Do not move them into Foundry runtime governance.

## Azure CLI Surface Boundaries

### In scope

The canonical CLI surfaces for the Foundry-enabled Odoo platform are:

- `az cognitiveservices ...` for Foundry model deployment and model endpoint management
- `az ml ...` where Microsoft Foundry project connection flows explicitly require the `ml` extension
- SDK / REST / project-endpoint based agent operations for Azure AI Agent Service

### Out of scope

`az workloads` is not part of the canonical Odoo + Foundry implementation surface.

It is a SAP-specific Azure CLI extension for managing Virtual Instance for SAP solutions and related SAP workload resources. It may be referenced only as an architectural benchmark for Azure-managed workload lifecycle patterns, not as an implementation dependency for Odoo, Foundry, or the multi-agent runtime.

### Design rule

Do not add `az workloads` to platform runbooks, bootstrap scripts, CI pipelines, or deployment contracts for the Odoo + Foundry stack unless a separate SAP workload lane is intentionally introduced.

## Control Surface Mapping

| Concern | Canonical surface | Notes |
|---|---|---|
| Odoo application lifecycle | repo IaC / app runtime automation | Not handled by `az workloads` |
| Foundry model deployment | `az cognitiveservices` | Model deployment and endpoint management |
| Foundry project connection setup | `az ml` where required by Microsoft docs | Project-scoped connection workflows |
| Agent runtime operations | SDK / REST against Foundry project endpoint | Agent Service uses project endpoint model |
| SAP managed workload operations | `az workloads` | Benchmark/reference only, out of current scope |

---

*SSOT: `ssot/governance/ai-consolidation-foundry.yaml`*
*Agent policy: `infra/ssot/agents/prod_policy.yaml`*
*Target state: `docs/architecture/COPILOT_TARGET_STATE.md`*
*Last updated: 2026-03-25*
