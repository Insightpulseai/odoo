# Agent Orchestrator

Agent orchestrator: receives requests, resolves routing, dispatches to executor.

## Responsibilities

- Accept inbound agent execution requests
- Resolve agent manifest from registry
- Route to appropriate executor instance
- Manage execution lifecycle (start, checkpoint, complete, fail)
- Emit telemetry events for observability

## Status

Stub implementation. See `index.ts` for interface definitions.
