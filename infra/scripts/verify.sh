#!/usr/bin/env bash
# infra/scripts/verify.sh
# Verifies all production resources match the Bicep spec (§9 BOM)
# Usage: ./infra/scripts/verify.sh [--fix]
# Outputs: PASS / FAIL per resource + summary
set -euo pipefail

PREFIX="ipai"
ENV="prd"
FIX="${1:-}"

PASS=0; FAIL=0
pass() { echo "  ✅ $1"; ((PASS++)); }
fail() { echo "  ❌ $1"; ((FAIL++)); }
header() { echo ""; echo "── $1 ──"; }

check_rg() {
  local rg="$1"
  az group show --name "$rg" &>/dev/null && pass "RG: $rg" || fail "RG: $rg — MISSING"
}
check_resource() {
  local rg="$1" type="$2" name="$3" query="${4:-}"
  local result
  result=$(az resource show --resource-group "$rg" \
    --resource-type "$type" --name "$name" \
    --query "${query:-id}" -o tsv 2>/dev/null || echo "")
  [[ -n "$result" ]] && pass "${type##*/}: $name" || fail "${type##*/}: $name — MISSING"
}
check_param() {
  local rg="$1" server="$2" param="$3" expected="$4"
  local actual
  actual=$(az postgres flexible-server parameter show \
    --resource-group "$rg" --server-name "$server" \
    --name "$param" --query value -o tsv 2>/dev/null || echo "")
  if [[ "$actual" == "$expected" ]]; then
    pass "PG param ${param}=${actual}"
  else
    fail "PG param ${param}: expected=${expected}, actual=${actual}"
    if [[ "$FIX" == "--fix" ]]; then
      az postgres flexible-server parameter set \
        --resource-group "$rg" --server-name "$server" \
        --name "$param" --value "$expected" && echo "    → Fixed"
    fi
  fi
}

echo "═══════════════════════════════════════════════════════════"
echo " IPAI Pulser Production — Resource Verification"
echo " Subscription: $(az account show --query id -o tsv)"
echo "═══════════════════════════════════════════════════════════"

header "Resource Groups (§9 §10)"
check_rg "rg-${PREFIX}-${ENV}-odoo-sea"
check_rg "rg-${PREFIX}-${ENV}-data-sea"
check_rg "rg-${PREFIX}-${ENV}-security-sea"
check_rg "rg-${PREFIX}-${ENV}-net-sea"
check_rg "rg-${PREFIX}-${ENV}-ai-sea"
check_rg "rg-${PREFIX}-${ENV}-ai-eus2"
check_rg "rg-${PREFIX}-${ENV}-mon-sea"

header "Security"
check_resource "rg-${PREFIX}-${ENV}-security-sea" \
  "Microsoft.ManagedIdentity/userAssignedIdentities" "id-${PREFIX}-${ENV}"
check_resource "rg-${PREFIX}-${ENV}-security-sea" \
  "Microsoft.KeyVault/vaults" "kv-${PREFIX}-${ENV}-sea"

header "Monitoring"
check_resource "rg-${PREFIX}-${ENV}-mon-sea" \
  "Microsoft.OperationalInsights/workspaces" "log-${PREFIX}-${ENV}-sea"
check_resource "rg-${PREFIX}-${ENV}-mon-sea" \
  "Microsoft.Insights/components" "appi-${PREFIX}-${ENV}"

header "Data — PostgreSQL"
check_resource "rg-${PREFIX}-${ENV}-data-sea" \
  "Microsoft.DBforPostgreSQL/flexibleServers" "pg-${PREFIX}-odoo-${ENV}"

PG_NAME="pg-${PREFIX}-odoo-${ENV}"
RG_DATA="rg-${PREFIX}-${ENV}-data-sea"
check_param "$RG_DATA" "$PG_NAME" "wal_level"  "logical"
check_param "$RG_DATA" "$PG_NAME" "pgbouncer.enabled" "on"

# Check all 3 databases exist
for db in odoo odoo_staging odoo_dev; do
  az postgres flexible-server db show \
    --resource-group "$RG_DATA" \
    --server-name "$PG_NAME" \
    --database-name "$db" &>/dev/null && \
    pass "PG DB: $db" || fail "PG DB: $db — MISSING"
done

header "Data — Storage"
check_resource "rg-${PREFIX}-${ENV}-data-sea" \
  "Microsoft.Storage/storageAccounts" "st${PREFIX}${ENV}"
check_resource "rg-${PREFIX}-${ENV}-data-sea" \
  "Microsoft.Storage/storageAccounts" "stlk${PREFIX}${ENV}"

header "Data — Service Bus"
check_resource "rg-${PREFIX}-${ENV}-odoo-sea" \
  "Microsoft.ServiceBus/namespaces" "sb-${PREFIX}-${ENV}-sea"

header "AI Services"
check_resource "rg-${PREFIX}-${ENV}-ai-sea" \
  "Microsoft.Search/searchServices" "srch-${PREFIX}-${ENV}"
check_resource "rg-${PREFIX}-${ENV}-ai-sea" \
  "Microsoft.Databricks/workspaces" "dbw-${PREFIX}-${ENV}"
check_resource "rg-${PREFIX}-${ENV}-ai-eus2" \
  "Microsoft.CognitiveServices/accounts" "aif-${PREFIX}-${ENV}"

header "Containers"
check_resource "rg-${PREFIX}-${ENV}-odoo-sea" \
  "Microsoft.ContainerRegistry/registries" "acr${PREFIX}${ENV}"
check_resource "rg-${PREFIX}-${ENV}-odoo-sea" \
  "Microsoft.App/managedEnvironments" "acae-${PREFIX}-${ENV}-sea"

for app in "ca-${PREFIX}-odoo-web-${ENV}" "ca-${PREFIX}-odoo-cron-${ENV}" \
           "ca-${PREFIX}-odoo-worker-${ENV}" "ca-${PREFIX}-release-manager-${ENV}" \
           "ca-${PREFIX}-ade-mcp-${ENV}"; do
  check_resource "rg-${PREFIX}-${ENV}-odoo-sea" \
    "Microsoft.App/containerApps" "$app"
done
check_resource "rg-${PREFIX}-${ENV}-odoo-sea" \
  "Microsoft.App/jobs" "caj-${PREFIX}-build-agent-${ENV}"

header "Networking"
check_resource "rg-${PREFIX}-${ENV}-net-sea" \
  "Microsoft.Cdn/profiles" "afd-${PREFIX}-${ENV}"

header "Resource Locks (critical resources)"
for locked_resource in \
  "rg-${PREFIX}-${ENV}-security-sea/Microsoft.KeyVault/vaults/kv-${PREFIX}-${ENV}-sea" \
  "rg-${PREFIX}-${ENV}-data-sea/Microsoft.DBforPostgreSQL/flexibleServers/pg-${PREFIX}-odoo-${ENV}" \
  "rg-${PREFIX}-${ENV}-data-sea/Microsoft.Storage/storageAccounts/stlk${PREFIX}${ENV}" \
  "rg-${PREFIX}-${ENV}-odoo-sea/Microsoft.ContainerRegistry/registries/acr${PREFIX}${ENV}" \
  "rg-${PREFIX}-${ENV}-ai-sea/Microsoft.Search/searchServices/srch-${PREFIX}-${ENV}"; do
  rg=$(echo "$locked_resource" | cut -d/ -f1)
  resource_type=$(echo "$locked_resource" | cut -d/ -f2-3)
  resource_name=$(echo "$locked_resource" | cut -d/ -f4)
  lock_count=$(az lock list \
    --resource-group "$rg" \
    --resource-name "$resource_name" \
    --resource-type "$resource_type" \
    --query "length(@)" -o tsv 2>/dev/null || echo "0")
  [[ "$lock_count" -gt "0" ]] && \
    pass "Lock on: ${resource_name}" || fail "Lock MISSING on: ${resource_name}"
done

header "KV Secrets (bootstrap check)"
KV_NAME="kv-${PREFIX}-${ENV}-sea"
for secret in ade-vision-agent-api-key pg-odoo-fqdn foundry-endpoint \
              appi-connection-string; do
  az keyvault secret show --vault-name "$KV_NAME" --name "$secret" \
    --query "attributes.enabled" -o tsv 2>/dev/null | \
    grep -q "true" && \
    pass "KV secret: $secret" || fail "KV secret: $secret — MISSING or disabled"
done

# ── Summary ───────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════════════════════"
TOTAL=$((PASS + FAIL))
echo " Results: ${PASS}/${TOTAL} PASS  |  ${FAIL} FAIL"
if [[ "$FAIL" -eq 0 ]]; then
  echo " ✅ All resources verified — infrastructure matches Bicep spec"
else
  echo " ❌ ${FAIL} resource(s) missing — run: azd up --environment ipai-prd"
  echo "    or for targeted fix: az deployment sub create -f infra/main.bicep"
fi
echo "═══════════════════════════════════════════════════════════"
exit $FAIL
