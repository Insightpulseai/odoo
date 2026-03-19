---
name: Entra Identity Governance
description: Review and implement Microsoft Entra ID, Key Vault, managed identity, workload identity, conditional access, and Agent ID configurations for InsightPulseAI platform
---

# Entra Identity Governance Skill

## When to use

When reviewing, implementing, or auditing:
- Microsoft Entra ID configuration (users, groups, roles, app registrations)
- Azure Key Vault access policies and RBAC assignments
- Managed identity configuration for Container Apps, Front Door, APIM
- Workload identity federation for GitHub Actions or external services
- Conditional access policies for users, workloads, and AI agents
- Entra Agent ID registration and governance for AI agent identities
- Zero Trust architecture alignment

## Platform Context

### Current State (InsightPulseAI)

| Component | Resource | Environment | Status |
|-----------|----------|-------------|--------|
| Key Vault | `ipai-odoo-dev-kv` | dev | Active |
| Key Vault | `ipai-odoo-staging-kv` | staging | **Missing** |
| Key Vault | `ipai-odoo-prod-kv` | prod | **Missing** |
| Managed Identity | `mi-ipai-odoo-dev` | dev | Active (rg-ipai-shared-dev) |
| Managed Identity | `mi-ipai-odoo-staging` | staging | Active (rg-ipai-shared-staging) |
| Managed Identity | `mi-ipai-odoo-prod` | prod | Active (rg-ipai-shared-prod) |
| SSO | Keycloak | transitional | Migrating to Entra |
| App Registration | InsightPulseAI | all | Active with 15 app roles |

### Target Architecture

```
                    ┌──────────────────────────────────┐
                    │     Microsoft Entra ID Tenant     │
                    │   (insightpulseai.com directory)  │
                    ├──────────────────────────────────┤
                    │                                   │
  ┌─────────────┐   │  ┌─────────────┐  ┌───────────┐  │
  │ Human Users │───│──│ Conditional │──│ App Roles │  │
  │ (Entra ID)  │   │  │   Access    │  │  (RBAC)   │  │
  └─────────────┘   │  └──────┬──────┘  └─────┬─────┘  │
                    │         │               │         │
  ┌─────────────┐   │  ┌──────▼──────┐  ┌─────▼─────┐  │
  │ AI Agents   │───│──│ Agent ID    │──│ Workload  │  │
  │ (Entra      │   │  │ (Identity   │  │ Identity  │  │
  │  Agent ID)  │   │  │  Protection)│  │ (Fed/MI)  │  │
  └─────────────┘   │  └─────────────┘  └─────┬─────┘  │
                    │                          │        │
                    └──────────────────────────┼────────┘
                                               │
                    ┌──────────────────────────┼────────┐
                    │    Azure Resources        │        │
                    │                           ▼        │
                    │  ┌────────────────────────────┐    │
                    │  │ Key Vault (per environment) │    │
                    │  │  dev / staging / prod       │    │
                    │  └─────────────┬──────────────┘    │
                    │                │                    │
                    │  ┌─────────────▼──────────────┐    │
                    │  │ Container Apps (ACA)        │    │
                    │  │  web / worker / cron        │    │
                    │  └────────────────────────────┘    │
                    │                                     │
                    │  ┌────────────────────────────┐    │
                    │  │ PostgreSQL / ACR / Front Door│   │
                    │  └────────────────────────────┘    │
                    └─────────────────────────────────────┘
```

## Checks

### Key Vault Requirements

1. **One vault per environment** — dev, staging, prod (Microsoft recommendation)
2. **RBAC authorization enabled** — `enableRbacAuthorization: true` (never legacy access policies)
3. **Soft delete + purge protection** — 90-day retention, enabled
4. **Managed identity access** — `Key Vault Secrets User` role for Container Apps identities
5. **Diagnostic logging** — audit logs to Log Analytics workspace
6. **Network ACLs** — `bypass: 'AzureServices'`, restrict public access in prod

### Managed Identity Requirements

1. **User-assigned for Container Apps creation** — system-assigned not available at `create` time
2. **Scoped identity availability** — use `None` scope for identities only needed for ACR/Key Vault
3. **Separate identities per environment** — never share across dev/staging/prod
4. **RBAC role assignments**:
   - `Key Vault Secrets User` for secret reading
   - `AcrPull` for container image pull
   - `Key Vault Certificates User` for TLS certificates (Front Door)

### Workload Identity Federation

1. **GitHub Actions** — federate with user-assigned MI, not secrets
2. **Max 20 federated credentials** per app/MI
3. **Use RS256-signed tokens** — only supported algorithm
4. **Audience**: `api://AzureADTokenExchange`
5. **Sequential creation** — create federated credentials one at a time

### Conditional Access (Zero Trust)

1. **Workload identity policies** — block service principals outside known IP ranges
2. **Risk-based policies** — auto-block compromised workload identities
3. **Agent ID policies** — apply CA to AI agents (preview)
4. **Continuous Access Evaluation (CAE)** — enable for workload identities
5. **Requires Workload Identities Premium license**

### Entra Agent ID (Preview)

1. **Agent Registry** — register all AI agents (Claude, Pulser, Copilot) in Entra
2. **Agent Blueprints** — define reusable templates for agent types
3. **Sponsor Assignment** — assign human sponsors to agent identities
4. **Attended vs Unattended** — classify agent auth flow
5. **Access Packages** — use entitlement management for agent resource access
6. **Lifecycle Governance** — automated sponsor lifecycle via Lifecycle Workflows

## RBAC Role Reference

### Key Vault Data Plane Roles

| Role | ID | Use For |
|------|----|---------|
| Key Vault Administrator | `00482a5a-887f-4fb3-b363-3b7fe8e74483` | Full KV management |
| Key Vault Secrets User | `4633458b-17de-408a-b874-0445c86b69e6` | Read secrets (Container Apps) |
| Key Vault Secrets Officer | `b86a8fe4-44ce-4948-aee5-eccb2c155cd7` | Manage secrets (CI/CD) |
| Key Vault Certificates User | `db79e9a7-68ee-4b58-9aeb-b90e7c24fcba` | Read certs (Front Door) |
| Key Vault Crypto User | `12338af0-0e69-4776-bea7-57ae8d297424` | Use keys for crypto ops |

### InsightPulseAI App Roles (from app-roles-manifest.json)

| Role Value | Type | Mode |
|------------|------|------|
| `product.viewer` | User/App | ADVISORY |
| `product.operator` | User/App | ACTION |
| `finance.close.operator` | User/App | ACTION |
| `finance.close.approver` | User/App | ACTION |
| `finance.viewer` | User/App | ADVISORY |
| `marketing.manager` | User/App | ACTION |
| `marketing.viewer` | User/App | ADVISORY |
| `media.ops` | User/App | ACTION |
| `retail.operator` | User/App | ACTION |
| `analytics.viewer` | User/App | ADVISORY |
| `analytics.admin` | User/App | ACTION |
| `copilot.advisory` | User/App | ADVISORY |
| `copilot.action` | User/App | ACTION |
| `ops.admin` | User/App | ACTION |
| `ops.viewer` | User/App | ADVISORY |

## Secrets Inventory (Key Vault)

### Required Secrets per Environment

| Secret Name | Source | Consumer |
|-------------|--------|----------|
| `zoho-smtp-user` | Zoho | Odoo mail server |
| `zoho-smtp-password` | Zoho | Odoo mail server |
| `pg-admin-password` | Generated | PostgreSQL connection |
| `odoo-admin-password` | Generated | Odoo admin user |
| `supabase-service-role-key` | Supabase | n8n/integrations |
| `supabase-anon-key` | Supabase | Public client access |
| `slack-bot-token` | Slack | Slack agent |
| `slack-signing-secret` | Slack | Webhook verification |
| `anthropic-api-key` | Anthropic | AI copilot |
| `openai-api-key` | OpenAI | AI features |
| `github-token` | GitHub | CI/CD |
| `acr-password` | ACR | Container image pull |
| `front-door-secret` | Generated | Origin verification |

## Bicep Patterns

### Key Vault with MI Access

```bicep
// Deploy Key Vault
module keyVault 'modules/keyvault.bicep' = {
  name: 'kvDeployment'
  params: {
    keyVaultName: '${resourcePrefix}-kv'
    location: location
    tags: tags
  }
}

// Grant managed identity access
resource kvSecretsUserRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(keyVault.outputs.keyVaultName, managedIdentity.id, 'KeyVaultSecretsUser')
  scope: keyVault
  properties: {
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      '4633458b-17de-408a-b874-0445c86b69e6' // Key Vault Secrets User
    )
    principalId: managedIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}
```

### Container App with Key Vault Reference

```bicep
secrets: [
  {
    name: 'db-password'
    keyVaultUrl: '${keyVaultUri}secrets/pg-admin-password'
    identity: managedIdentity.id
  }
]
```

## Reference Docs

- `infra/azure/modules/keyvault.bicep` — Key Vault Bicep module
- `infra/azure/odoo-runtime.bicep` — Odoo runtime with KV + MI
- `infra/entra/app-roles-manifest.json` — App role definitions
- `infra/entra/role-tool-mapping.yaml` — Role-to-tool RBAC map
- `.claude/rules/security-baseline.md` — Secrets policy
- `.claude/commands/entra-manage.md` — Entra tenant management command
- `docs/architecture/ROADMAP_TARGET_STATE.md` — Target state architecture
