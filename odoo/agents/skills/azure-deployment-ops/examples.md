# Examples — azure-deployment-ops

## Example 1: New Container App for CRM service

**Input**: PR adds `ipai-crm-dev` Container App to `rg-ipai-dev`

**Output**:
- Resource: `ipai-crm-dev` (Microsoft.App/containerApps)
- Resource group: `rg-ipai-dev` — PASS
- Managed identity: system-assigned enabled — PASS
- Key Vault binding: `kv-ipai-dev` via managed identity — PASS
- Front Door routing: origin `ipai-crm-dev.thankfulbush-191bdcb0.southeastasia.azurecontainerapps.io` added — PASS
- TLS: `crm.insightpulseai.com` certificate bound — PASS
- Health probe: `/health` returning 200 — PASS
- Blockers: none
- Evidence: Resource Graph query `resources | where name == 'ipai-crm-dev'`

## Example 2: Container App missing managed identity

**Input**: PR adds `ipai-docs-dev` Container App without managed identity configuration

**Output**:
- Resource: `ipai-docs-dev` (Microsoft.App/containerApps)
- Resource group: `rg-ipai-dev` — PASS
- Managed identity: NOT CONFIGURED — FAIL (BLOCKER)
- Key Vault binding: cannot validate without managed identity — FAIL (BLOCKER)
- Front Door routing: not yet configured — FAIL
- TLS: no custom domain — FAIL
- Blockers: [managed identity missing, Key Vault binding impossible, no Front Door route]
- Recommendation: Add `identity: { type: 'SystemAssigned' }` to Bicep/Terraform before merge

## Example 3: Connection string detected in environment variables

**Input**: Container App config uses `POSTGRES_CONNECTION_STRING` directly instead of Key Vault reference

**Output**:
- Resource: `ipai-odoo-dev-web` (Microsoft.App/containerApps)
- Key Vault binding: POLICY VIOLATION — connection string found in env vars
- Blocker: Secret `POSTGRES_CONNECTION_STRING` must be moved to Key Vault and referenced via `secretref`
- Evidence: `az containerapp show --name ipai-odoo-dev-web --resource-group rg-ipai-dev --query "properties.template.containers[0].env"`
