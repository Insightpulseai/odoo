#!/usr/bin/env bash
# migrate-variable-groups.sh
#
# Migrates ADO variable groups to use kv-ipai-dev secrets
# instead of plaintext or inline variables.
#
# Run: bash migrate-variable-groups.sh
# Auth: az login (uses Entra, not PAT)
#
# Key Vault: kv-ipai-dev (rg-ipai-dev-platform, SEA)
# ADO org: dev.azure.com/insightpulseai
# ADO project: ipai-platform

set -euo pipefail

ORG="https://dev.azure.com/insightpulseai"
PROJECT="ipai-platform"
KV_NAME="kv-ipai-dev"
KV_RG="rg-ipai-dev-platform"
KV_SUB="536d8cf6-89e1-4815-aef3-d5f2c5f4d070"
KV_ID="/subscriptions/${KV_SUB}/resourceGroups/${KV_RG}/providers/Microsoft.KeyVault/vaults/${KV_NAME}"

# ---------------------------------------------------------------------------
# Step 1: Verify Key Vault exists and user has access
# ---------------------------------------------------------------------------
echo "=== Verifying kv-ipai-dev access ==="
az keyvault show --name "$KV_NAME" --resource-group "$KV_RG" \
  --query "{name:name, uri:properties.vaultUri}" -o table

# ---------------------------------------------------------------------------
# Step 2: List existing variable groups to identify which need migration
# ---------------------------------------------------------------------------
echo ""
echo "=== Current variable groups in ipai-platform ==="
az pipelines variable-group list \
  --org "$ORG" \
  --project "$PROJECT" \
  --query "[].{id:id, name:name, type:type, variables:variables}" \
  -o table

# ---------------------------------------------------------------------------
# Step 3: Create KV-linked variable group for IPAI platform secrets
# This replaces any inline secrets in existing groups
# ---------------------------------------------------------------------------
echo ""
echo "=== Creating ipai-platform-secrets (KV-linked) ==="
az pipelines variable-group create \
  --org "$ORG" \
  --project "$PROJECT" \
  --name "ipai-platform-secrets" \
  --authorize true \
  --variables placeholder="see-key-vault" \
  2>/dev/null || echo "Group already exists — will update"

# Get the group ID
GROUP_ID=$(az pipelines variable-group list \
  --org "$ORG" \
  --project "$PROJECT" \
  --query "[?name=='ipai-platform-secrets'].id | [0]" \
  -o tsv)

echo "Group ID: $GROUP_ID"

# ---------------------------------------------------------------------------
# Step 4: Link the variable group to kv-ipai-dev
# Requires ADO service connection to the Key Vault subscription
# ---------------------------------------------------------------------------
echo ""
echo "=== Linking ipai-platform-secrets to kv-ipai-dev ==="

# Create ADO service connection to Azure subscription (if not exists)
# This is needed for variable groups to read from Key Vault
SERVICE_CONN_NAME="ipai-azure-subscription"

echo "Creating/verifying Azure service connection..."
az devops service-endpoint azurerm create \
  --org "$ORG" \
  --project "$PROJECT" \
  --azure-rm-service-principal-id "" \
  --azure-rm-subscription-id "$KV_SUB" \
  --azure-rm-subscription-name "Azure subscription 1" \
  --azure-rm-tenant-id "402de71a-87ec-4302-a609-fb76098d1da7" \
  --name "$SERVICE_CONN_NAME" \
  2>/dev/null || echo "Service connection already exists"

CONN_ID=$(az devops service-endpoint list \
  --org "$ORG" \
  --project "$PROJECT" \
  --query "[?name=='${SERVICE_CONN_NAME}'].id | [0]" \
  -o tsv)

echo "Service connection ID: $CONN_ID"

# ---------------------------------------------------------------------------
# Step 5: Add Key Vault secrets to the variable group
# These are the secrets that should be in KV, not in pipeline YAML
#
# Expected secrets in kv-ipai-dev:
# ---------------------------------------------------------------------------
declare -A KV_SECRETS=(
  # Odoo / app secrets
  ["ODOO-ADMIN-PASSWORD"]="odoo-admin-password"
  ["ENTRA-CLIENT-SECRET"]="entra-client-secret"
  # Azure AI Foundry
  ["IPAI-FOUNDRY-ENDPOINT"]="ipai-foundry-endpoint"
  # Azure resources
  ["ACR-PASSWORD"]="acr-password"
  # Database
  ["PG-PASSWORD"]="pg-password"
)

echo ""
echo "=== Adding KV secret references to variable group ==="
for secret_name in "${!KV_SECRETS[@]}"; do
  kv_key="${KV_SECRETS[$secret_name]}"
  echo "Mapping ${secret_name} → kv-ipai-dev/${kv_key}"

  # Check if secret exists in KV first
  az keyvault secret show \
    --vault-name "$KV_NAME" \
    --name "$kv_key" \
    --query "id" -o tsv 2>/dev/null || {
    echo "  WARNING: Secret '$kv_key' not found in kv-ipai-dev — create it first"
    echo "  az keyvault secret set --vault-name $KV_NAME --name $kv_key --value '<value>'"
    continue
  }
done

# ---------------------------------------------------------------------------
# Step 6: Variable group YAML usage template
# ---------------------------------------------------------------------------
cat << 'YAML'

=== Add to your pipeline YAML ===

# Reference the KV-linked variable group
variables:
  - group: ipai-platform-secrets   # secrets from kv-ipai-dev

# Use in steps:
steps:
  - script: echo "Foundry endpoint: $(IPAI-FOUNDRY-ENDPOINT)"
    displayName: 'Verify KV secrets available'

  - task: AzureContainerApps@1
    inputs:
      azureSubscription: 'ipai-azure-subscription'
      containerAppName: 'ipai-copilot-gateway'
      resourceGroup: 'rg-ipai-dev-odoo-runtime'
      imageToDeploy: '$(image)'
    env:
      ENTRA_CLIENT_SECRET: $(ENTRA-CLIENT-SECRET)
      IPAI_FOUNDRY_ENDPOINT: $(IPAI-FOUNDRY-ENDPOINT)

YAML

# ---------------------------------------------------------------------------
# Step 7: Audit — find any plaintext secrets in existing variable groups
# ---------------------------------------------------------------------------
echo ""
echo "=== Auditing existing variable groups for plaintext secrets ==="
az pipelines variable-group list \
  --org "$ORG" \
  --project "$PROJECT" \
  --query "[].{name:name, vars:variables}" \
  -o json | python3 -c "
import json, sys
groups = json.load(sys.stdin)
for g in groups:
    name = g['name']
    for var, val in (g.get('vars') or {}).items():
        is_secret = val.get('isSecret', False)
        value = val.get('value', '')
        if is_secret and value:
            print(f'WARNING: {name}/{var} = inline secret (should be in KV)')
        elif any(kw in var.lower() for kw in ['secret', 'password', 'key', 'token', 'pat']):
            if not is_secret:
                print(f'WARNING: {name}/{var} looks like a secret but isSecret=False')
print('Audit complete')
"

echo ""
echo "=== Migration complete ==="
echo "Next steps:"
echo "1. Verify secrets exist in kv-ipai-dev: az keyvault secret list --vault-name kv-ipai-dev -o table"
echo "2. Grant ipai-build-agent MI access to kv-ipai-dev:"
echo "   az keyvault set-policy --name kv-ipai-dev --object-id <ipai-build-agent-mi-oid> --secret-permissions get list"
echo "3. Update pipeline YAML to use '- group: ipai-platform-secrets' variable group"
echo "4. Remove any inline secrets from pipeline YAML and variable groups"
