# Identity and Access

> Workforce, workload, and agent identity model for Odoo Copilot on Azure.

## Identity Subjects

### 1. Workforce Identity (Human Users)

Users who interact with the copilot through the Odoo web client.

| Attribute | Value |
|-----------|-------|
| Identity provider | Microsoft Entra ID |
| Auth protocol | OpenID Connect |
| Odoo mapping | `res.users` with `oauth_provider_id` pointing to Entra |
| Group membership | Synced from Entra groups to Odoo groups (target) |
| Session | Odoo web session cookie after OIDC exchange |
| MFA | Enforced at Entra ID level |

Supported providers for Odoo login:
- Entra ID (primary, workforce)
- Google OAuth (secondary, external collaborators)

### 2. Workload Identity (Service-to-Service)

Backend services that call Foundry, Search, or Odoo APIs on behalf of the copilot.

| Attribute | Value |
|-----------|-------|
| Identity type | Azure Managed Identity (system-assigned on ACA) |
| Token audience | `https://cognitiveservices.azure.com/.default` (Foundry) |
| Auth flow | Managed Identity -> token endpoint -> bearer token |
| No secrets | Managed Identity eliminates client secrets for Azure-to-Azure calls |

Workload identity subjects:

| Service | Identity | Calls |
|---------|----------|-------|
| `ipai-odoo-dev-web` | System-assigned MI | Foundry API, Search API |
| `ipai-copilot-gateway` | System-assigned MI | Foundry API, Odoo internal API |
| `ipai-odoo-dev-worker` | System-assigned MI | Foundry API (async tool execution) |

### 3. Agent Identity (Future -- Foundry Agent Service)

When migrating to hosted agents, the Foundry Agent Service manages agent
identity for tool callbacks.

| Attribute | Value |
|-----------|-------|
| Identity type | Foundry-managed agent identity |
| Tool callback auth | Bearer token scoped to tool endpoint |
| Odoo endpoint auth | Agent presents token; Odoo validates against known agent registration |
| Principle | Agent identity is distinct from user identity -- agent acts on behalf of user but with its own credential |

## Trust Boundaries

```
+---------------------------+
|  Browser (User Agent)     |  Workforce identity (OIDC session)
+---------------------------+
          |
          v
+---------------------------+
|  Azure Front Door         |  TLS termination, WAF
+---------------------------+
          |
          v
+---------------------------+
|  Odoo ACA (web)           |  Odoo session validates user
|  ipai_odoo_copilot        |  Copilot respects user's Odoo ACLs
+---------------------------+
          |
          v (Managed Identity token)
+---------------------------+
|  Azure AI Foundry         |  Workload identity (MI token)
|  data-intel-ph            |  Model inference + tool orchestration
+---------------------------+
          |
          v (Tool callback with agent token)
+---------------------------+
|  Odoo FastAPI / JSON-RPC  |  Tool endpoint validates agent token
|  ipai_copilot_actions     |  Executes as delegated user context
+---------------------------+
          |
          v
+---------------------------+
|  PostgreSQL               |  DB-level access via Odoo ORM only
|  pg-ipai-odoo             |
+---------------------------+
```

## Role-Based Access

Copilot tool access is governed by Odoo group membership:

| Odoo Group | Copilot Capability |
|------------|-------------------|
| `base.group_user` | Read-only queries, basic navigation |
| `account.group_account_user` | Finance read tools, reconciliation queries |
| `account.group_account_manager` | Finance write tools, close support |
| `hr_expense.group_hr_expense_team_approver` | Expense approval actions |
| `ipai_copilot.group_copilot_admin` | Tool configuration, prompt management |

## Token Flows

### User -> Copilot (Workforce)

```
1. User authenticates via Entra OIDC -> Odoo session established
2. User sends copilot message via Odoo web client (session cookie)
3. Odoo validates session, extracts user context (uid, groups, company)
4. Copilot module constructs prompt with user context
5. Copilot calls Foundry using workload identity (MI token, not user token)
6. Foundry response rendered to user via Odoo web client
```

### Copilot -> Foundry (Workload)

```
1. ACA managed identity requests token for cognitiveservices.azure.com
2. Token included as Bearer in Foundry API call
3. Foundry validates token against tenant 402de71a-...
4. Request processed, response returned
```

### Foundry -> Odoo Tool Callback (Agent, future)

```
1. Foundry agent decides to call an Odoo tool
2. Agent presents callback token to Odoo FastAPI endpoint
3. Odoo validates token against registered agent identity
4. Tool executes in delegated user context (user_id from original request)
5. Result returned to Foundry agent
```
