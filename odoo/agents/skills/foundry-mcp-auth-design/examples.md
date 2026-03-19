# Examples — foundry-mcp-auth-design

## Example 1: Azure-native tool — managed identity

**Input**: New MCP server for Azure Cosmos DB queries, hosted as Azure Function in `rg-ipai-dev`.

**Output**:
- MCP server: `cosmos-query-mcp` (Azure-native)
- Hosting: Azure Functions
- Auth mode: MANAGED IDENTITY (preference tier 1)
- Rationale: Azure-native hosting supports managed identity; no credentials to manage; RBAC grants Cosmos DB Data Reader role
- Entra requirements: N/A
- Key Vault requirements: N/A
- Security assessment: LOW RISK — managed identity is zero-credential, RBAC-scoped

## Example 2: External provider — OAuth2

**Input**: New MCP server for GitHub API access, hosted as Azure Function.

**Output**:
- MCP server: `github-api-mcp` (external provider)
- Hosting: Azure Functions
- Auth mode: OAUTH2 (preference tier 3)
- Rationale: GitHub supports OAuth2 App authentication; managed identity not applicable (external provider); Entra integration possible but adds complexity without benefit for GitHub API
- Entra requirements: N/A
- Key Vault requirements: OAuth2 client secret stored in `kv-ipai-dev` as `github-oauth-client-secret`; 90-day rotation policy
- Security assessment: MODERATE RISK — OAuth2 client secret in Key Vault with rotation; scoped to minimum required GitHub permissions

## Example 3: External provider — key-based (last resort)

**Input**: New MCP server for legacy internal API that only supports API keys.

**Output**:
- MCP server: `legacy-api-mcp` (external/internal legacy)
- Hosting: Azure Container Apps
- Auth mode: KEY-BASED (preference tier 4 — last resort)
- Rationale: legacy API has no OAuth2 or OIDC support; managed identity not possible for non-Azure target; Entra not supported by target API; key-based is the only option
- Entra requirements: N/A
- Key Vault requirements: API key stored in `kv-ipai-dev` as `legacy-api-key`; 30-day rotation policy; alert on rotation failure
- Security assessment: ELEVATED RISK — key-based auth requires strict rotation and monitoring; document plan to migrate to OAuth2 when legacy API is upgraded
