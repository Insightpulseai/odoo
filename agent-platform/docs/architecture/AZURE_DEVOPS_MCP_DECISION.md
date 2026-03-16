# Azure DevOps MCP Decision

## Decision

Adopt Azure DevOps MCP Server as the canonical MCP integration surface for Azure Boards, pull requests, builds, test plans, and related Azure DevOps artifacts.

## Role in architecture

- Azure Boards remains portfolio/execution system of record
- Azure DevOps MCP is the live AI access path (read + act)
- GitHub / spec / SSOT remain engineering truth
- Plane is optional mirror (SoW, not SoR)

## What it enables

- Standup preparation from assigned work items
- Sprint planning from backlog + capacity
- PR review with linked work-item business context
- Pipeline/build/test status retrieval
- Natural-language issue triage
- Release status summaries
- Converting agent findings into Board updates or follow-up work items

## Primary consumers

| Agent | Use case |
|---|---|
| release-ops | deploy health, release summaries, evidence linking |
| governance-judge | SSOT consistency vs Board state |
| architecture-judge | boundary compliance in linked PRs |
| security-judge | security-tagged work item tracking |
| maker agents | sprint context for implementation decisions |

## Constraints

- Runs locally (not a cloud service)
- Requires agent mode in the assistant
- Does not replace source-of-truth docs or specs
- Does not store or manage secrets
- Read-heavy by default; write operations require explicit policy gate

## Canonical placement

```
agent-platform/
  tools/
    azure-devops-mcp/
```

## Rule

Azure DevOps MCP is a **tool layer**, not doctrine. It reads and acts on Azure DevOps data. It does not define architecture, topology, or SSOT.
