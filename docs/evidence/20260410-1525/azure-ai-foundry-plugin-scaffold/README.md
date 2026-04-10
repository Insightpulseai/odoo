# Azure AI Foundry Plugin Scaffold Evidence

Timestamp: `20260410-1525`

Scope:
- Confirmed the repo already carried the Azure AI Foundry plugin manifest and marketplace entry.
- Added `plugins/azure-ai-foundry/.mcp.json` as a real plugin MCP config instead of an empty stub.
- Added `plugins/azure-ai-foundry/assets/.gitkeep` so the scaffolded assets directory is preserved in Git.

Verification:
- `python3 -m json.tool plugins/azure-ai-foundry/.codex-plugin/plugin.json`
- `python3 -m json.tool plugins/azure-ai-foundry/.mcp.json`
- `python3 -m json.tool .agents/plugins/marketplace.json`
- `git diff --check -- .agents/plugins/marketplace.json plugins/azure-ai-foundry docs/evidence/20260410-1525/azure-ai-foundry-plugin-scaffold`

Artifacts:
- `plugin.json.pretty.json`
- `mcp.pretty.json`
- `marketplace.pretty.json`

Source basis:
- Microsoft Learn preview docs identify the Foundry MCP endpoint as `https://mcp.ai.azure.com`.
- The MCP Registry lists Azure AI Foundry as an experimental MCP server from Microsoft.

Result:
- JSON validation passed for the plugin manifest, plugin MCP config, and marketplace manifest.
- `git diff --check` passed with no whitespace errors.
- The plugin now contains a concrete MCP server definition for the Microsoft Foundry preview endpoint.
