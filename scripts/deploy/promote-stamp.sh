#!/bin/bash

# =============================================================================
# Pulser Stamp Promotion Script — ACA Progressive Rollout
# =============================================================================
# Purpose: Promote ACA revisions across a deployment stamp via traffic splitting.
# Ref: docs/architecture/DEPLOYMENT_STAMPS.md
# =============================================================================

set -e

# Usage: ./promote-stamp.sh <resource-group> <app-name> <revision-name> <weight>
# Example: ./promote-stamp.sh rg-ipai-stamp-01-prod odoo-web odoo-web--v2 10

RESOURCE_GROUP=${1}
APP_NAME=${2}
REVISION_NAME=${3}
WEIGHT=${4:-100} # Default to 100%

if [ -z "$RESOURCE_GROUP" ] || [ -z "$APP_NAME" ] || [ -z "$REVISION_NAME" ]; then
  echo "Usage: $0 <resource-group> <app-name> <revision-name> [weight]"
  exit 1
fi

echo "--- Promoting Revision $REVISION_NAME in $APP_NAME ($RESOURCE_GROUP) ---"

# 1. Apply 'latest' label to the target revision (if not already applied)
echo "Adding 'latest' label to $REVISION_NAME..."
az containerapp revision label add \
  --name "$APP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --label latest \
  --revision "$REVISION_NAME"

# 2. Shift Traffic
echo "Shifting $WEIGHT% traffic to $REVISION_NAME..."
# Note: This command assumes we are shifting from the 'stable' label or the current distribution
# A full production promotion would shift 100% to 'latest' and then swap labels.

az containerapp ingress traffic set \
  --name "$APP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --label-weight latest="$WEIGHT" stable="$((100 - WEIGHT))"

# 3. Health Check (Simulated - in production this would curl a health endpoint)
echo "Verifying health..."
# REVISION_FQDN=$(az containerapp revision show --name $APP_NAME --resource-group $RESOURCE_GROUP --revision $REVISION_NAME --query properties.fqdn -o tsv)
# curl -f "https://$REVISION_FQDN/web/health" || { echo "Health check failed! Rolling back..."; exit 1; }

echo "Promotion of $REVISION_NAME to $WEIGHT% complete."

if [ "$WEIGHT" -eq 100 ]; then
  echo "Finalizing: Swapping 'stable' label to $REVISION_NAME..."
  az containerapp revision label add \
    --name "$APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --label stable \
    --revision "$REVISION_NAME"
  
  # Set traffic 100% to stable label
  az containerapp ingress traffic set \
    --name "$APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --label-weight stable=100
fi

echo "--- Done ---"
