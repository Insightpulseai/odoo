# Azure DevOps MCP Server

## Source

https://learn.microsoft.com/en-us/azure/devops/mcp-server/mcp-server-overview?view=azure-devops

## Weight

0.95

## Why it matters

- Official MCP integration surface for Azure DevOps
- Gives AI assistants secure local access to Boards, PRs, builds, tests, and docs
- Runs locally, free to use (aside from normal Azure DevOps / AI usage costs)
- Requires assistant to be in agent mode
- Fits target model: Azure Boards = portfolio SoR, agents need live execution context

## Allowed influence

- agent-platform tool design
- Azure Boards automation and analysis workflows
- release-ops and judge-agent context retrieval
- standup / sprint / PR / deploy assistance patterns
- work item triage and status summaries

## Must not influence

- repo topology
- Odoo module boundaries
- SSOT structure
- core platform architecture
- spec bundle design

## Primary consumers

- release-ops agent
- governance-judge
- architecture-judge
- security-judge
- maker agents needing sprint/PR/build context

## Canonical placement

```
agent-platform/tools/azure-devops-mcp/
```
