#!/usr/bin/env bash
# =============================================================================
# azure_estate_audit.sh — Deterministic Azure estate inventory
# =============================================================================
# Queries every resource in the subscription and produces a YAML inventory
# that can be diffed against ssot/azure/expected-estate.yaml.
#
# Output: .artifacts/azure-estate/estate-<timestamp>.yaml
#         .artifacts/azure-estate/drift-report.txt (if expected file exists)
#
# Requires: az CLI authenticated, jq
# =============================================================================
set -euo pipefail

TIMESTAMP=$(date -u +%Y%m%dT%H%M%SZ)
OUT_DIR=".artifacts/azure-estate"
ESTATE_FILE="${OUT_DIR}/estate-${TIMESTAMP}.yaml"
LATEST_LINK="${OUT_DIR}/estate-latest.yaml"
DRIFT_FILE="${OUT_DIR}/drift-report.txt"
EXPECTED="ssot/azure/expected-estate.yaml"

mkdir -p "${OUT_DIR}"

echo "# Azure Estate Audit — ${TIMESTAMP}" | tee "${ESTATE_FILE}"

# -------------------------------------------------------------------------
# 1. Subscription context
# -------------------------------------------------------------------------
SUB=$(az account show -o json 2>&1)
SUB_NAME=$(echo "$SUB" | jq -r '.name')
SUB_ID=$(echo "$SUB" | jq -r '.id')
TENANT_ID=$(echo "$SUB" | jq -r '.tenantId')

cat >> "${ESTATE_FILE}" <<EOF
subscription:
  name: "${SUB_NAME}"
  id: "${SUB_ID}"
  tenant: "${TENANT_ID}"
  queried_at: "${TIMESTAMP}"

EOF

# -------------------------------------------------------------------------
# 2. Resource groups
# -------------------------------------------------------------------------
echo "resource_groups:" >> "${ESTATE_FILE}"
az group list --query "[].{name:name, location:location}" -o json 2>/dev/null | \
  jq -r '.[] | "  - name: \"\(.name)\"\n    location: \"\(.location)\""' >> "${ESTATE_FILE}"
echo "" >> "${ESTATE_FILE}"

# -------------------------------------------------------------------------
# 3. All resources (per-RG to avoid RBAC blind spots)
# -------------------------------------------------------------------------
echo "resources:" >> "${ESTATE_FILE}"

RESOURCE_COUNT=0
for rg in $(az group list --query "[].name" -o tsv 2>/dev/null); do
  RESOURCES=$(az resource list -g "$rg" --query "[].{name:name, type:type, location:location}" -o json 2>/dev/null || echo "[]")
  COUNT=$(echo "$RESOURCES" | jq 'length')

  if [ "$COUNT" -gt 0 ]; then
    echo "$RESOURCES" | jq -r --arg rg "$rg" '.[] | "  - name: \"\(.name)\"\n    type: \"\(.type)\"\n    resource_group: \"\($rg)\"\n    location: \"\(.location)\""' >> "${ESTATE_FILE}"
  fi
  RESOURCE_COUNT=$((RESOURCE_COUNT + COUNT))
done

# -------------------------------------------------------------------------
# 4. Targeted queries for RBAC-filtered resource types
# -------------------------------------------------------------------------
echo "" >> "${ESTATE_FILE}"
echo "# Targeted queries (RBAC-resilient)" >> "${ESTATE_FILE}"

# PostgreSQL
echo "postgresql_servers:" >> "${ESTATE_FILE}"
for rg in $(az group list --query "[].name" -o tsv 2>/dev/null); do
  az postgres flexible-server list -g "$rg" --query "[].{name:name, state:state, version:version, sku:sku.name}" -o json 2>/dev/null | \
    jq -r --arg rg "$rg" '.[] | "  - name: \"\(.name)\"\n    resource_group: \"\($rg)\"\n    state: \"\(.state)\"\n    version: \"\(.version)\"\n    sku: \"\(.sku)\""' >> "${ESTATE_FILE}" 2>/dev/null || true
done
echo "" >> "${ESTATE_FILE}"

# Key Vaults
echo "key_vaults:" >> "${ESTATE_FILE}"
az keyvault list --query "[].{name:name, rg:resourceGroup, uri:properties.vaultUri}" -o json 2>/dev/null | \
  jq -r '.[] | "  - name: \"\(.name)\"\n    resource_group: \"\(.rg)\"\n    uri: \"\(.uri)\""' >> "${ESTATE_FILE}" 2>/dev/null || true
# Fallback: direct query known vaults
for kv in kv-ipai-dev kv-ipai-staging kv-ipai-prod ipai-odoo-dev-kv; do
  for rg in rg-ipai-dev-platform rg-ipai-dev-odoo-runtime rg-ipai-shared-staging rg-ipai-shared-prod; do
    RESULT=$(az keyvault show --name "$kv" --resource-group "$rg" --query "{name:name, uri:properties.vaultUri}" -o json 2>/dev/null || true)
    if [ -n "$RESULT" ] && [ "$RESULT" != "null" ]; then
      echo "$RESULT" | jq -r --arg rg "$rg" '"  - name: \"\(.name)\"\n    resource_group: \"\($rg)\"\n    uri: \"\(.uri)\""' >> "${ESTATE_FILE}"
    fi
  done
done
echo "" >> "${ESTATE_FILE}"

# Container Apps
echo "container_apps:" >> "${ESTATE_FILE}"
az containerapp list --query "[].{name:name, rg:resourceGroup, provisioningState:properties.provisioningState}" -o json 2>/dev/null | \
  jq -r '.[] | "  - name: \"\(.name)\"\n    resource_group: \"\(.rg)\"\n    state: \"\(.provisioningState)\""' >> "${ESTATE_FILE}" 2>/dev/null || true
echo "" >> "${ESTATE_FILE}"

# Container App Jobs
echo "container_app_jobs:" >> "${ESTATE_FILE}"
az containerapp job list --query "[].{name:name, rg:resourceGroup}" -o json 2>/dev/null | \
  jq -r '.[] | "  - name: \"\(.name)\"\n    resource_group: \"\(.rg)\""' >> "${ESTATE_FILE}" 2>/dev/null || true
echo "" >> "${ESTATE_FILE}"

# Container Registries
echo "container_registries:" >> "${ESTATE_FILE}"
az acr list --query "[].{name:name, rg:resourceGroup, loginServer:loginServer}" -o json 2>/dev/null | \
  jq -r '.[] | "  - name: \"\(.name)\"\n    resource_group: \"\(.rg)\"\n    login_server: \"\(.loginServer)\""' >> "${ESTATE_FILE}" 2>/dev/null || true
echo "" >> "${ESTATE_FILE}"

# Front Door
echo "front_doors:" >> "${ESTATE_FILE}"
az afd profile list --query "[].{name:name, rg:resourceGroup, sku:sku.name}" -o json 2>/dev/null | \
  jq -r '.[] | "  - name: \"\(.name)\"\n    resource_group: \"\(.rg)\"\n    sku: \"\(.sku)\""' >> "${ESTATE_FILE}" 2>/dev/null || true
echo "" >> "${ESTATE_FILE}"

# VNets
echo "virtual_networks:" >> "${ESTATE_FILE}"
az network vnet list --query "[].{name:name, rg:resourceGroup, addressSpace:addressSpace.addressPrefixes[0]}" -o json 2>/dev/null | \
  jq -r '.[] | "  - name: \"\(.name)\"\n    resource_group: \"\(.rg)\"\n    address_space: \"\(.addressSpace)\""' >> "${ESTATE_FILE}" 2>/dev/null || true
echo "" >> "${ESTATE_FILE}"

# DNS Zones
echo "dns_zones:" >> "${ESTATE_FILE}"
az network dns zone list --query "[].{name:name, rg:resourceGroup}" -o json 2>/dev/null | \
  jq -r '.[] | "  - name: \"\(.name)\"\n    resource_group: \"\(.rg)\""' >> "${ESTATE_FILE}" 2>/dev/null || true
echo "" >> "${ESTATE_FILE}"

# Private Endpoints
echo "private_endpoints:" >> "${ESTATE_FILE}"
az network private-endpoint list --query "[].{name:name, rg:resourceGroup}" -o json 2>/dev/null | \
  jq -r '.[] | "  - name: \"\(.name)\"\n    resource_group: \"\(.rg)\""' >> "${ESTATE_FILE}" 2>/dev/null || true
echo "" >> "${ESTATE_FILE}"

# Function Apps
echo "function_apps:" >> "${ESTATE_FILE}"
az functionapp list --query "[].{name:name, rg:resourceGroup, state:state}" -o json 2>/dev/null | \
  jq -r '.[] | "  - name: \"\(.name)\"\n    resource_group: \"\(.rg)\"\n    state: \"\(.state)\""' >> "${ESTATE_FILE}" 2>/dev/null || true
echo "" >> "${ESTATE_FILE}"

# Application Insights
echo "application_insights:" >> "${ESTATE_FILE}"
for rg in $(az group list --query "[].name" -o tsv 2>/dev/null); do
  az resource list -g "$rg" --resource-type "Microsoft.Insights/components" --query "[].{name:name}" -o json 2>/dev/null | \
    jq -r --arg rg "$rg" '.[] | "  - name: \"\(.name)\"\n    resource_group: \"\($rg)\""' >> "${ESTATE_FILE}" 2>/dev/null || true
done
echo "" >> "${ESTATE_FILE}"

# Log Analytics Workspaces
echo "log_analytics_workspaces:" >> "${ESTATE_FILE}"
az monitor log-analytics workspace list --query "[].{name:name, rg:resourceGroup}" -o json 2>/dev/null | \
  jq -r '.[] | "  - name: \"\(.name)\"\n    resource_group: \"\(.rg)\""' >> "${ESTATE_FILE}" 2>/dev/null || true
echo "" >> "${ESTATE_FILE}"

# Storage Accounts
echo "storage_accounts:" >> "${ESTATE_FILE}"
az storage account list --query "[].{name:name, rg:resourceGroup}" -o json 2>/dev/null | \
  jq -r '.[] | "  - name: \"\(.name)\"\n    resource_group: \"\(.rg)\""' >> "${ESTATE_FILE}" 2>/dev/null || true
echo "" >> "${ESTATE_FILE}"

# Private DNS Zones
echo "private_dns_zones:" >> "${ESTATE_FILE}"
az network private-dns zone list --query "[].{name:name, rg:resourceGroup}" -o json 2>/dev/null | \
  jq -r '.[] | "  - name: \"\(.name)\"\n    resource_group: \"\(.rg)\""' >> "${ESTATE_FILE}" 2>/dev/null || true
echo "" >> "${ESTATE_FILE}"

# Alert Rules
echo "alert_rules:" >> "${ESTATE_FILE}"
az monitor metrics alert list -g rg-ipai-dev-odoo-runtime --query "[].{name:name, enabled:enabled}" -o json 2>/dev/null | \
  jq -r '.[] | "  - name: \"\(.name)\"\n    enabled: \(.enabled)"' >> "${ESTATE_FILE}" 2>/dev/null || true
echo "" >> "${ESTATE_FILE}"

# WAF Policies
echo "waf_policies:" >> "${ESTATE_FILE}"
az network front-door waf-policy list -g rg-ipai-dev-odoo-runtime --query "[].{name:name}" -o json 2>/dev/null | \
  jq -r '.[] | "  - name: \"\(.name)\""' >> "${ESTATE_FILE}" 2>/dev/null || true
echo "" >> "${ESTATE_FILE}"

# -------------------------------------------------------------------------
# 5. Summary (count all named resources across targeted sections)
# -------------------------------------------------------------------------
TOTAL_NAMED=$(grep -c '  - name:' "${ESTATE_FILE}" 2>/dev/null || echo 0)
cat >> "${ESTATE_FILE}" <<EOF

summary:
  total_resources_generic_api: ${RESOURCE_COUNT}
  total_resources_targeted: ${TOTAL_NAMED}
  resource_groups: $(az group list --query "length(@)" -o tsv 2>/dev/null)
  container_apps: $(az containerapp list --query "length(@)" -o tsv 2>/dev/null)
  queried_at: "${TIMESTAMP}"
  queried_by: "azure_estate_audit.sh"
  note: "total_resources_generic_api is from az resource list (RBAC-filtered). total_resources_targeted is the real count from per-type queries."
EOF

# -------------------------------------------------------------------------
# 6. Create latest symlink
# -------------------------------------------------------------------------
ln -sf "estate-${TIMESTAMP}.yaml" "${LATEST_LINK}"

# -------------------------------------------------------------------------
# 7. Drift detection (if expected file exists)
# -------------------------------------------------------------------------
if [ -f "${EXPECTED}" ]; then
  echo "Drift detection against ${EXPECTED}:" | tee "${DRIFT_FILE}"

  # Extract resource names from both files and diff
  EXPECTED_NAMES=$(grep '  name:' "${EXPECTED}" 2>/dev/null | sed 's/.*name: *"\(.*\)"/\1/' | sort)
  ACTUAL_NAMES=$(grep '  - name:' "${ESTATE_FILE}" 2>/dev/null | sed 's/.*name: *"\(.*\)"/\1/' | sort -u)

  MISSING=$(comm -23 <(echo "$EXPECTED_NAMES") <(echo "$ACTUAL_NAMES"))
  UNEXPECTED=$(comm -13 <(echo "$EXPECTED_NAMES") <(echo "$ACTUAL_NAMES"))

  if [ -n "$MISSING" ]; then
    echo "" | tee -a "${DRIFT_FILE}"
    echo "MISSING (expected but not found):" | tee -a "${DRIFT_FILE}"
    echo "$MISSING" | sed 's/^/  - /' | tee -a "${DRIFT_FILE}"
  fi

  if [ -n "$UNEXPECTED" ]; then
    echo "" | tee -a "${DRIFT_FILE}"
    echo "UNEXPECTED (found but not in expected):" | tee -a "${DRIFT_FILE}"
    echo "$UNEXPECTED" | sed 's/^/  - /' | tee -a "${DRIFT_FILE}"
  fi

  if [ -z "$MISSING" ] && [ -z "$UNEXPECTED" ]; then
    echo "NO DRIFT — actual matches expected." | tee -a "${DRIFT_FILE}"
  fi
else
  echo "No expected estate file at ${EXPECTED}. Skipping drift detection." | tee "${DRIFT_FILE}"
  echo "To enable: copy ${LATEST_LINK} to ${EXPECTED} after manual review."
fi

# -------------------------------------------------------------------------
# 8. Final output
# -------------------------------------------------------------------------
echo ""
echo "============================================="
echo "Estate audit complete"
echo "  Inventory: ${ESTATE_FILE}"
echo "  Latest:    ${LATEST_LINK}"
echo "  Drift:     ${DRIFT_FILE}"
echo "  Resources: ${RESOURCE_COUNT}"
echo "============================================="
