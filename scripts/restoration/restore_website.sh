#!/bin/bash
# =============================================================================
# scripts/restoration/restore_website.sh
# Direct Origin Restoration for www.insightpulseai.com
# =============================================================================
set -euo pipefail

# Resource Identification
export ZONE="insightpulseai.com"
export HOSTNAME="www.insightpulseai.com"
# Path identification
AZ_PATH=$(which az || echo "/opt/homebrew/bin/az")

# Target Discovery (Deterministic Baseline)
# Website resides in the runtime/dev group per web-landing-deploy.yml
export RG_RUNTIME="rg-ipai-dev-odoo-runtime"
export APP="ipai-website-dev"
export RG_DNS="rg-ipai-dev-odoo-runtime"
export ACA_ENV="ipai-odoo-dev-env-v2"

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

echo "=== $HOSTNAME Restoration Complete ==="
