# Skill: Azure Foundry Agent Service

## Metadata

| Field | Value |
|-------|-------|
| **id** | `azure-foundry-agent-service` |
| **domain** | `azure_foundry` |
| **source** | https://learn.microsoft.com/en-us/azure/foundry/agents/overview |
| **extracted** | 2026-03-15 |
| **applies_to** | agents, infra, foundry |
| **tags** | azure, foundry, agent-service, managed-platform, multi-agent |

---

## What It Is

Fully managed platform for building, deploying, and scaling AI agents. Handles hosting, scaling, identity, observability, and enterprise security. Supports any framework and many models from the Foundry model catalog.

## Core Components

| Component | What It Does |
|-----------|--------------|
| **Agent Runtime** | Hosts and scales prompt + hosted agents. Manages conversations, tool calls, lifecycle. |
| **Tools** | Built-in: web search, file search, code interpreter, MCP, A2A, OpenAPI. Managed auth (service-managed + OBO). |
| **Models** | GPT-4o, Claude (Opus/Sonnet/Haiku 4.5-4.6), Llama, DeepSeek, Phi, Mistral, Cohere. Swap without code changes. |
| **Observability** | End-to-end tracing (OpenTelemetry), metrics, Application Insights integration. |
| **Identity & Security** | Entra identity, RBAC, content filters, VNet isolation. |
| **Publishing** | Version agents, stable endpoints, share via Teams/M365 Copilot/Entra Agent Registry. |

## Agent Types

| Type | Code Required | Hosting | Orchestration | Best For |
|------|--------------|---------|---------------|----------|
| **Prompt agents** | No | Fully managed | Single agent | Rapid prototyping, simple tasks |
| **Workflow agents** (preview) | No (YAML optional) | Fully managed | Multi-agent, branching | Multi-step automation |
| **Hosted agents** (preview) | Yes | Container-based, managed | Custom logic | Full control, custom frameworks |

## Development Lifecycle

1. **Create** — Prompt agent in portal or hosted agent in code
2. **Test** — Agents playground or local run
3. **Trace** — Inspect every model call, tool invocation, decision (OpenTelemetry)
4. **Evaluate** — Run evaluations to measure quality, catch regressions
5. **Publish** — Promote to managed resource with stable endpoint
6. **Monitor** — Track performance with service metrics and dashboards

## IPAI Relevance

| Foundry Concept | IPAI Equivalent | Gap |
|-----------------|-----------------|-----|
| Prompt agents | Claude agents with SKILL.md context | None — same pattern |
| Workflow agents | n8n workflows | Foundry adds visual builder + YAML |
| Hosted agents | ACA-deployed agent containers | Foundry adds managed scaling + identity |
| Agent Runtime | Supabase ops.runs + n8n triggers | Foundry is fully managed |
| Tool catalog | agents/skills/ directory | Foundry adds portal discovery |
| Publishing | ACA revision + AFD endpoint | Foundry adds versioning + Teams/M365 |

### Where Foundry Wins Over Current Stack

- **Managed identity** — Entra agent identity auto-provisioned, no credential management
- **Built-in eval framework** — 9 evaluators with Pass/Fail scoring
- **Visual workflow builder** — No-code multi-agent orchestration
- **One-click Teams/M365 publishing** — Instant distribution channel

### Where Current Stack Wins

- **Supabase SSOT** — Foundry has no equivalent control plane for business state
- **Odoo SOR** — Foundry has no ERP integration
- **Claude-first** — Foundry's Claude support is preview-only via Marketplace
- **n8n webhook routing** — Simpler for pure integration patterns

## SDK Quick Start (Python)

```python
import os
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, WebSearchTool

project = AIProjectClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

agent = project.agents.create_version(
    agent_name="my-agent",
    definition=PromptAgentDefinition(
        model=os.environ["MODEL_NAME"],
        instructions="You are a helpful assistant.",
        tools=[WebSearchTool()],
    ),
)
```

## Region Availability

Hosted agents supported in **Southeast Asia** (confirmed) — compatible with IPAI's `rg-ipai-dev` region.

---

## Related Skills

- [control-plane](../control-plane/SKILL.md) — Fleet management
- [foundry-iq](../foundry-iq/SKILL.md) — Knowledge grounding
- [tool-catalog](../tool-catalog/SKILL.md) — Available tools
- [hosted-agents](../hosted-agents/SKILL.md) — Container deployment
- [workflow-agents](../workflow-agents/SKILL.md) — Multi-agent orchestration
