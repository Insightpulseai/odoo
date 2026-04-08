# Identity Architecture

> Identity subjects, trust boundaries, token flows, RBAC mapping, and Key Vault
> integration for the InsightPulse AI platform. Follows the Microsoft Entra
> identity model with three identity classes: workforce, workload, and agent.

---

## Three Identity Classes

### 1. Workforce Identity (Human Users via Entra OIDC)

Human users who access the platform through browsers or mobile apps.
Authentication flows through Microsoft Entra ID using OpenID Connect.

| Attribute | Value |
|-----------|-------|
| Identity provider | Microsoft Entra ID (primary) |
| Protocol | OpenID Connect (authorization code + PKCE) |
| Tenant | `402de71a-87ec-4302-a609-fb76098d1da7` |
| Verified domain | `insightpulseai.com` |
| MFA | Enforced at Entra Conditional Access level |
| License tier | Entra ID P2 |
| Session authority | Odoo web session (cookie-based, 7-day default) |
| Group sync | Entra groups mapped to Odoo groups (manual today, automated target) |

#### Authentication Flow

```
Browser
  --> Entra /authorize (authorization code + PKCE)
  --> Browser receives auth code
  --> Odoo /auth_oauth/signin (exchanges code for id_token)
  --> Odoo validates id_token (signature, audience, issuer, expiry)
  --> Odoo creates or matches res.users record
  --> Odoo issues session cookie
  --> User operates within Odoo's native security model
```

After the OIDC exchange, the Entra `id_token` is consumed by Odoo and not
forwarded to downstream services. The user operates entirely within Odoo's
native security model (groups, record rules, field ACLs). Entra is the
authentication authority; Odoo is the authorization authority.

#### Token Details

| Token | Issuer | Audience | Lifetime | Used by |
|-------|--------|----------|----------|---------|
| `id_token` | Entra ID | Odoo app registration (`client_id`) | 1 hour | Odoo `/auth_oauth/signin` |
| `access_token` | Entra ID | `https://graph.microsoft.com` | 1 hour | Not used by Odoo (reserved for Graph API if needed) |
| Odoo session cookie | Odoo | Odoo | 7 days (configurable) | Browser |

#### Entra App Registration (Workforce)

| Field | Value |
|-------|-------|
| Application (client) ID | `07bd9669-*` (registered in tenant `402de71a`) |
| Supported account types | Single tenant (this org only) |
| Redirect URI | `https://erp.insightpulseai.com/auth_oauth/signin` |
| Platform | Web |
| Client secret | Stored in Key Vault (`entra-client-secret`) |
| Scopes requested | `openid`, `profile`, `email` |
| Token version | v2.0 |
| ID token claims | `preferred_username`, `email`, `name`, `oid`, `groups` |

---

### 2. Workload Identity (Service-to-Service via Managed Identity)

Service principals and managed identities used for service-to-service
communication. No human interaction. No client secrets to rotate.

| Identity | Type | ACA App | Calls | Token audience |
|----------|------|---------|-------|---------------|
| `ipai-odoo-dev-web` MI | System-assigned | Odoo web | Foundry API, AI Search, Key Vault | Per-service (see below) |
| `ipai-copilot-gateway` MI | System-assigned | Copilot gateway | Foundry API, Key Vault | Per-service |
| `ipai-odoo-dev-worker` MI | System-assigned | Odoo worker | Foundry API (async), Key Vault | Per-service |
| `ipai-odoo-dev-cron` MI | System-assigned | Odoo cron | Key Vault | `vault.azure.net` |

#### Token Acquisition

Workload identities acquire tokens from the Azure Instance Metadata Service
(IMDS) endpoint. No client secrets are involved.

```
Container process
  --> GET http://169.254.169.254/metadata/identity/oauth2/token
      ?api-version=2018-02-01
      &resource={audience}
  --> IMDS returns access_token
  --> Container uses Bearer token for downstream API call
```

#### Token Scopes and Audiences

| Downstream service | Token audience | RBAC role required |
|-------------------|---------------|-------------------|
| Microsoft Foundry API | `https://cognitiveservices.azure.com/.default` | Cognitive Services OpenAI User |
| Azure Key Vault | `https://vault.azure.net/.default` | Key Vault Secrets User |
| Azure AI Search | `https://search.azure.com/.default` | Search Index Data Reader |
| Databricks SQL | `https://management.azure.com/.default` | Contributor on Databricks workspace |
| Azure Storage (ADLS) | `https://storage.azure.com/.default` | Storage Blob Data Reader |

#### Entra App Registration (Workload)

Managed identities do not require explicit app registrations. They are
automatically registered in Entra ID when the system-assigned MI is enabled on
the ACA app. The principal ID is used directly in RBAC assignments.

---

### 3. Agent Identity (Foundry Agent Identity)

AI agents hosted on Microsoft Foundry that act on behalf of users. Agent
identity is a third subject class distinct from both workforce and workload.

| Attribute | Value |
|-----------|-------|
| Runtime | Microsoft Foundry Agent Service |
| Project | `data-intel-ph` |
| Auth to Foundry API | Managed identity (workload) from copilot gateway |
| Auth for tool callbacks | Foundry-managed callback token |
| Delegation model | Agent acts as user (`user_id` passed in tool call context) |
| Audit identity | Logged as both `agent_id` and `delegated_user_id` |

#### Agent Auth Model

Microsoft Foundry requires Entra ID for Agents and Evaluations. API keys are
acceptable only for inference (completions) endpoints in development. In
production, all Foundry interactions use managed identity.

| Foundry capability | Auth method (dev) | Auth method (prod) |
|-------------------|-------------------|-------------------|
| Chat completions (inference) | API key or MI | Managed identity |
| Agent Service (hosted agents) | Managed identity | Managed identity |
| Evaluations | Managed identity | Managed identity |
| Tracing | Managed identity | Managed identity |
| Connections (data sources) | Managed identity | Managed identity |

#### Agent Delegation Chain

When a Foundry agent executes a tool (e.g., creating a journal entry in Odoo),
the full delegation chain is:

```
Human user (Entra OIDC session in Odoo)
  --> Pulser UI sends prompt to copilot gateway
  --> Gateway authenticates via Odoo session cookie
  --> Gateway calls Foundry Agent Service (MI token)
  --> Foundry Agent decides to invoke Odoo tool
  --> Agent calls back to Odoo API with:
      - Foundry callback token (agent auth)
      - user_id claim (delegated human identity)
  --> Odoo validates callback token
  --> Odoo executes tool as delegated user (user's ACL enforced)
  --> Result returned through chain
```

The agent cannot escalate beyond the delegated user's permissions. If the human
user does not have `account.group_account_manager`, the agent cannot post
journal entries on their behalf.

#### Agent Identity in Audit Logs

Every agent action produces an audit record with both identities:

| Field | Source | Example |
|-------|--------|---------|
| `agent_id` | Foundry agent registration | `pulser-finance-agent-v1` |
| `delegated_user_id` | Odoo `res.users` ID from session | `7` |
| `delegated_user_login` | Odoo user login | `maria@insightpulseai.com` |
| `action` | Tool method | `action_post` |
| `model` | Odoo model | `account.move` |
| `record_ids` | Affected records | `[42, 43]` |
| `timestamp` | UTC | `2026-03-28T08:15:42Z` |

---

## RBAC Mapping: Entra Roles to Odoo Groups

Entra groups are mapped to Odoo groups to provide a unified RBAC model. The
mapping is maintained in the `ipai_auth_oidc` module.

### Mapping Table

| Entra Group | Entra Object ID | Odoo Group | Purpose |
|-------------|----------------|-----------|---------|
| `IPAI-ERP-Users` | (configured in module) | `base.group_user` | Basic ERP access |
| `IPAI-ERP-Finance` | (configured in module) | `account.group_account_user` | Finance read access |
| `IPAI-ERP-Finance-Managers` | (configured in module) | `account.group_account_manager` | Finance write access |
| `IPAI-ERP-HR` | (configured in module) | `hr.group_hr_user` | HR access |
| `IPAI-ERP-HR-Managers` | (configured in module) | `hr.group_hr_manager` | HR management |
| `IPAI-ERP-Sales` | (configured in module) | `sales_team.group_sale_salesman` | Sales access |
| `IPAI-ERP-Sales-Managers` | (configured in module) | `sales_team.group_sale_manager` | Sales management |
| `IPAI-ERP-Inventory` | (configured in module) | `stock.group_stock_user` | Inventory access |
| `IPAI-ERP-Admin` | (configured in module) | `base.group_system` | System administration |
| `IPAI-Copilot-Admin` | (configured in module) | `ipai_copilot.group_copilot_admin` | Copilot tool and prompt configuration |

### Sync Mechanism

**Current state**: Manual mapping. When a new user authenticates via Entra
OIDC, the `ipai_auth_oidc` module reads the `groups` claim from the `id_token`
and assigns the corresponding Odoo groups.

**Target state**: Automated sync via Microsoft Graph API. A scheduled job
queries Entra group membership and reconciles Odoo group assignments. Changes
are logged in the audit trail.

### Copilot-Specific Groups

| Odoo Group | Copilot capability | Transactional scope |
|------------|-------------------|-------------------|
| `base.group_user` | Basic copilot access (informational queries) | Read only |
| `account.group_account_user` | Finance read tools (aging, trial balance) | Read only |
| `account.group_account_manager` | Finance write tools (post, reconcile) | Create, update, approve |
| `ipai_copilot.group_copilot_admin` | Tool configuration, prompt templates, agent profiles | Configuration |

---

## Trust Boundaries

```
+================================================================+
|                    INTERNET (untrusted)                         |
+================================================================+
          |
          v
+---------------------------+
|  Azure Front Door         |  TLS termination, WAF, DDoS
|  (ipai-fd-dev)            |  Geographic filtering
|  Endpoint: ipai-fd-dev-   |  Custom domains: *.insightpulseai.com
|  ep-*.azurefd.net         |
+---------------------------+
          |
          v
+================================================================+
|              ACA ENVIRONMENT (ipai-odoo-dev-env)               |
|              Trust boundary: Azure VNet + NSG                  |
|              Region: Southeast Asia                            |
+================================================================+
|                                                                |
|  +-------------------------+  +---------------------------+   |
|  | ipai-odoo-dev-web       |  | ipai-copilot-gateway      |   |
|  | Port 8069 (external)    |  | Port 8088 (internal only) |   |
|  | Workforce session auth  |  | MI auth to Foundry        |   |
|  | Odoo ACL enforcement    |  | No direct user session    |   |
|  +-------------------------+  +---------------------------+   |
|         |          |                    |                      |
|         |          |                    |                      |
|  +------v----------v----+  +-----------v--------------------+|
|  | ipai-odoo-dev-worker  |  | ipai-odoo-dev-cron            ||
|  | Internal only         |  | Internal only (singleton)     ||
|  | MI auth to KV         |  | MI auth to KV                 ||
|  +-----------------------+  +-------------------------------+|
|                                                                |
+================================================================+
          |                    |                    |
          v                    v                    v
+----------------+  +--------------------+  +----------------+
| PostgreSQL     |  | Microsoft Foundry  |  | Azure AI       |
| pg-ipai-odoo   |  | data-intel-ph      |  | Search         |
| DB auth (env   |  | MI token required  |  | srch-ipai-dev  |
| vars from KV)  |  | RBAC: Cognitive    |  | MI or admin    |
| Port 5432      |  | Services OpenAI    |  | key auth       |
+----------------+  | User               |  +----------------+
                    +--------------------+
                             |
                             v
                    +--------------------+
                    | Databricks         |
                    | dbw-ipai-dev       |
                    | MI or SP auth      |
                    | Unity Catalog RLS  |
                    +--------------------+
          |
          v
+---------------------------+
|  Azure Key Vault          |  Secrets: MI access only
|  (kv-ipai-dev)            |  No network exposure
|  No public endpoint       |  RBAC: Key Vault Secrets User
+---------------------------+
```

### Trust Boundary Rules

1. **Internet to ACA**: All traffic passes through Azure Front Door. No direct access to ACA container IPs.
2. **ACA to PostgreSQL**: Database credentials from Key Vault. Connection over private network (Azure internal).
3. **ACA to Foundry**: Managed identity token. No API keys in production.
4. **ACA to Key Vault**: Managed identity token. No network exposure.
5. **Foundry to Odoo (callback)**: Foundry-managed callback token validated by the copilot gateway.
6. **Cross-ACA**: Internal ACA apps communicate over the shared ACA environment network. No internet traversal.

---

## Token Flows

### Flow A: Workforce Login (Entra OIDC)

```
Browser
  --> GET https://login.microsoftonline.com/402de71a.../oauth2/v2.0/authorize
      ?client_id=07bd9669-*
      &redirect_uri=https://erp.insightpulseai.com/auth_oauth/signin
      &response_type=code
      &scope=openid profile email
      &code_challenge=...
      &code_challenge_method=S256
  --> Entra authenticates user (MFA if required by Conditional Access)
  --> Redirect to Odoo with authorization code
  --> Odoo exchanges code for id_token (back-channel)
  --> Odoo validates id_token:
      - Signature (Entra JWKS)
      - Issuer: https://login.microsoftonline.com/402de71a.../v2.0
      - Audience: 07bd9669-*
      - Expiry: not expired
  --> Odoo matches user by email or creates new res.users
  --> Odoo assigns groups based on Entra groups claim
  --> Odoo issues session cookie (HttpOnly, Secure, SameSite=Lax)
```

### Flow B: Workload to Foundry (Managed Identity)

```
Copilot gateway (ACA)
  --> GET http://169.254.169.254/metadata/identity/oauth2/token
      ?api-version=2018-02-01
      &resource=https://cognitiveservices.azure.com
  --> IMDS returns access_token (aud: cognitiveservices.azure.com)
  --> POST https://data-intel-ph-resource.openai.azure.com/openai/...
      Authorization: Bearer {mi_token}
```

### Flow C: Workload to Key Vault (Managed Identity)

```
Odoo ACA
  --> GET http://169.254.169.254/metadata/identity/oauth2/token
      ?api-version=2018-02-01
      &resource=https://vault.azure.net
  --> IMDS returns access_token (aud: vault.azure.net)
  --> GET https://kv-ipai-dev.vault.azure.net/secrets/odoo-db-password
      Authorization: Bearer {mi_token}
```

### Flow D: Agent to Odoo Tool (Foundry Callback)

```
Foundry Agent Service
  --> Agent decides to call Odoo tool (e.g., action_post)
  --> POST https://erp.insightpulseai.com/api/copilot/tool/execute
      (routed internally via ACA to copilot gateway)
      Authorization: Bearer {foundry_callback_token}
      X-Delegated-User-Id: 7
  --> Copilot gateway validates:
      - Callback token (registered in Foundry agent config)
      - Delegated user_id exists and is active
  --> Gateway calls Odoo ORM as delegated user
      (using Odoo's sudo-less context with user_id=7)
  --> Result returned to Foundry Agent
```

### Flow E: Workload to Databricks SQL

```
Copilot gateway (ACA)
  --> GET http://169.254.169.254/metadata/identity/oauth2/token
      ?api-version=2018-02-01
      &resource=https://management.azure.com
  --> IMDS returns access_token
  --> POST https://adb-*.azuredatabricks.net/api/2.0/sql/statements
      Authorization: Bearer {mi_token}
      warehouse_id: e7d89eabce4c330c
      statement: SELECT ... FROM gold.fact_invoice_line WHERE ...
```

---

## Azure RBAC Assignments

| Principal | Role | Scope | Purpose |
|-----------|------|-------|---------|
| `ipai-odoo-dev-web` MI | Cognitive Services OpenAI User | `data-intel-ph-resource` | Foundry inference |
| `ipai-odoo-dev-web` MI | Key Vault Secrets User | `kv-ipai-dev` | Secret retrieval |
| `ipai-copilot-gateway` MI | Cognitive Services OpenAI User | `data-intel-ph-resource` | Foundry agent calls |
| `ipai-copilot-gateway` MI | Key Vault Secrets User | `kv-ipai-dev` | Secret retrieval |
| `ipai-copilot-gateway` MI | Search Index Data Reader | `srch-ipai-dev` | AI Search queries |
| `ipai-odoo-dev-worker` MI | Cognitive Services OpenAI User | `data-intel-ph-resource` | Async Foundry calls |
| `ipai-odoo-dev-worker` MI | Key Vault Secrets User | `kv-ipai-dev` | Secret retrieval |
| `ipai-odoo-dev-cron` MI | Key Vault Secrets User | `kv-ipai-dev` | Secret retrieval |
| Platform team (Entra group) | Contributor | `rg-ipai-dev-odoo-runtime` | Infrastructure management |

---

## Key Vault Integration

### Architecture

```
ACA managed identity
  --> RBAC: Key Vault Secrets User on kv-ipai-dev
  --> Secret reference in ACA environment config
  --> Injected as environment variable at container start
  --> Application reads env var (never calls KV at runtime)
```

### Secret Inventory

| Secret name | Consumer(s) | Purpose | Rotation |
|-------------|------------|---------|----------|
| `odoo-db-host` | web, worker, cron | PostgreSQL hostname | On infra change |
| `odoo-db-user` | web, worker, cron | PostgreSQL user | On infra change |
| `odoo-db-password` | web, worker, cron | PostgreSQL password | 90-day rotation |
| `azure-openai-api-key` | copilot gateway (fallback) | Foundry API key (dev only) | MI preferred in prod |
| `zoho-smtp-user` | web | Outbound email sender | On credential change |
| `zoho-smtp-password` | web | Outbound email auth | On credential change |
| `entra-client-secret` | web | OIDC client authentication | Per Entra app policy |

### Rules

1. No secrets in `odoo.conf`, `.env` files in git, or container image layers
2. All secrets accessed via managed identity -- no shared access keys
3. Secret names follow `kebab-case` convention
4. Key Vault has no public network access (private endpoint only)
5. Rotation events are logged in Key Vault audit log (Azure Monitor)

---

## Design Principles

1. **Managed Identity first** -- eliminate client secrets for all Azure-to-Azure communication
2. **Least privilege** -- each managed identity gets only the RBAC roles it needs for its specific function
3. **No credential sharing** -- each ACA app has its own system-assigned managed identity
4. **User context preservation** -- agents and workloads carry the originating `user_id` through the full delegation chain
5. **Audit separation** -- workforce, workload, and agent actions are distinguishable in logs by identity class
6. **Zero secrets in code** -- all secrets via Key Vault, injected at runtime as environment variables
7. **Entra authenticates, Odoo authorizes** -- Entra is the identity provider; Odoo's group/rule system is the authorization authority
8. **Agent cannot escalate** -- Foundry agents operate within the delegated user's permission boundary, never beyond it
