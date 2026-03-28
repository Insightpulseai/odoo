# Authentication Flow

> OIDC login, Odoo user mapping, and backend workload authentication.

## Overview

Three authentication flows operate in the copilot system:

1. **User login** -- Entra ID OIDC -> Odoo session (workforce)
2. **Copilot backend** -- Managed Identity -> Foundry token (workload)
3. **Tool callback** -- Foundry agent -> Odoo endpoint (agent, future)

## Flow 1: User Login (Entra ID OIDC)

```
Browser                  Odoo                     Entra ID
  |                        |                         |
  |-- GET /web/login ----->|                         |
  |<-- 302 Entra auth -----|                         |
  |-- GET /authorize ------|------------------------>|
  |                        |                         |
  |<-- 302 callback + code |<------------------------|
  |-- GET /auth_oauth/signin?code=... ------------->|
  |                        |-- POST /token --------->|
  |                        |<-- id_token + access_token
  |                        |                         |
  |                        |-- Validate id_token     |
  |                        |-- Map to res.users      |
  |                        |-- Create Odoo session   |
  |<-- Set-Cookie: session_id                        |
  |                        |                         |
```

### Entra App Registration

| Parameter | Value |
|-----------|-------|
| Tenant | `402de71a-87ec-4302-a609-fb76098d1da7` |
| Redirect URI | `https://erp.insightpulseai.com/auth_oauth/signin` |
| Scopes | `openid profile email` |
| Token version | v2.0 |
| Grant type | Authorization Code + PKCE |

### Odoo OAuth Provider Configuration

```
Name: Microsoft Entra ID
Auth endpoint: https://login.microsoftonline.com/402de71a-.../oauth2/v2.0/authorize
Token endpoint: https://login.microsoftonline.com/402de71a-.../oauth2/v2.0/token
Client ID: <from Entra app registration>
Scope: openid profile email
Validation endpoint: https://login.microsoftonline.com/402de71a-.../oauth2/v2.0/userinfo
Data endpoint: https://graph.microsoft.com/v1.0/me
Enabled: True
```

### User Mapping

On first OIDC login, Odoo creates or matches a `res.users` record:

| Entra claim | Odoo field |
|-------------|-----------|
| `sub` | `oauth_uid` |
| `email` | `login` (email = login in Odoo) |
| `name` | `name` |
| `preferred_username` | `login` (fallback) |

Matching priority: `oauth_uid` (exact) > `email` (case-insensitive).

If no match, a new user is created with default groups per Odoo's OAuth
provider configuration.

## Flow 2: Google OAuth (Secondary)

For external collaborators using Google accounts:

| Parameter | Value |
|-----------|-------|
| Auth endpoint | `https://accounts.google.com/o/oauth2/v2/auth` |
| Scope | `openid email profile` |
| Mapping | Same `oauth_uid` / email matching as Entra |

Google OAuth users are assigned `base.group_portal` by default unless
explicitly promoted.

## Flow 3: Copilot Backend (Managed Identity)

The copilot backend authenticates to Azure AI Foundry using the ACA's
system-assigned managed identity. No client secrets are involved.

```
Odoo ACA                 Azure IMDS               Azure AI Foundry
  |                        |                         |
  |-- GET /metadata/identity/oauth2/token?resource=  |
  |   https://cognitiveservices.azure.com             |
  |                        |                         |
  |<-- { access_token }    |                         |
  |                        |                         |
  |-- POST /openai/deployments/gpt-4.1/... -------->|
  |   Authorization: Bearer <token>                  |
  |                        |                         |
  |<-- { response }        |<------------------------|
```

### Token Details

| Parameter | Value |
|-----------|-------|
| Resource / scope | `https://cognitiveservices.azure.com/.default` |
| Token lifetime | ~1 hour (auto-refreshed by Azure SDK) |
| Identity | System-assigned MI on `ipai-odoo-dev-web` |
| RBAC role | `Cognitive Services OpenAI User` on `data-intel-ph-resource` |

### Fallback: API Key Auth

If managed identity is not configured (e.g., local dev), the module falls back
to API key authentication:

```
AZURE_OPENAI_API_KEY env var -> api-key header
```

API key auth is acceptable for development only. Production must use managed
identity.

## Flow 4: Tool Callback (Future -- Foundry Agent)

When Foundry Agent Service calls back to Odoo to execute a tool:

```
Foundry Agent            Odoo FastAPI Endpoint
  |                        |
  |-- POST /api/copilot/tool/execute
  |   Authorization: Bearer <agent_callback_token>
  |   Body: { tool: "read_invoice", args: {...}, user_context: { uid: 42 } }
  |                        |
  |                        |-- Validate agent_callback_token
  |                        |-- Switch to user context (uid=42)
  |                        |-- Execute tool via ORM
  |                        |-- Return result
  |                        |
  |<-- { result: {...} }   |
```

The callback token is issued by Foundry and validated by the Odoo endpoint
against the registered agent identity. The `user_context.uid` is the original
requesting user -- tools execute with that user's permissions.

## Session Lifetime

| Session type | Lifetime | Refresh |
|-------------|----------|---------|
| Odoo web session | 7 days (configurable) | Extended on activity |
| Entra access token | ~1 hour | Refresh token (OIDC) |
| MI token (Foundry) | ~1 hour | Auto-refreshed by SDK |
| Agent callback token | Per-request | Issued per tool call |
