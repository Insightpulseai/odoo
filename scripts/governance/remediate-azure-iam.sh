#!/bin/bash

# =============================================================================
# Pulser for Odoo — Azure IAM Remediation Script
# =============================================================================
# Purpose: Remediate PULSER-IAM-GATE-01 (Least-Privilege findings)
# Ref: docs/governance/AZURE_IAM_REMEDIATION.md
# =============================================================================

set -e

# Target Variables (Please fill these or ensure they are in your environment)
# export PLATFORM_ADMIN_ID="<OBJECT_ID_HERE>"
# export JAKE_TOLENTINO_ID="<OBJECT_ID_HERE>"
# export DEVOPS_SERVICE_ID="<SP_OBJECT_ID_HERE>"
# export SUBSCRIPTION_ID="<SUB_ID_HERE>"

echo "--- Azure IAM Remediation Start ---"

# 1. REMOVE P0 FINDINGS (IMMEDIATE)

echo "[P0] Removing root-scope User Access Administrator..."
if [ -n "$PLATFORM_ADMIN_ID" ]; then
  az role assignment delete \
    --assignee "$PLATFORM_ADMIN_ID" \
    --role "User Access Administrator" \
    --scope "/"
else
  echo "SKIP: PLATFORM_ADMIN_ID not set."
fi

echo "[P0] Removing orphaned Unknown principals holding Owner..."
# Add assignment IDs found in audit (Step 1 of remediation doc)
ORPHANED_IDS=(
  # "<ASSIGNMENT_ID_1>"
  # "<ASSIGNMENT_ID_2>"
)

for id in "${ORPHANED_IDS[@]}"; do
  echo "Deleting orphaned assignment: $id"
  az role assignment delete --ids "$id"
done

echo "[P0] Removing direct subscription Owner assignment for Jake Tolentino..."
if [ -n "$JAKE_TOLENTINO_ID" ] && [ -n "$SUBSCRIPTION_ID" ]; then
  az role assignment delete \
    --assignee "$JAKE_TOLENTINO_ID" \
    --role "Owner" \
    --scope "/subscriptions/$SUBSCRIPTION_ID"
else
  echo "SKIP: JAKE_TOLENTINO_ID or SUBSCRIPTION_ID not set."
fi

# 2. FIX P1 FINDINGS (PRODUCTION PROMOTION GATES)

echo "[P1] Scaling down DevOps Service from subscription Owner to RG Contributor..."
if [ -n "$DEVOPS_SERVICE_ID" ] && [ -n "$SUBSCRIPTION_ID" ]; then
  # Remove broad Owner
  az role assignment delete --assignee "$DEVOPS_SERVICE_ID" --role "Owner" --scope "/subscriptions/$SUBSCRIPTION_ID" || true
  
  # Assign narrow Contributor
  az role assignment create \
    --assignee "$DEVOPS_SERVICE_ID" \
    --role "Contributor" \
    --scope "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/rg-ipai-deploy-prod"
else
  echo "SKIP: DEVOPS_SERVICE_ID or SUBSCRIPTION_ID not set."
fi

echo "[P1] Removing redundant Contributor for Platform Admin (Keep Owner)..."
if [ -n "$PLATFORM_ADMIN_ID" ] && [ -n "$SUBSCRIPTION_ID" ]; then
  az role assignment delete --assignee "$PLATFORM_ADMIN_ID" --role "Contributor" --scope "/subscriptions/$SUBSCRIPTION_ID" || true
else
  echo "SKIP: PLATFORM_ADMIN_ID or SUBSCRIPTION_ID not set."
fi

echo "[P1] Removing redundant Azure AI User for Jake Tolentino (Owner covers it)..."
if [ -n "$JAKE_TOLENTINO_ID" ] && [ -n "$SUBSCRIPTION_ID" ]; then
  az role assignment delete --assignee "$JAKE_TOLENTINO_ID" --role "Azure AI User" --scope "/subscriptions/$SUBSCRIPTION_ID" || true
else
  echo "SKIP: JAKE_TOLENTINO_ID or SUBSCRIPTION_ID not set."
fi

echo "--- Remediation Complete ---"
echo "Please run: az role assignment list --all --include-inherited --output table"
echo "to verify the clean state."
