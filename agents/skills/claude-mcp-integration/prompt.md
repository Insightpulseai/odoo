# Claude MCP Integration — Prompt

You are integrating Claude with external tools via MCP (Model Context Protocol).

## Tool Design (Most Important Step)

Tool descriptions directly impact agent success. Anthropic observed 40% task time reduction from description improvements alone.

### Naming
- Use namespace prefixes: `service_resource_action` (e.g., `odoo_sale_create`, `azure_keyvault_get_secret`)
- Test naming schemes empirically — small changes have measurable impact

### Descriptions
- Describe capability, not implementation
- Include domain terminology, query formats, resource relationships
- Be specific about parameter expectations
- Include specialized query syntax if applicable

### Responses
- Return only high-signal data
- Strip technical noise (UUIDs, MIME types unless needed)
- Implement optional `response_format` parameter (detailed vs. concise)
- Apply pagination with sensible defaults

### Errors
- Replace opaque codes with specific, actionable guidance
- Errors should teach the agent what went wrong and how to fix it

## Auth Selection

1. **Managed identity** (preferred) — zero-secret, Azure-native
2. **Entra OAuth2** — token-based, auditable
3. **API key** — last resort, Key Vault-sourced

## Dynamic Discovery (if >10 tools)

- Mark infrequent tools with `defer_loading: true`
- Keep 3-5 most-used tools always loaded
- Provide search/discovery tool for on-demand loading
- Accuracy improved 49% → 74% with this approach

## Output

```
MCP Server: [name]
Tools: [count] ([always loaded] + [deferred])
Auth: [method]
Tool schema: [key tools with descriptions]
Discovery: [enabled/disabled]
```
