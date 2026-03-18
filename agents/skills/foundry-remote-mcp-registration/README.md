# foundry-remote-mcp-registration

Standardizes how new enterprise tools become Foundry MCP tools via Azure Functions, API Center, or ACA patterns.

## When to use
- New tool integration requires MCP registration
- Setting up a remote MCP server
- Onboarding an enterprise tool to Foundry

## Key rule
Auth must be configured before registration. Azure Functions is preferred for new internal tools.
Every registered tool must have connectivity validation evidence and a documented trust boundary.
Registration updates `ssot/agents/mcp-baseline.yaml`.

## Cross-references
- `agents/knowledge/benchmarks/microsoft-foundry-models-and-tools.md`
- `agents/personas/foundry-tool-governor.md`
- `agents/skills/foundry-mcp-auth-design/skill-contract.yaml`
- `ssot/agents/mcp-baseline.yaml`
