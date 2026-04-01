# agent-platform

Deployable runtime and orchestration plane for agent execution, tool routing, evaluation runtime hooks, and telemetry.

## Purpose

This repository owns the running agent system: runtime services, orchestration logic, gateways, worker management, checkpointing, eval execution hooks, and runtime observability.

## Owns

- Deployable agent runtime services
- Orchestrator and executor components
- Runtime gateways and adapters
- Worker lifecycle management
- Runtime telemetry and tracing bridges
- Execution-time evaluation hooks

## Does Not Own

- Canonical skill definitions
- Personas
- Judges
- Eval suites as source content
- Shared business/control-plane UI
- ERP runtime logic

## Repository Structure

```text
agent-platform/
├── .github/
├── runtimes/
│   ├── orchestrator/
│   ├── executor/
│   ├── checkpointing/
│   └── gateways/
├── services/
│   ├── runtime-api/
│   ├── worker-manager/
│   ├── eval-runner/
│   └── telemetry-bridge/
├── packages/
├── configs/
├── docs/
├── scripts/
├── spec/
├── ssot/
└── tests/
```

## Boundary Rule

If it runs as a deployable service, it belongs here.

## Dependencies

This repo consumes:

- behavioral definitions from `agents`
- shared contracts from `platform`
- infrastructure and runtime policies from `infra`

## Validation

Changes must:

- preserve runtime reliability
- expose observable behavior
- keep orchestration deterministic where required
- pass contract, integration, and smoke validation
