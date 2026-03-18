# Builder Factory

Agent builder workspace inside `agent-platform`. Creates, tests, evaluates, and publishes agents to Microsoft Foundry.

## Boundary

- Runtime/orchestration/publishing/contracts → here (`agent-platform`)
- Personas/skills/judges/templates/knowledge → `agents/`
- Promotion to standalone repo: see `docs/architecture/BUILDER_FACTORY_RUNTIME.md`

## Packages

| Package | Purpose |
|---|---|
| `builder-contract` | Shared types and schemas |
| `builder-orchestrator` | Agent creation/eval orchestration |
| `builder-runner` | Execution runtime |
| `builder-foundry-client` | Foundry SDK integration |
| `builder-evals` | Evaluation harness |
