# agent-framework-core

Design and validate agent/workflow logic using Microsoft Agent Framework patterns — graph orchestration, middleware, telemetry, checkpoint/resume.

## When to use
- New agent design requiring multi-step workflow
- Workflow refactor or restructuring
- Multi-agent orchestration design
- Observability review for agent telemetry
- Human-in-the-loop gate design or audit

## Key rule
Every production workflow must have OpenTelemetry instrumentation and checkpoint/resume for long-running operations. Orchestration is separate from channel delivery — this skill owns workflow logic only.

## Cross-references
- `agents/personas/agent-orchestrator.md`
- `agents/knowledge/benchmarks/microsoft-agent-framework.md`
- `agent-platform/ssot/learning/agent_sdk_stack_map.yaml`
