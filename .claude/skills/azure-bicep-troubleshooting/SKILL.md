---
name: azure-bicep-troubleshooting
description: Common Bicep deployment errors and fixes for Azure-native IPAI infrastructure. Captured from production deployment rounds on sponsored sub eba824fb.
---

# Azure Bicep Troubleshooting — IPAI Patterns

## Known errors and fixes (from 2026-04-13 deployment)

| Error | Root cause | Fix |
|---|---|---|
| BCP236 | Semicolons in Bicep object literals | Use commas between properties, not semicolons |
| BCP165 | Cross-scope KV secret writes from child modules | Remove inline KV writes, expose values as `output`, write secrets from parent module or `post-deploy.sh` |
| ACR SKU | Sponsorship sub doesn't support Basic or Premium | `Standard` for dev (sponsored sub), `Premium` for prod (geo-replication requires it) |
| Zone redundancy | ACA `zoneRedundant: true` requires VNet injection | Set `zoneRedundant: false` when no `InfrastructureSubnetId` provided |
| Foundry project API | Version `2024-10-01` too old + missing `allowProjectManagement` | Use `@2025-06-01` + set `allowProjectManagement: true` on parent AI Services account |
| PG collation | Wrong case in PostgreSQL collation string | `en_US.utf8` (lowercase), not `en_US.UTF-8` |
| Tag mismatch | Subscription tags derived from CLI don't match Bicep `var tags` | Tags must match `var tags` in `main.bicep` exactly — Bicep is the BOM |

## Tag alignment rule

Tags in the Azure portal/CLI must always be derived from the `var tags` block in `main.bicep`. Never set tags via CLI that aren't in the Bicep BOM.

```bicep
// main.bicep — canonical tag source
var tags = {
  product:         'pulser'
  environment:     env
  owner:           'jake@insightpulseai.com'
  repo:            'github.com/InsightPulseAI/odoo'
  costCenter:      'ipai-platform'
  'azd-env-name':  'ipai-${env}'
}
```

## ACR SKU rule

```bicep
sku: { name: env == 'prd' ? 'Premium' : 'Standard' }
```

- `Standard` on sponsored sub (`eba824fb`) — dev workloads
- `Premium` on prod sub — geo-replication to EUS2 requires it
- `Basic` is never used (not supported on sponsorship offer type)

## Cross-scope KV secret pattern

Wrong (BCP165):
```bicep
// Inside a child module
resource kv 'Microsoft.KeyVault/vaults@...' existing = {
  name: kvName
  scope: resourceGroup(kvRgName)  // ← different scope = BCP165
}
resource secret 'Microsoft.KeyVault/vaults/secrets@...' = {
  parent: kv
  name: 'my-secret'
  properties: { value: someValue }
}
```

Right:
```bicep
// Child module: expose as output
output myValue string = someValue

// Parent module or post-deploy.sh: write secret at correct scope
az keyvault secret set --vault-name kv-ipai-dev-sea --name my-secret --value $VALUE
```

## Foundry project pattern

```bicep
resource foundry 'Microsoft.CognitiveServices/accounts@2025-06-01' = {
  name: 'aif-ipai-${env}'
  kind: 'AIServices'
  properties: {
    allowProjectManagement: true  // ← required for child projects
    disableLocalAuth: true
  }
}

resource project 'Microsoft.CognitiveServices/accounts/projects@2025-06-01' = {
  parent: foundry
  name: 'proj-ipai-claude'
}
```

## PostgreSQL collation

```bicep
resource db 'Microsoft.DBforPostgreSQL/flexibleServers/databases@...' = {
  name: 'odoo'
  properties: {
    collation: 'en_US.utf8'   // ← lowercase, no hyphen
    charset: 'UTF8'
  }
}
```

## PgBouncer parameter

```bicep
{
  name: 'pgbouncer.enabled'
  value: 'True'    // ← capital T, string, not 'on'
}
```
