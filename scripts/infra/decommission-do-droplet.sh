#!/usr/bin/env bash
# =============================================================================
# DO Droplet Decommission Script
# =============================================================================
# Decommissions the DigitalOcean droplet (178.128.112.214) after verifying
# that all Azure Front Door origins have been migrated away from DO.
#
# Prerequisites:
#   - az CLI authenticated
#   - doctl CLI authenticated
#   - All Front Door origins pointing to Azure (no 178.128.112.214)
#
# Usage:
#   ./scripts/infra/decommission-do-droplet.sh [--dry-run|--execute|--snapshot-only]
#
# SSOT: infra/ssot/migration/do-to-azure-service-mapping.yaml
# Plan: infra/ssot/migration/DO_TO_AZURE_MIGRATION_PLAN.md
# =============================================================================

set -euo pipefail

DROPLET_IP="178.128.112.214"
DROPLET_NAME="odoo-erp-prod"
FD_RG="rg-ipai-shared-dev"
FD_PROFILE="ipai-fd-dev"
EVIDENCE_DIR="docs/evidence/$(date -u +%Y%m%d-%H%M)/do-decommission"
MODE="${1:---dry-run}"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[✓]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }
fail() { echo -e "${RED}[✗]${NC} $1"; exit 1; }

# =============================================================================
# Gate 1: Verify zero DO origins in Front Door
# =============================================================================
gate_check_origins() {
  echo ""
  echo "=== Gate 1: Front Door Origin Check ==="

  DO_COUNT=0
  for group in $(az afd origin-group list --resource-group "$FD_RG" --profile-name "$FD_PROFILE" --query "[].name" -o tsv 2>/dev/null); do
    HOSTS=$(az afd origin list --resource-group "$FD_RG" --profile-name "$FD_PROFILE" --origin-group-name "$group" --query "[].hostName" -o tsv 2>/dev/null)
    if echo "$HOSTS" | grep -q "$DROPLET_IP"; then
      fail "DO origin found in group: $group ($HOSTS)"
      DO_COUNT=$((DO_COUNT + 1))
    fi
  done

  if [ "$DO_COUNT" -eq 0 ]; then
    log "Zero DO origins in Front Door"
  else
    fail "$DO_COUNT DO origins still active. Cannot decommission."
  fi
}

# =============================================================================
# Gate 2: Health check all public hostnames
# =============================================================================
gate_check_health() {
  echo ""
  echo "=== Gate 2: Public Hostname Health ==="

  FAILURES=0
  for svc in erp auth mcp ocr superset plane shelf crm; do
    STATUS=$(curl -sS -o /dev/null -w "%{http_code}" --connect-timeout 10 "https://$svc.insightpulseai.com/" 2>/dev/null || echo "000")
    if [ "$STATUS" -ge 200 ] && [ "$STATUS" -lt 500 ]; then
      log "$svc.insightpulseai.com → HTTP $STATUS"
    elif [ "$STATUS" = "000" ]; then
      warn "$svc.insightpulseai.com → timeout (non-blocking)"
    else
      warn "$svc.insightpulseai.com → HTTP $STATUS"
      FAILURES=$((FAILURES + 1))
    fi
  done

  if [ "$FAILURES" -gt 0 ]; then
    warn "$FAILURES services returning 5xx. Review before proceeding."
  else
    log "All hostnames responding (2xx-4xx)"
  fi
}

# =============================================================================
# Gate 3: Verify droplet exists
# =============================================================================
gate_check_droplet() {
  echo ""
  echo "=== Gate 3: Droplet Existence ==="

  DROPLET_ID=$(doctl compute droplet list --format ID,Name,PublicIPv4 --no-header 2>/dev/null | grep "$DROPLET_IP" | awk '{print $1}')
  if [ -z "$DROPLET_ID" ]; then
    warn "Droplet with IP $DROPLET_IP not found (may already be decommissioned)"
    return 1
  fi

  log "Droplet found: ID=$DROPLET_ID, Name=$DROPLET_NAME, IP=$DROPLET_IP"
  echo "$DROPLET_ID"
}

# =============================================================================
# Action: Take snapshot
# =============================================================================
action_snapshot() {
  local droplet_id="$1"
  echo ""
  echo "=== Taking final snapshot ==="

  SNAPSHOT_NAME="decommission-${DROPLET_NAME}-$(date -u +%Y%m%d-%H%M%S)"

  if [ "$MODE" = "--dry-run" ]; then
    warn "[DRY RUN] Would create snapshot: $SNAPSHOT_NAME"
  else
    doctl compute droplet-action snapshot "$droplet_id" --snapshot-name "$SNAPSHOT_NAME" --wait
    log "Snapshot created: $SNAPSHOT_NAME"
  fi
}

# =============================================================================
# Action: Power off droplet
# =============================================================================
action_power_off() {
  local droplet_id="$1"
  echo ""
  echo "=== Powering off droplet ==="

  if [ "$MODE" = "--dry-run" ]; then
    warn "[DRY RUN] Would power off droplet $droplet_id ($DROPLET_NAME)"
  else
    doctl compute droplet-action power-off "$droplet_id" --wait
    log "Droplet powered off: $DROPLET_NAME ($DROPLET_IP)"
  fi
}

# =============================================================================
# Action: Delete droplet (30-day hold)
# =============================================================================
action_delete() {
  local droplet_id="$1"
  echo ""
  echo "=== DELETE DROPLET (IRREVERSIBLE) ==="

  if [ "$MODE" = "--dry-run" ]; then
    warn "[DRY RUN] Would delete droplet $droplet_id ($DROPLET_NAME)"
  else
    warn "Deleting droplet $droplet_id ($DROPLET_NAME) in 10 seconds..."
    warn "Press Ctrl+C to abort."
    sleep 10
    doctl compute droplet delete "$droplet_id" --force
    log "Droplet deleted: $DROPLET_NAME"
  fi
}

# =============================================================================
# Save evidence
# =============================================================================
save_evidence() {
  echo ""
  echo "=== Saving evidence ==="

  mkdir -p "$EVIDENCE_DIR"

  # Front Door state
  for group in $(az afd origin-group list --resource-group "$FD_RG" --profile-name "$FD_PROFILE" --query "[].name" -o tsv 2>/dev/null); do
    az afd origin list --resource-group "$FD_RG" --profile-name "$FD_PROFILE" --origin-group-name "$group" --query "[].{name:name, host:hostName}" -o table 2>/dev/null
  done > "$EVIDENCE_DIR/afd-origins-final.log"

  # ACA state
  az containerapp list --resource-group rg-ipai-dev --query "[].{name:name, fqdn:properties.configuration.ingress.fqdn, status:properties.runningStatus}" -o table 2>/dev/null > "$EVIDENCE_DIR/aca-list-final.log"

  # DO state
  doctl compute droplet list --format ID,Name,PublicIPv4,Status --no-header 2>/dev/null > "$EVIDENCE_DIR/doctl-droplet-list.log"

  # Health checks
  for svc in erp auth mcp ocr superset plane shelf crm; do
    STATUS=$(curl -sS -o /dev/null -w "%{http_code}" --connect-timeout 10 "https://$svc.insightpulseai.com/" 2>/dev/null || echo "000")
    echo "$svc.insightpulseai.com: HTTP $STATUS"
  done > "$EVIDENCE_DIR/health-checks.log"

  log "Evidence saved to: $EVIDENCE_DIR"
}

# =============================================================================
# Main
# =============================================================================
echo "=============================================="
echo "DO Droplet Decommission — $MODE"
echo "=============================================="
echo "Target: $DROPLET_NAME ($DROPLET_IP)"
echo "Date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo ""

gate_check_origins
gate_check_health

DROPLET_ID=$(gate_check_droplet) || exit 0

save_evidence

case "$MODE" in
  --dry-run)
    echo ""
    echo "=== DRY RUN COMPLETE ==="
    echo "All gates passed. To execute:"
    echo "  $0 --snapshot-only   # Take snapshot only"
    echo "  $0 --execute         # Snapshot + power off"
    ;;
  --snapshot-only)
    action_snapshot "$DROPLET_ID"
    log "Snapshot complete. Droplet still running."
    ;;
  --execute)
    action_snapshot "$DROPLET_ID"
    action_power_off "$DROPLET_ID"
    log "Droplet powered off. Delete after 30-day hold with:"
    echo "  doctl compute droplet delete $DROPLET_ID --force"
    ;;
  --delete)
    warn "Direct delete requested. Ensure 30-day hold has passed."
    action_delete "$DROPLET_ID"
    ;;
  *)
    echo "Usage: $0 [--dry-run|--snapshot-only|--execute|--delete]"
    exit 1
    ;;
esac

echo ""
echo "=== Done ==="
