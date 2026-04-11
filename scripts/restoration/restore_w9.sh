#!/bin/bash
# =============================================================================
# scripts/restoration/restore_w9.sh
# Direct Origin Restoration for www.w9studio.net
# =============================================================================
set -euo pipefail

export RG_RUNTIME="rg-ipai-dev-odoo-runtime"
export ACA_ENV="ipai-odoo-dev-env-v2"
export APP="ipai-w9studio-dev"
export HOSTNAME="www.w9studio.net"
AZ_PATH="/opt/homebrew/bin/az"

echo "=== Restoring $HOSTNAME directly to $APP ==="

# 1. Discover FQDN and Verification ID
APP_FQDN=$($AZ_PATH containerapp show -g "$RG_RUNTIME" -n "$APP" --query properties.configuration.ingress.fqdn -o tsv)
VERIFY_ID=$($AZ_PATH containerapp show-custom-domain-verification-id -o tsv)

echo "APP FQDN: $APP_FQDN"
echo "VERIFY ID: $VERIFY_ID"

echo "---------------------------------------------------------------------------"
echo "ACTION REQUIRED: Create these DNS records at your authoritative provider for w9studio.net:"
echo "CNAME www       -> $APP_FQDN"
echo "TXT   asuid.www -> $VERIFY_ID"
echo "---------------------------------------------------------------------------"

# 2. Bind Hostname to ACA
echo "Attempting to bind $HOSTNAME to $APP (Verify DNS records are in place)..."
$AZ_PATH containerapp hostname add \
  -g "$RG_RUNTIME" -n "$APP" --hostname "$HOSTNAME" || true

$AZ_PATH containerapp hostname bind \
  -g "$RG_RUNTIME" -n "$APP" \
  --environment "$ACA_ENV" \
  --hostname "$HOSTNAME" \
  --validation-method CNAME || echo "WARNING: Binding failed. Ensure DNS CNAME/TXT records for w9studio.net are propagated."

echo "=== $HOSTNAME Restoration Attempt Complete ==="
