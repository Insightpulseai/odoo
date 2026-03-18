# Microsoft Agent Framework

> Source: github.com/microsoft/agent-framework

## What it is

A framework for building, orchestrating, and deploying AI agents and multi-agent workflows in Python and .NET. This is the **core orchestration and workflow layer** — not a channel delivery SDK, not a developer assistant, not an external platform connector.

## Key Capabilities

| Capability | Description |
|-----------|-------------|
| Graph-based workflows | Define agent execution as directed graphs with conditional branching, parallel paths, and convergence points |
| Checkpointing | Persist workflow state at defined points for recovery, resume, and long-running process support |
| Human-in-the-loop | Built-in support for approval gates, escalation triggers, and human intervention points in workflows |
| DevUI | Development-time UI for visualizing and debugging agent workflows |
| OpenTelemetry observability | Native telemetry integration — traces, spans, metrics for all agent operations |
| Multi-provider support | Orchestrate agents across different LLM providers (Azure OpenAI, Anthropic, etc.) |
| Middleware pipeline | Request/response processing hooks for auth, logging, rate limiting, content filtering |

## Role in Our Stack

**Core orchestration/workflow/eval-friendly agent implementation layer.**

Use this when you need to:
- Design a multi-agent workflow with defined execution graph
- Add checkpointing to a long-running agent process
- Instrument agent operations with OpenTelemetry
- Implement human-in-the-loop approval flows
- Build middleware pipelines for agent request processing

## What it is NOT

| Misuse | Correct layer |
|--------|--------------|
| Channel delivery (Teams, M365 Copilot, web) | Microsoft 365 Agents SDK (`microsoft/Agents`) |
| Developer coding assistant | GitHub Copilot SDK (`github/copilot-sdk`) |
| External platform connector (Palantir) | Palantir Foundry SDK (`palantir/foundry-platform-python`) |

## Architecture Position

```
Microsoft Agent Framework  <-- THIS (orchestration)
        |
        v
Microsoft 365 Agents SDK   (channel delivery)
GitHub Copilot SDK          (developer assistance)
Palantir Foundry SDK        (external integration, optional)
```

The Agent Framework sits at the core. Channel delivery, developer tooling, and external integrations are separate concerns with their own SDKs and personas.

## Key Design Patterns

1. **Agent Graph**: Define nodes (agent steps) and edges (transitions) as a directed graph. Conditions on edges enable branching logic.
2. **Middleware Stack**: Chain middleware components for cross-cutting concerns (auth, logging, content safety) without modifying agent logic.
3. **Checkpoint Strategy**: Define checkpoint frequency based on workflow duration and cost of re-execution. Long workflows checkpoint at every major decision point.
4. **Telemetry Contract**: Every production agent emits OpenTelemetry traces. Span names follow `agent.<workflow>.<step>` convention.

## Cross-References

- Persona: `agents/personas/agent-orchestrator.md`
- Skill: `agents/skills/agent-framework-core/`
- Skill map: `agent-platform/ssot/learning/agent_sdk_stack_map.yaml`
