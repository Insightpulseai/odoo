#!/usr/bin/env bash
# cleanup-fix-jobs.sh — Delete 7 stale one-off ACA jobs from rg-ipai-dev-odoo-runtime
#
# Closes Gap #3 from the 2026-04-12 inventory: incident-era debug/patch jobs that
# were never cleaned up. They count against ACA environment limits and clutter
# the job list.
#
# SAFETY: Dry-run by default. Set CLEANUP_APPLY=1 to actually delete.
#
# Usage:
#   ./cleanup-fix-jobs.sh              # dry-run
#   CLEANUP_APPLY=1 ./cleanup-fix-jobs.sh  # apply deletions

set -euo pipefail

RG="${CLEANUP_RG:-rg-ipai-dev-odoo-runtime}"
SUBSCRIPTION="${CLEANUP_SUB:-}"

JOBS=(
  asset-deep-fix
  asset-fix-job
  oauth-diag-job
  oauth-fix-job
  oauth-signup-fix
  oauth-verify-job
  url-fix-job
)

if [ -n "$SUBSCRIPTION" ]; then
  az account set --subscription "$SUBSCRIPTION"
fi

echo "=== ACA Fix-Jobs Cleanup ==="
echo "Resource group: $RG"
echo "Subscription: $(az account show --query 'name' -o tsv 2>/dev/null || echo 'default')"
echo ""

FOUND=0
MISSING=0
DELETED=0

for job in "${JOBS[@]}"; do
  if az containerapp job show --name "$job" --resource-group "$RG" -o none 2>/dev/null; then
    FOUND=$((FOUND + 1))
    EXEC_COUNT=$(az containerapp job execution list --name "$job" --resource-group "$RG" --query "length([])" -o tsv 2>/dev/null || echo "0")
    LAST_EXEC=$(az containerapp job execution list --name "$job" --resource-group "$RG" --query "[0].properties.startTime" -o tsv 2>/dev/null || echo "never")
    echo "  [FOUND] $job (executions: $EXEC_COUNT, last: $LAST_EXEC)"
    if [ "${CLEANUP_APPLY:-0}" = "1" ]; then
      echo "         deleting..."
      az containerapp job delete --name "$job" --resource-group "$RG" --yes
      DELETED=$((DELETED + 1))
    fi
  else
    MISSING=$((MISSING + 1))
    echo "  [gone ] $job (already removed)"
  fi
done

echo ""
echo "Summary: $FOUND present, $MISSING already removed, $DELETED deleted"
if [ "${CLEANUP_APPLY:-0}" != "1" ] && [ "$FOUND" -gt 0 ]; then
  echo ""
  echo "Re-run with CLEANUP_APPLY=1 to actually delete the $FOUND job(s) found."
fi
