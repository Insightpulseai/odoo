#!/usr/bin/env bash
# =============================================================================
# bootstrap-azure.sh — First-time Azure setup for Odoo deployment
#
# Creates: resource group, service principal, OIDC federation
# Prints: GitHub secrets to configure
#
# Prerequisites:
#   - az cli logged in (az login)
#   - gh cli authenticated (gh auth login)
#   - jq installed
#
# Usage: bash scripts/azure/bootstrap-azure.sh [dev|staging|prod]
# =============================================================================
set -euo pipefail

ENV="${1:-dev}"
RG="rg-ipai-${ENV}"
LOCATION="southeastasia"
GITHUB_REPO="Insightpulseai/odoo"

echo "=== Azure Bootstrap for environment: ${ENV} ==="
echo ""

# Verify prerequisites
command -v az >/dev/null 2>&1 || { echo "ERROR: az cli not found"; exit 1; }
command -v jq >/dev/null 2>&1 || { echo "ERROR: jq not found"; exit 1; }

SUBSCRIPTION_ID=$(az account show --query id -o tsv)
echo "Subscription: ${SUBSCRIPTION_ID}"
echo "Resource Group: ${RG}"
echo "Location: ${LOCATION}"
echo ""

# 1. Create resource group
echo "--- Step 1: Create resource group ---"
az group create \
  --name "$RG" \
  --location "$LOCATION" \
  --tags Environment="$ENV" Project="IPAI" ManagedBy="Bicep" \
  --output none
echo "Resource group ${RG} created"

# 2. Create service principal
echo ""
echo "--- Step 2: Create service principal ---"
SP_NAME="ipai-github-${ENV}"
SP=$(az ad sp create-for-rbac \
  --name "$SP_NAME" \
  --role contributor \
  --scopes "/subscriptions/${SUBSCRIPTION_ID}/resourceGroups/${RG}" \
  --query '{clientId:appId, tenantId:tenant}' -o json)

CLIENT_ID=$(echo "$SP" | jq -r .clientId)
TENANT_ID=$(echo "$SP" | jq -r .tenantId)
echo "Service principal ${SP_NAME} created (clientId: ${CLIENT_ID})"

# 3. Configure OIDC federation for GitHub Actions
echo ""
echo "--- Step 3: Configure OIDC federation ---"
APP_OBJ_ID=$(az ad app show --id "$CLIENT_ID" --query id -o tsv)

az ad app federated-credential create \
  --id "$APP_OBJ_ID" \
  --parameters "{
    \"name\": \"github-oidc-${ENV}\",
    \"issuer\": \"https://token.actions.githubusercontent.com\",
    \"subject\": \"repo:${GITHUB_REPO}:environment:${ENV}\",
    \"audiences\": [\"api://AzureADTokenExchange\"]
  }" \
  --output none
echo "OIDC federation configured for repo:${GITHUB_REPO}:environment:${ENV}"

# 4. Print secrets to set
echo ""
echo "=== GitHub Secrets to Configure ==="
echo ""
echo "Run these commands (or set via GitHub UI):"
echo ""
echo "  gh secret set AZURE_CLIENT_ID -b '${CLIENT_ID}' --env ${ENV} -R ${GITHUB_REPO}"
echo "  gh secret set AZURE_TENANT_ID -b '${TENANT_ID}' --env ${ENV} -R ${GITHUB_REPO}"
echo "  gh secret set AZURE_SUBSCRIPTION_ID -b '${SUBSCRIPTION_ID}' --env ${ENV} -R ${GITHUB_REPO}"
echo "  gh secret set ACR_NAME -b 'ipaiodoo${ENV}acr' --env ${ENV} -R ${GITHUB_REPO}"
echo "  gh secret set CONTAINERAPP_NAME -b 'ipai-odoo-${ENV}-app' --env ${ENV} -R ${GITHUB_REPO}"
echo "  gh secret set PG_ADMIN_PASSWORD -b '<your-secure-password>' --env ${ENV} -R ${GITHUB_REPO}"
echo ""
echo "=== Next Steps ==="
echo ""
echo "1. Set the GitHub secrets above"
echo "2. Run: gh workflow run azure-provision -f environment=${ENV} -R ${GITHUB_REPO}"
echo "3. After provision completes: gh workflow run odoo-azure-deploy -f environment=${ENV} -R ${GITHUB_REPO}"
