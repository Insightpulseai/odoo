# MCP Usage

## Purpose

Use MCP as a tool-access layer for:

- Azure runtime inspection
- Azure DevOps delivery inspection
- Microsoft docs grounding
- Browser verification
- Document normalization

## Active servers

| Server | Category | Priority |
|--------|----------|----------|
| Azure MCP Server | infra | 1 |
| Azure DevOps MCP | delivery | 2 |
| Microsoft Learn MCP | grounding | 3 |
| Playwright | verification | 4 |
| Markitdown | transformation | 5 |

## Rules

- Odoo has no direct MCP runtime dependency
- MCP tools are read-only by default
- Production mutations require explicit approval flows
- Registry of record: `platform/mcp/registry.yaml`
- Access policy: `platform/mcp/policy.yaml`

## Deferred (not yet active)

- Azure AI Foundry MCP (experimental)
- Microsoft MCP Server for Enterprise (Entra NL lookup)
- Fabric RTI MCP (Eventhouse/KQL)
