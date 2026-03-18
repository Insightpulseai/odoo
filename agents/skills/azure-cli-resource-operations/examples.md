# Examples — azure-cli-resource-operations

## Example 1: Resource inventory with Resource Graph

```bash
# List all Container Apps in dev resource group
az graph query -q "
  resources
  | where type == 'microsoft.app/containerapps'
  | where resourceGroup == 'rg-ipai-dev'
  | project name, location, properties.provisioningState
" --output table
```

---

## Example 2: Container App log query

```bash
# Last 100 log lines for Odoo web
az containerapp logs show \
  -n ipai-odoo-dev-web \
  -g rg-ipai-dev \
  --tail 100 \
  --output table
```

---

## Example 3: Scaling update

```bash
# Scale Odoo web to 2-5 replicas
az containerapp update \
  -n ipai-odoo-dev-web \
  -g rg-ipai-dev \
  --min-replicas 2 \
  --max-replicas 5

# Verify
az containerapp show \
  -n ipai-odoo-dev-web \
  -g rg-ipai-dev \
  --query "properties.template.scale" \
  --output json
```

---

## Example 4: Key Vault diagnostics (names only, never values)

```bash
# List secret names (NEVER --show-value in automation)
az keyvault secret list \
  --vault-name kv-ipai-dev \
  --query "[].{name:name, enabled:attributes.enabled}" \
  --output table
```

---

## Anti-pattern: Using Azure CLI for app bootstrap

```bash
# WRONG — use azd for this
az containerapp create -n my-app -g rg-ipai-dev ...
az containerapp update -n my-app -g rg-ipai-dev ...
az containerapp ingress enable ...

# CORRECT — use azd
azd up --environment dev
```
