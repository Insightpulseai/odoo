# Skill: Claude MCP Integration

## Purpose

Integrates Claude with external tools and resources via Model Context Protocol (MCP). Covers MCP server registration, tool design for Claude, auth configuration, and dynamic tool discovery.

## Owner Persona

`claude-runtime-integrator`

## Skill Type

`capability_uplift` — provides MCP integration expertise beyond base model knowledge.

## Key Principles

- MCP is the standard tool integration layer
- Tool descriptions are prompt engineering — invest heavily
- Auth hierarchy: managed identity > Entra OAuth2 > API key
- Dynamic tool discovery for large tool libraries (defer_loading)

## Cross-references

- `agents/knowledge/benchmarks/claude-runtime-surfaces.md`
- `agents/skills/foundry-mcp-auth-design/` (Foundry three-plane family)
- `agents/personas/claude-runtime-integrator.md`
