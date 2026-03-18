# foundry-tool-catalog-curation

Classifies tools as approved, conditional, or forbidden for the Foundry tool baseline.

## When to use
- New tool proposed for the Foundry baseline
- Periodic or ad hoc tool catalog review
- MCP server registration request
- Quarterly audit of approved tool catalog

## Key rule
Every tool must be classified (approved/conditional/forbidden) with auth mode, trust boundary,
and rationale documented. Unregistered tools are never approved for production.
Local and remote MCP have distinct trust boundaries.

## Cross-references
- `agents/knowledge/benchmarks/microsoft-foundry-models-and-tools.md`
- `agents/personas/foundry-tool-governor.md`
- `ssot/agents/mcp-baseline.yaml`
