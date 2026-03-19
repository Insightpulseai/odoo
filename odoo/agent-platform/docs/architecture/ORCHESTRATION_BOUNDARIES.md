# Orchestration Boundaries

## What builder-factory orchestrates

- Agent creation and configuration
- Skill attachment and tool binding
- Evaluation execution and scoring
- Agent publishing to Foundry hosted runtime
- Judge review workflows (pre-publish quality gate)

## What builder-factory does NOT orchestrate

- Data pipeline execution (owned by `data-intelligence`)
- ERP transaction processing (owned by `odoo`)
- Infrastructure provisioning (owned by `infra`)
- n8n workflow execution (owned by `automations`)
- Frontend rendering (owned by `web`)

## Internal orchestration pattern

```
User request
  → builder-orchestrator (packages/builder-orchestrator)
    → builder-runner (execute agent/skill/eval)
      → builder-foundry-client (Foundry SDK calls)
    → builder-evals (evaluation harness)
  → builder-contract (shared types/schemas)
```

## External integration points

| System | Direction | Interface |
|---|---|---|
| Foundry | Read + Write | Foundry SDK (project endpoint) |
| Databricks | Read only | Agent context products (via data-intelligence) |
| Odoo | Read only | Business context (via Supabase mirror or API) |
| Azure DevOps | Read + Write | Azure DevOps MCP (work items, PRs, builds) |
| GitHub | Read + Write | GitHub API (repos, PRs, issues) |
