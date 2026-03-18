# Microsoft Foundry (Azure AI Foundry) — Platform Skill

> Source: https://learn.microsoft.com/en-us/azure/foundry/what-is-foundry
> Domain: `platform` / `agents`
> Last validated: 2026-03-15

---

## What this skill is for

Agents building on or integrating with Microsoft Foundry use this skill to understand
the platform capabilities, map them to IPAI architecture, and choose the right
integration patterns (MCP, A2A, tool catalog, workflows).

---

## Platform Overview

Microsoft Foundry is a unified Azure PaaS for:
- **Application developers** — building AI agents with models + tools
- **ML engineers** — fine-tuning, evaluations, model deployments
- **IT admins** — governance, RBAC, policies

### Evolution from Previous Services

| Previous | Current (Foundry) |
|---|---|
| Azure AI Studio / Azure AI Foundry | Microsoft Foundry |
| Azure AI Services | Foundry Tools |
| Assistants API (Agents v0.5/v1) | Responses API (Agents v2) |
| Monthly `api-version` params | v1 stable routes (`/openai/v1/`) |
| Hub + Azure OpenAI + Azure AI Services | Foundry resource (single, with projects) |
| Multiple SDKs (`azure-ai-inference`, `azure-ai-ml`, etc.) | Unified `azure-ai-projects` 2.x + `OpenAI()` |
| Threads, Messages, Runs, Assistants | Conversations, Items, Responses, Agent Versions |

---

## Key Capabilities

### 1. Build Agents

| Capability | Description | IPAI Mapping |
|---|---|---|
| Multi-agent orchestration | Sequential, group chat, human-in-the-loop workflows | → A2A Coordinator (`agents/mcp/servers/agent-coordination-server/`) |
| Tool catalog | 1,400+ tools via MCP, A2A, OpenAPI | → MCP servers (`agents/mcp/servers/`) |
| Memory | Persist context across interactions | → `ops.platform_events` + Supabase |
| Foundry IQ | Ground responses in enterprise/web content | → Knowledge base (`agents/knowledge-base/`) |
| Publishing | Deploy to M365, Teams, BizChat, containers | → Azure Container Apps (`ca-ipai-dev`) |

### 2. Operate & Govern

| Capability | Description | IPAI Mapping |
|---|---|---|
| Real-time observability | Metrics, tracing, dashboards | → MCP Jobs dashboard + `ops.platform_events` |
| Centralized asset mgmt | Manage agents, models, tools | → `agents/registry/skills-index.json` |
| Enterprise controls | RBAC, AI gateway, Azure Policy | → Entra ID + Azure RBAC |

---

## Workflow Orchestration Patterns

Foundry provides 3 workflow templates:

### Sequential
```
Agent A → Agent B → Agent C → Result
```
**Use**: Step-by-step pipelines, multi-stage processing.
**IPAI equivalent**: Job queue chain (`mcp_jobs.jobs` with dependencies).

### Group Chat
```
Orchestrator ↔ Agent A
             ↔ Agent B
             ↔ Agent C
(dynamic routing based on context)
```
**Use**: Expert handoff, escalation, fallback.
**IPAI equivalent**: A2A Coordinator with `HandoffRequest`.

### Human in the Loop
```
Agent → Ask user question → Wait → Continue
```
**Use**: Approvals, clarifications.
**IPAI equivalent**: Odoo `mail.activity` + stage transitions.

### Workflow Nodes
- **Agent**: Invoke a Foundry agent
- **Logic**: if/else, go to, for each
- **Data transformation**: Set variable, parse value
- **Basic chat**: Send message, ask question

Workflows can be authored visually or as YAML (version-controlled).

---

## Tool Catalog

### Built-in Tools

| Tool | Description | IPAI Equivalent |
|---|---|---|
| Web Search | Real-time web grounding with citations | Firecrawl MCP server |
| Code Interpreter | Sandboxed Python execution | Odoo `ir.cron` + scripts |
| File Search | Vector search over uploaded docs | Supabase pgvector |
| Function Calling | Custom functions, app-executed | MCP tool definitions |
| Image Generation | DALL-E / image gen in conversations | fal.ai inference skill |
| Browser Automation | Playwright-style browser control | `@anthropic/playwright-mcp-server` |
| Computer Use | UI interaction via natural language | Claude computer use |
| Microsoft Fabric | Data agent for analytics | Databricks lakehouse |
| SharePoint | Chat with private docs | Supabase Storage + search |

### Custom Tool Types

| Type | Protocol | IPAI Pattern |
|---|---|---|
| MCP Server (remote) | Model Context Protocol | `agents/mcp/servers/` — our primary pattern |
| MCP Server (local) | MCP (self-hosted) | `.mcp.json` project config |
| OpenAPI Tool | OpenAPI 3.0/3.1 spec | FastAPI endpoints (OCA `rest-framework`) |
| Agent-to-Agent (A2A) | A2A protocol | `agent-coordination-server` (planned) |

### MCP Authentication Methods

| Method | When to Use | IPAI Config |
|---|---|---|
| Key-based (API key/token) | Third-party services | Azure Key Vault → env var |
| Microsoft Entra (managed identity) | Azure-native services | Managed identity on ACA |
| OAuth (user passthrough) | Per-user auth flows | Keycloak / Entra OIDC |

---

## Integration with IPAI Stack

### Foundry as Copilot Runtime

The `ipai-odoo-copilot-azure` foundry spec (`agents/foundry/ipai-odoo-copilot-azure/`) maps to Foundry:

| Foundry Concept | IPAI Implementation |
|---|---|
| Foundry Project | Azure resource group `rg-ipai-dev` |
| Agent Version | Copilot runtime at `mcp.insightpulseai.com` |
| Tool Catalog | MCP servers in `agents/mcp/servers/` |
| Structured Inputs | Context envelope (`context-envelope-contract.md`) |
| Evaluations | `agents/evals/odoo-copilot/` (dataset + rubric + thresholds) |
| Publishing | ACA deployment via `infra/azure/modules/container-apps.bicep` |

### SDK Usage Pattern

```python
# Foundry SDK — creating an agent with tools
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, MCPTool
from azure.identity import DefaultAzureCredential

project = AIProjectClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

# Register MCP server as tool
odoo_tool = MCPTool(
    server_label="odoo-erp",
    server_url="https://mcp.insightpulseai.com/odoo",
    require_approval="always",
    project_connection_id="odoo-mcp-connection",
)

agent = project.agents.create_version(
    agent_name="ipai-odoo-copilot",
    definition=PromptAgentDefinition(
        model="gpt-4o",
        instructions="You are the IPAI Odoo Copilot...",
        tools=[odoo_tool],
    ),
)
```

### A2A Integration (Agent-to-Agent)

Foundry A2A maps directly to our planned `agent-coordination-server`:

```python
from azure.ai.projects.models import AgentToAgentTool

# Connect to a specialist agent
finance_agent = AgentToAgentTool(
    agent_name="finance-specialist",
    description="Handles BIR compliance, month-end close, tax calculations",
)

# Orchestrator can delegate to specialists
orchestrator = project.agents.create_version(
    agent_name="ipai-orchestrator",
    definition=PromptAgentDefinition(
        model="gpt-4o",
        instructions="Route tasks to specialist agents",
        tools=[finance_agent, odoo_tool],
    ),
)
```

---

## SSOT/SOR Mapping

| Foundry Resource | IPAI SSOT | Notes |
|---|---|---|
| Foundry Project | `rg-ipai-dev` (Azure) | One project per environment |
| Agent definitions | `agents/foundry/` (repo) | Version-controlled |
| Tool catalog | `agents/registry/skills-index.json` | Machine-readable index |
| Model deployments | Azure Container Apps | `infra/azure/modules/` |
| Evaluations | `agents/evals/` | Dataset + rubric + results |
| Secrets | Azure Key Vault (`kv-ipai-dev`) | Never in code |

---

## Anti-Patterns

1. **Using Foundry as SSOT for agent definitions** — Repo is SSOT. Foundry is runtime.
2. **Skipping tool catalog for ad-hoc integrations** — All tools must be registered in skills-index.json.
3. **Hub-based projects** — Use new Foundry projects, not classic hubs.
4. **Assistants API (v0.5/v1)** — Deprecated. Use Responses API (Agents v2).
5. **Multiple SDK packages** — Use unified `azure-ai-projects` 2.x only.

---

## When to use this skill

- Deploying IPAI copilot to Azure Foundry
- Registering MCP servers in Foundry tool catalog
- Building multi-agent workflows (sequential, group chat)
- Setting up A2A communication between IPAI agents
- Evaluating agent performance via Foundry observability
- Publishing agents to Teams/M365/BizChat

## When NOT to use this skill

- Databricks-specific work → `databricks-platform` skill
- ETL pipeline design → `databricks-data-engineering` skill
- Odoo module development → `odoo-services-ee-parity` or OCA skills
- CI/CD pipelines → `azure-pipelines` skill
