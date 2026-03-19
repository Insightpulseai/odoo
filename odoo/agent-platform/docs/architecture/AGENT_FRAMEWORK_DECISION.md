# Agent Framework Decision

> Version: 1.0.0
> Canonical repo: `agent-platform`

## Context
While the Foundry SDK serves as the primary gateway for intelligent capabilities, complex workflows require multi-agent orchestration and dynamic tool calling within backend logic.

## Decision
- **Use Microsoft Agent Framework** for multi-agent systems built in code.
- **Mirror the DevUI** sample ergonomics for the local developer workflow.
- **Keep Python samples as first-class** initially; however, **add C# (.NET) parity** as a direct mandate to match the official framework's multi-language intent.

## Consequences
- The platform uses a documented framework for agentic coordination.
- `agent-platform/` will structure its agents, workflows, and tools based on the established framework primitives.
- Odoo stays decoupled from multi-agent state machines, instead interacting strictly via API boundaries.
