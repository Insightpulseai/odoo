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

## Runtime positioning

`agent-platform` uses `microsoft/agent-framework` as the default orchestration substrate for the Agent plane.

### Role in the architecture
- **Agent plane runtime**: workflow orchestration, multi-agent coordination, checkpoints, middleware, observability, and human-in-the-loop control
- **Not the transaction plane**: Odoo remains the transactional system of record
- **Not the delivery system of record**: GitHub remains source-control and engineering truth; Azure DevOps remains planning/governance-aware and integrates through Azure Boards / Azure Pipelines rather than replacing GitHub

### Adoption rule
- consume `microsoft/agent-framework` directly
- do not fork it by default
- custom-build only the Pulser-specific delta:
  - tool adapters
  - approval and guardrail logic
  - Odoo action wrappers
  - Partner Center / Google Workspace / Azure task wrappers
  - telemetry conventions

### Boundary rule
Business-domain logic, ERP parity logic, and finance-source-of-record behavior must not be implemented in the framework layer itself. Those stay in:
- Odoo / selected OCA modules
- thin `ipai_*` adapters only where required
- SSOT and platform contracts in the appropriate repos

### Anchors
- `CLAUDE.md` § Engineering Execution Doctrine + Cross-Repo Invariant #23
- `ssot/governance/upstream-adoption-register.yaml` (microsoft/agent-framework row)
- `docs/architecture/repo-adoption-register.md` (row 49)
- `ssot/governance/platform-authority-split.yaml` (GitHub vs Azure DevOps authority)
- Microsoft DevBlogs (Nov 2024): "Getting the most out of Azure DevOps and GitHub" — confirms keep-both-integrate pattern (Azure Boards GitHub app, Azure Pipelines GitHub app, GitHub Enterprise license includes ADO Basic)
