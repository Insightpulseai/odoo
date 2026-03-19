# Skill: Azure Foundry Agent Observability

## Metadata

| Field | Value |
|-------|-------|
| **id** | `azure-foundry-observability` |
| **domain** | `azure_foundry` |
| **source** | https://learn.microsoft.com/en-us/azure/foundry/observability/concepts/trace-agent-concept |
| **extracted** | 2026-03-15 |
| **applies_to** | agents, infra |
| **tags** | tracing, opentelemetry, application-insights, observability, spans |

---

## How Tracing Works

Captures during agent runs: user inputs, agent outputs, tool usage (calls + results), retries, latencies, costs. Uses OpenTelemetry semantic conventions for consistency.

## Key Concepts

| Concept | Description |
|---------|-------------|
| **Traces** | Capture full journey of a request through the agent |
| **Spans** | Building blocks — each span = one operation (nested for hierarchy) |
| **Attributes** | Key-value metadata on spans (function params, return values) |
| **Semantic Conventions** | Standardized names/formats for trace data (OpenTelemetry + W3C) |
| **Trace Exporters** | Send data to Azure Monitor Application Insights |

## Multi-Agent Semantic Conventions

Microsoft + Cisco Outshift introduced conventions for multi-agent systems:

| Type | Name | Purpose |
|------|------|---------|
| Span | `execute_task` | Task planning and event propagation |
| Child Span | `agent_to_agent_interaction` | Agent-to-agent communication |
| Child Span | `agent.state.management` | Context and memory management |
| Child Span | `agent_planning` | Internal planning steps |
| Child Span | `agent orchestration` | Agent-to-agent orchestration |
| Attribute | `tool_definitions` | Tool purpose/configuration |
| Attribute | `llm_spans` | Model call spans |
| Attribute | `tool.call.arguments` | Arguments passed to tools |
| Attribute | `tool.call.results` | Results returned by tools |
| Event | `Evaluation` | Structured performance evaluation |

## Supported Frameworks

Semantic conventions integrated into:
- Foundry
- Microsoft Agent Framework
- Semantic Kernel
- LangChain / LangGraph
- OpenAI Agents SDK

## IPAI Mapping

| Foundry | IPAI | Gap |
|---------|------|-----|
| Application Insights | Sentry + custom ops.platform_events | Foundry has deeper agent-specific spans |
| OpenTelemetry spans | ops.run_events in Supabase | Need to adopt OTLP conventions |
| Multi-agent tracing | None | **Gap — need agent-to-agent trace correlation** |
| Trace visualization | None | **Gap — Foundry portal visualizer has no equivalent** |

### Adoption Path

1. Add OTLP exporter to agent workflows → send to Azure Monitor
2. Adopt semantic conventions for span naming in ops.run_events
3. Correlate evaluation run IDs with traces
4. Redact sensitive content before telemetry storage

## Best Practices

- Use consistent span attributes across all agents and tools
- Correlate evaluation run IDs with trace data
- Redact PII, secrets, and credentials from prompts and span attributes
- Treat trace data as production telemetry (same access controls as logs)
