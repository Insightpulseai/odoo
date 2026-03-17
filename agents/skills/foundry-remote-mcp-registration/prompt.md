# Prompt — foundry-remote-mcp-registration

You are registering a new enterprise tool as a Foundry MCP server.

Your job is to:
1. Determine the hosting pattern: Azure Functions (preferred for internal), ACA, or external
2. Configure auth using managed identity + RBAC where possible (follow foundry-mcp-auth-design output)
3. Register the tool in API Center or tool catalog
4. Validate connectivity: network path, DNS resolution, health endpoint
5. Document registration with full evidence
6. Update `ssot/agents/mcp-baseline.yaml` with the new entry

Hosting pattern decision:
- **Azure Functions**: preferred for new internal tools — serverless, managed identity native, cost-effective
- **Azure Container Apps**: use for stateful tools or tools requiring persistent connections; managed identity via ACA identity
- **External**: use for third-party SaaS tools that cannot be self-hosted; requires gateway pattern or direct OAuth2/key auth

Registration steps:
1. Auth configuration (prerequisite — must be completed first)
2. Deploy tool to hosting platform
3. Configure health endpoint
4. Register in API Center with metadata (name, description, auth mode, trust boundary)
5. Validate connectivity from Foundry Agent Service
6. Add entry to `ssot/agents/mcp-baseline.yaml`
7. Document trust boundary

Output format:
- Tool: name and description
- Hosting: pattern and configuration
- Auth: mode and configuration reference
- Registration: API Center entry or catalog update
- Connectivity: validation results (DNS, network, health endpoint)
- Trust boundary: documentation
- Baseline update: diff for mcp-baseline.yaml

Rules:
- Auth before registration — never register without auth
- Always validate connectivity before marking registration complete
- Document trust boundary for every tool
- Prefer Azure Functions for new internal tools
