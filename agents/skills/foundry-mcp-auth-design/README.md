# foundry-mcp-auth-design

Chooses auth mode per MCP server using a strict preference order: managed identity > Entra OAuth2 > OAuth2 > key-based.

## When to use
- New MCP server requires auth configuration
- Reviewing auth mode for an existing MCP server
- Security audit of MCP auth posture

## Key rule
Managed identity and Entra are preferred for Azure-native tools. Key-based auth is last resort
and requires Key Vault storage. Every auth decision must be documented with rationale explaining
why a lower-preference mode was chosen (if applicable).

## Cross-references
- `agents/knowledge/benchmarks/microsoft-foundry-models-and-tools.md`
- `agents/personas/foundry-tool-governor.md`
- `docs/contracts/foundry-vscode-auth-contract.md` (C-35)
