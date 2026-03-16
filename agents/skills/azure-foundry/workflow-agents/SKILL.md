# Skill: Azure Foundry Workflow Agents

## Metadata

| Field | Value |
|-------|-------|
| **id** | `azure-foundry-workflow-agents` |
| **domain** | `azure_foundry` |
| **source** | https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/workflow |
| **extracted** | 2026-03-15 |
| **applies_to** | agents, automations |
| **tags** | workflows, orchestration, multi-agent, visual-builder, power-fx |

---

## What It Is

Declarative, visual multi-agent orchestration in Foundry. Build without code using a visual builder, or define in YAML via VS Code.

## Orchestration Patterns

| Pattern | Description | Use Case |
|---------|-------------|----------|
| **Sequential** | Result from one agent passes to next in order | Pipelines, multi-stage processing |
| **Group Chat** | Dynamic control passing between agents by context/rules | Escalation, expert handoff |
| **Human in the Loop** | Pauses for user approval/input | Approvals, clarification |

## Node Types

| Node | Purpose |
|------|---------|
| **Agent** | Invoke an agent |
| **Logic** | If/else, go to, for each |
| **Data Transformation** | Set variable, parse value |
| **Basic Chat** | Send message, ask question |

## Features

- **YAML Visualizer View** — Edit as YAML or visual, changes sync
- **Versioning** — Each save = immutable version with full history
- **Power Fx** — Excel-like formulas for data manipulation (variables, conditions, parsing)
- **Structured JSON output** — Configure agents to return typed JSON schemas

## Power Fx System Variables

| Variable | Description |
|----------|-------------|
| `System.Conversation.Id` | Unique conversation ID |
| `System.LastMessage.Text` | Previous user message |
| `System.User.Language` | User language locale |
| `System.Conversation.InTestMode` | Whether running in test canvas |

## IPAI Comparison

| Foundry Workflows | n8n | Winner |
|-------------------|-----|--------|
| Visual multi-agent orchestration | Visual workflow builder | Tie |
| Power Fx expressions | JavaScript code nodes | n8n (more flexible) |
| Agent-native nodes | HTTP/webhook nodes | Foundry (agent-aware) |
| YAML definition | JSON workflow export | Both exportable |
| Human-in-the-loop | Webhook wait nodes | Foundry (native) |
| Version history | Manual version control | Foundry (built-in) |

### Decision: When to Use Foundry Workflows vs n8n

| Use Case | Choose |
|----------|--------|
| Multi-agent reasoning chains | Foundry Workflows |
| Pure integration/webhook routing | n8n |
| Human approval flows | Foundry Workflows |
| Connecting to 400+ services | n8n |
| Agent-to-agent coordination | Foundry Workflows |
| Cron-based automation | n8n |
