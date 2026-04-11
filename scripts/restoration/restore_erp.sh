#!/bin/bash
# =============================================================================
# scripts/restoration/restore_erp.sh
# Direct Origin Restoration for erp.insightpulseai.com
# =============================================================================
set -euo pipefail

# Resource Identification
export ZONE="insightpulseai.com"
export HOSTNAME="erp.insightpulseai.com"
export LABEL="erp"
AZ_PATH="/opt/homebrew/bin/az"

# Target Discovery (Deterministic Baseline)
# Check for Prod target first (as per pipeline history)
export RG_RUNTIME="rg-ipai-shared-prod"
export APP="ipai-odoo-prod-web"

if ! $AZ_PATH containerapp show -g "$RG_RUNTIME" -n "$APP" --query name -o tsv >/dev/null 2>&1; then
    echo "NOTICE: Prod app not found in $RG_RUNTIME, falling back to Dev..."
    export RG_RUNTIME="rg-ipai-dev-odoo-runtime"
    export APP="ipai-odoo-dev-web"
fi

export RG_DNS="rg-ipai-dev-odoo-runtime" # DNS Zone stays in runtime/dev
export ACA_ENV="ipai-odoo-dev-env-v2"  # Update this if prod env is different

echo "=== Restoring $HOSTNAME directly to $APP (in $RG_RUNTIME) ==="

# 1. Discover FQDN and Verification ID
APP_FQDN=$($AZ_PATH containerapp show -g "$RG_RUNTIME" -n "$APP" --query properties.configuration.ingress.fqdn -o tsv)
VERIFY_ID=$($AZ_PATH containerapp show-custom-domain-verification-id -o tsv)

echo "APP FQDN: $APP_FQDN"
echo "VERIFY ID: $VERIFY_ID"

# 2. Update DNS Records (CNAME)
$AZ_PATH network dns record-set cname set-record \
  -g "$RG_DNS" -z "$ZONE" -n "$LABEL" -c "$APP_FQDN"

# 3. Update DNS Records (TXT for Verification)
$AZ_PATH network dns record-set txt show -g "$RG_DNS" -z "$ZONE" -n "asuid.$LABEL" >/dev/null 2>&1 || \
  $AZ_PATH network dns record-set txt create -g "$RG_DNS" -z "$ZONE" -n "asuid.$LABEL"

$AZ_PATH network dns record-set txt add-record \
  -g "$RG_DNS" -z "$ZONE" -n "asuid.$LABEL" -v "$VERIFY_ID" || true

# 4. Bind Hostname to ACA
echo "Binding $HOSTNAME to $APP..."
$AZ_PATH containerapp hostname add \
  -g "$RG_RUNTIME" -n "$APP" --hostname "$HOSTNAME" || true

$AZ_PATH containerapp hostname bind \
  -g "$RG_RUNTIME" -n "$APP" \
  --environment "$ACA_ENV" \
  --hostname "$HOSTNAME" \
  --validation-method CNAME

# 5. Fix Odoo Proxy Mode (Disable)
echo "Ensuring proxy_mode is False for direct binding..."
$AZ_PATH containerapp update -g "$RG_RUNTIME" -n "$APP" \
  --set-env-vars ODOO_PROXY_MODE=False

echo "=== $HOSTNAME Restoration Complete ==="
