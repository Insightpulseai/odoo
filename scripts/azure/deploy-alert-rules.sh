#!/usr/bin/env bash
# deploy-alert-rules.sh — Deploy Azure Monitor alert rules for Odoo platform
# Issue: Insightpulseai/odoo#642
# Usage: ./scripts/azure/deploy-alert-rules.sh [--dry-run]

set -euo pipefail

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SUBSCRIPTION="$(az account show --query id -o tsv)"
RUNTIME_RG="rg-ipai-dev-odoo-runtime"
DATA_RG="rg-ipai-dev-odoo-data"
LOCATION="southeastasia"
TEMPLATE_FILE="$(cd "$(dirname "$0")/../../infra/azure/monitoring" && pwd)/alert-rules.bicep"

# Container App names
ACA_ODOO_WEB="ipai-odoo-dev-web"
ACA_ODOO_WORKER="ipai-odoo-dev-worker"
ACA_ODOO_CRON="ipai-odoo-dev-cron"
ACA_COPILOT_GW="ipai-copilot-gateway"

# PostgreSQL
PG_SERVER="pg-ipai-odoo"

# ---------------------------------------------------------------------------
# Pre-flight
# ---------------------------------------------------------------------------

if [[ ! -f "$TEMPLATE_FILE" ]]; then
  echo "ERROR: Bicep template not found at $TEMPLATE_FILE"
  exit 1
fi

echo "=== Azure Monitor Alert Rules Deployment ==="
echo "Subscription: $SUBSCRIPTION"
echo "Runtime RG:   $RUNTIME_RG"
echo "Data RG:      $DATA_RG"
echo "Template:     $TEMPLATE_FILE"
echo ""

# ---------------------------------------------------------------------------
# Resolve resource IDs
# ---------------------------------------------------------------------------

echo "Resolving resource IDs..."

resolve_aca_id() {
  local name="$1"
  local rg="$2"
  az containerapp show --name "$name" --resource-group "$rg" --query id -o tsv 2>/dev/null || {
    echo "ERROR: Container App '$name' not found in '$rg'" >&2
    exit 1
  }
}

ODOO_WEB_ID="$(resolve_aca_id "$ACA_ODOO_WEB" "$RUNTIME_RG")"
ODOO_WORKER_ID="$(resolve_aca_id "$ACA_ODOO_WORKER" "$RUNTIME_RG")"
ODOO_CRON_ID="$(resolve_aca_id "$ACA_ODOO_CRON" "$RUNTIME_RG")"
COPILOT_GW_ID="$(resolve_aca_id "$ACA_COPILOT_GW" "$RUNTIME_RG")"

PG_ID="$(az postgres flexible-server show --name "$PG_SERVER" --resource-group "$DATA_RG" --query id -o tsv 2>/dev/null)" || {
  echo "ERROR: PostgreSQL server '$PG_SERVER' not found in '$DATA_RG'"
  exit 1
}

APPI_ID="$(az monitor app-insights component show --app appi-ipai-dev --resource-group "$RUNTIME_RG" --query id -o tsv 2>/dev/null)" || {
  echo "WARNING: Application Insights 'appi-ipai-dev' not found in '$RUNTIME_RG'. Agent alerts (6-8) will be skipped."
  APPI_ID=""
}

echo "  odoo-web:        $ODOO_WEB_ID"
echo "  odoo-worker:     $ODOO_WORKER_ID"
echo "  odoo-cron:       $ODOO_CRON_ID"
echo "  copilot-gateway: $COPILOT_GW_ID"
echo "  postgres:        $PG_ID"
echo "  app-insights:    ${APPI_ID:-<not found>}"
echo ""

# ---------------------------------------------------------------------------
# Dry-run check
# ---------------------------------------------------------------------------

if [[ "${1:-}" == "--dry-run" ]]; then
  echo "=== DRY RUN — validating template ==="
  az deployment group validate \
    --resource-group "$RUNTIME_RG" \
    --template-file "$TEMPLATE_FILE" \
    --parameters \
      odooWebResourceId="$ODOO_WEB_ID" \
      odooWorkerResourceId="$ODOO_WORKER_ID" \
      odooCronResourceId="$ODOO_CRON_ID" \
      copilotGatewayResourceId="$COPILOT_GW_ID" \
      postgresResourceId="$PG_ID" \
      appInsightsResourceId="$APPI_ID" \
    --query 'properties.provisioningState' -o tsv
  echo "Validation complete."
  exit 0
fi

# ---------------------------------------------------------------------------
# Deploy
# ---------------------------------------------------------------------------

echo "=== Deploying alert rules to $RUNTIME_RG ==="

DEPLOYMENT_NAME="alert-rules-$(date +%Y%m%d-%H%M%S)"

az deployment group create \
  --name "$DEPLOYMENT_NAME" \
  --resource-group "$RUNTIME_RG" \
  --template-file "$TEMPLATE_FILE" \
  --parameters \
    odooWebResourceId="$ODOO_WEB_ID" \
    odooWorkerResourceId="$ODOO_WORKER_ID" \
    odooCronResourceId="$ODOO_CRON_ID" \
    copilotGatewayResourceId="$COPILOT_GW_ID" \
    postgresResourceId="$PG_ID" \
    appInsightsResourceId="$APPI_ID" \
  --query 'properties.provisioningState' -o tsv

echo ""
echo "=== Deployment complete ==="

# Verify alerts were created
echo ""
echo "=== Verifying alert rules ==="
az monitor metrics alert list \
  --resource-group "$RUNTIME_RG" \
  --query '[].{name:name, severity:severity, enabled:enabled}' \
  -o table

echo ""
echo "=== Scheduled query rules (agent alerts) ==="
az monitor scheduled-query list \
  --resource-group "$RUNTIME_RG" \
  --query '[].{name:name, severity:severity, enabled:enabled}' \
  -o table 2>/dev/null || echo "(no scheduled query rules found)"

echo ""
echo "=== Action groups ==="
az monitor action-group list \
  --resource-group "$RUNTIME_RG" \
  --query '[].{name:name, shortName:groupShortName, enabled:enabled}' \
  -o table
