# Microsoft MCP Server for Enterprise — Skill Contract

> Status: **Pilot**
> Source: https://github.com/microsoft/EnterpriseMCP
> Tenant: InsightPulseAI Entra tenant
> App ID: `e8c77dc2-69b3-43f4-bc51-3213c9d915b4` (Microsoft's server-side)

---

## When to use

- Query Entra tenant data: users, groups, app registrations, service principals
- Audit security posture: auth methods, Conditional Access, Security Defaults
- Check privileged access: directory roles, PIM status, role assignments
- Review application risk: app permissions, ownerless apps, external apps
- Inspect device readiness: compliance, join state, OS distribution
- Investigate sign-in/audit logs, provisioning telemetry
- Check license usage and hygiene: unused apps, stale groups, domain config

## When NOT to use

- Write operations (not yet supported — read-only in public preview)
- M365 data (covered by Agent 365, not this MCP server)
- Sovereign cloud tenants (not yet supported)
- Bulk user provisioning (use Graph API or Azure DevOps pipelines directly)

## Architecture

The MCP server exposes only 3 tools via RAG + few-shot prompting:

| Tool | Purpose |
|------|---------|
| `microsoft_graph_suggest_queries` | Finds relevant Graph API calls from natural language |
| `microsoft_graph_get` | Executes read-only Graph API calls with user RBAC |
| `microsoft_graph_list_properties` | Retrieves entity properties for grounding |

All operations use delegated permissions and respect Microsoft Graph throttling (100 req/min/user).

## Prerequisites

### One-time tenant provisioning (requires Entra admin)

```powershell
# 1. Install Entra PowerShell module (v1.0.13+)
Install-Module Microsoft.Entra.Beta -Force -AllowClobber

# 2. Connect to tenant
Connect-Entra -Scopes 'Application.ReadWrite.All', 'DelegatedPermissionGrant.ReadWrite.All'

# 3. Register MCP Server and grant permissions to VS Code
Grant-EntraBetaMCPServerPermission -ApplicationName VisualStudioCode
```

### If Microsoft Graph PowerShell SDK conflicts

```powershell
Install-Module Uninstall-Graph
Uninstall-Graph -All
```

### VS Code configuration

1. Install Microsoft MCP Server for Enterprise extension in VS Code
2. Login with admin account from the provisioned tenant
3. Open Copilot Chat and query tenant data

### Azure Foundry configuration

1. Navigate to Azure Foundry Portal → Agents → Create agent
2. Tools → Add → Catalog → search "Microsoft MCP Server for Enterprise"
3. Add MCP Client ID, configure redirect URI, connect
4. Open Consent with admin account

## Supported query categories

| Category | Examples |
|----------|---------|
| Security posture | "What auth methods are configured?", "Show Conditional Access policies" |
| Privileged access | "Who has Global Admin role?", "Show PIM-eligible assignments" |
| Application risk | "List ownerless app registrations", "Which apps have mail.read permission?" |
| Access governance | "Who has access to this group?", "Show pending access reviews" |
| Device readiness | "How many non-compliant devices?", "Show stale devices" |
| Investigation | "Show failed sign-ins last 7 days", "Audit log for app registration changes" |
| Hygiene | "Unused licenses", "Stale groups with no members" |

## Auth model

- Delegated permissions only (user context)
- MCP.* scopes mirror Microsoft Graph scopes
- Admin consent required for tenant-wide access
- All operations auditable via Microsoft Graph activity logs

### Audit query (KQL)

```kusto
MicrosoftGraphActivityLogs
| where TimeGenerated >= ago(30d)
| where AppId == "e8c77dc2-69b3-43f4-bc51-3213c9d915b4"
| project RequestId, TimeGenerated, UserId, RequestMethod, RequestUri, ResponseStatusCode
```

## Custom MCP client registration

For Claude, ChatGPT, or GitHub Copilot CLI:

```powershell
# Grant specific scopes to a custom MCP client
Grant-EntraBetaMCPServerPermission -ApplicationId "<MCP_Client_App_Id>" -Scopes "MCP.User.Read", "MCP.Group.Read"

# Revoke scopes
Revoke-EntraBetaMCPServerPermission -ApplicationId "<MCP_Client_App_Id>" -Scopes "MCP.User.Read"
```

## Integration with InsightPulseAI

| Use case | Flow |
|----------|------|
| Odoo user provisioning audit | Query Entra users → compare with Odoo `res.users` |
| App registration governance | List all app registrations → reconcile with SSOT |
| Sign-in monitoring | Query sign-in logs → feed to Fabric analytics |
| Conditional Access review | Audit policies → document in governance SSOT |
| Gmail addon app verification | Check app registration status and permissions |

## Limitations

- Read-only (write operations planned for future release)
- Public cloud only (sovereign clouds planned)
- 100 requests/minute/user rate limit
- Subject to Microsoft Graph throttling
- No Dynamic Client Registration (DCR) yet

## Safety

- Use read-only queries for investigation and audit
- Do not attempt write operations (will fail)
- All queries run under the authenticated user's RBAC scope
- Audit all MCP operations via Graph activity logs

---

*Created: 2026-03-27. Review when write operations become available.*
