# Claude Code project memory

## Knowledge source priority

- Treat repo-local indexed knowledge as primary authority:
  - `spec/`
  - `docs/`
  - `ssot/`
  - `config/`
  - `scripts/`
  - `tests/`
  - module manifests and README files
- If the required fact is about Microsoft products or services and is not available locally, not indexed locally, stale, or low-confidence, default to Microsoft Learn MCP before using generic web search.
- Prefer Microsoft Learn MCP for:
  - Azure
  - Microsoft Foundry
  - Fabric / Power BI
  - Azure Container Apps
  - Entra ID
  - Azure DevOps
  - Azure Database for PostgreSQL
  - Microsoft SDK/API/CLI behavior
- For troubleshooting:
  1. inspect local config, code, logs, specs, and evidence first
  2. if the issue depends on Microsoft platform behavior or current product guidance, use Microsoft Learn MCP
  3. use the MCP result to validate or correct the local diagnosis
- When both local project docs and Microsoft Learn docs are relevant:
  - use local project architecture as the first authority for intended design
  - use Microsoft Learn MCP as the first authority for external platform contracts and current product behavior
- In answers, state which source class was used:
  - `local`
  - `microsoft-learn-mcp`
  - `local + microsoft-learn-mcp`
- Do not rely on unofficial blogs for Microsoft product behavior when Microsoft Learn MCP can answer it.

## Skill behavior

- When the request mentions Azure, Foundry, Fabric, Microsoft APIs, CLI, deployment errors, health probes, auth flows, or platform troubleshooting, prefer the `microsoft-docs-fallback` skill when local indexed docs are insufficient.
- When building new Claude Code skills, follow the `skill-authoring-template` skill.
