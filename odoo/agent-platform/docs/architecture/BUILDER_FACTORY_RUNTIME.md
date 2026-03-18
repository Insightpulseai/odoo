# Builder Factory Runtime

## Decision

The builder factory is implemented as a workspace inside `agent-platform`, not as a separate top-level repository.

## Rationale

Microsoft Foundry is the runtime plane for agents, models, tools, evaluations, and operations. The Foundry SDK is the default SDK for applications using agents, evaluations, and Foundry-specific capabilities. Agent Framework is the default code-level orchestration layer for multi-agent systems.

Because the builder factory is still tightly coupled to:

- Foundry runtime and project endpoint usage
- Agent publishing and evaluation workflows
- Shared agent contracts
- Orchestration logic
- Runtime-facing tool bindings

it belongs in `agent-platform`.

## Boundary

- `agent-platform` owns runtime, orchestration, publishing, contracts, and execution
- `agents` owns personas, skills, judges, templates, knowledge, and eval assets
- `templates` owns generic cross-repo starter files if needed

## Promotion rule

Promote builder-factory to a standalone repo only when it has:

- An independent deployment lifecycle
- Separate secrets/infra
- Stable external API/SDK contracts
- Multi-repo platform ownership
- At least 3 months of stable operation as a workspace
