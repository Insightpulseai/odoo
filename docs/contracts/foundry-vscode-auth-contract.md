# Foundry / VS Code Auth Contract

> Defines the authentication path for Azure AI Foundry and VS Code extension surfaces.
> Contract: C-35
> Status: Active (auth registration pending)

---

## Purpose

Establish the canonical OAuth/OIDC authentication path for builder surfaces that connect to Azure AI Foundry, Azure DevOps, and Azure resource management from VS Code and browser.

---

## Required Entra App Registration

| Field | Value |
|-------|-------|
| Display name | `InsightPulseAI — Builder Surface` |
| Application type | Single-page application (SPA) + Public client |
| Supported account types | Single tenant (InsightPulseAI org only) |
| Tenant | InsightPulseAI Entra ID tenant |

### Redirect URIs (required)

| URI | Surface |
|-----|---------|
| `http://127.0.0.1:33418` | VS Code local OAuth callback |
| `https://vscode.dev/redirect` | VS Code for the Web / github.dev |
| `https://portal.azure.com` | Azure Portal (implicit) |

### API Permissions (minimum)

| API | Permission | Type |
|-----|------------|------|
| Azure DevOps | `user_impersonation` | Delegated |
| Azure Service Management | `user_impersonation` | Delegated |
| Microsoft Graph | `User.Read` | Delegated |
| Azure AI Foundry | project-scoped access | Delegated |

### Token configuration

- Access token version: v2
- ID token claims: `preferred_username`, `oid`, `tid`
- Token lifetime: default (1h access, 24h refresh)

---

## Canonical auth paths

| Surface | Auth method | Identity |
|---------|-------------|----------|
| Foundry web (browser) | Entra SSO via portal | User principal |
| VS Code Azure extensions | Device code / browser redirect via Entra app | User principal |
| VS Code Foundry extension | Same Entra app, project-scoped token | User principal |
| MCP servers (automated) | Managed identity or service principal | Service identity |
| Azure Pipelines | Managed identity (system-assigned) | Service identity |
| GitHub Actions | OIDC federation (`azure/login`) | Federated identity |

### Which path is canonical

- **Interactive builder work**: Entra app registration with redirect URIs above
- **CI/CD pipelines**: Managed identity (Azure Pipelines) or OIDC federation (GitHub Actions)
- **MCP automation**: Service principal with Key Vault-stored credentials

Never use personal access tokens (PATs) as the primary auth mechanism for builder surfaces.

---

## Auth completion checklist

- [ ] Register Entra app with display name and redirect URIs above
- [ ] Configure API permissions and admin consent
- [ ] Set client ID in VS Code Azure extension settings
- [ ] Verify Foundry project access via VS Code
- [ ] Verify Azure DevOps Boards access via VS Code
- [ ] Document client ID in `ssot/runtime/live-builder-surfaces.yaml` (do NOT commit the secret — ID only)
- [ ] Create service principal for MCP/pipeline automation path

---

## Invariants

1. All interactive auth flows use the same Entra app registration
2. Client ID is stored in `ssot/runtime/live-builder-surfaces.yaml` — never hardcoded in extension settings committed to git
3. Service principals for automation are separate from the interactive app registration
4. PATs are emergency-only fallback, never the primary path
5. Redirect URIs must match exactly — no wildcard redirects

---

## Cross-references

- `ssot/runtime/live-builder-surfaces.yaml` — runtime surface inventory
- `ssot/agents/mcp-baseline.yaml` — MCP control surface requirements
- `.claude/rules/security-baseline.md` — secrets policy

---

*Last updated: 2026-03-17*
