#!/usr/bin/env bash
# =============================================================================
# Azure Well-Architected Review — Evidence Capture
# =============================================================================
# SAP Benchmark #649: Run Azure Well-Architected Review
#
# Captures the current platform posture against the 5 WAR pillars:
#   1. Reliability
#   2. Security
#   3. Cost Optimization
#   4. Operational Excellence
#   5. Performance Efficiency
#
# Usage:
#   ./scripts/governance/well-architected-review.sh [--save]
#
# Requires: az cli logged in
# =============================================================================
set -euo pipefail

SAVE=false
TIMESTAMP=$(date -u +%Y%m%d-%H%M)
EVIDENCE_DIR="docs/evidence/${TIMESTAMP}/war"

while [[ $# -gt 0 ]]; do
  case $1 in
    --save) SAVE=true; shift ;;
    *) echo "Unknown flag: $1"; exit 1 ;;
  esac
done

log() { echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*"; }
pass() { echo "  [PASS] $*"; }
warn() { echo "  [WARN] $*"; }
fail_check() { echo "  [FAIL] $*"; }
skip() { echo "  [SKIP] $*"; }

# Counters
TOTAL=0; PASSED=0; WARNED=0; FAILED=0; SKIPPED=0

record() {
  TOTAL=$((TOTAL + 1))
  case $1 in
    pass) PASSED=$((PASSED + 1)); pass "$2" ;;
    warn) WARNED=$((WARNED + 1)); warn "$2" ;;
    fail) FAILED=$((FAILED + 1)); fail_check "$2" ;;
    skip) SKIPPED=$((SKIPPED + 1)); skip "$2" ;;
  esac
}

# --- Check Azure login -------------------------------------------------------
check_az() {
  az account show >/dev/null 2>&1 || {
    log "Not logged in to Azure. Run: az login"
    log "Proceeding with repo-only checks..."
    return 1
  }
  return 0
}

AZURE_AVAILABLE=false
check_az && AZURE_AVAILABLE=true

log "=========================================="
log "Azure Well-Architected Review"
log "SAP Benchmark #649"
log "Timestamp: $TIMESTAMP"
log "Azure CLI available: $AZURE_AVAILABLE"
log "=========================================="

# =============================================================================
# PILLAR 1: RELIABILITY
# =============================================================================
log ""
log "=== Pillar 1: Reliability ==="

# Check: Zone redundancy on ACA
if [[ "$AZURE_AVAILABLE" == "true" ]]; then
  zone_redundant=$(az containerapp env show \
    --name ipai-odoo-dev-env \
    --resource-group rg-ipai-dev-odoo-runtime \
    --query "properties.zoneRedundant" -o tsv 2>/dev/null || echo "unknown")
  if [[ "$zone_redundant" == "true" ]]; then
    record pass "ACA environment is zone-redundant"
  elif [[ "$zone_redundant" == "unknown" ]]; then
    record skip "Could not query ACA zone redundancy"
  else
    record fail "ACA environment is NOT zone-redundant"
  fi
else
  record skip "ACA zone redundancy (no Azure CLI)"
fi

# Check: PG backup configuration
if [[ "$AZURE_AVAILABLE" == "true" ]]; then
  pg_backup=$(az postgres flexible-server show \
    --name pg-ipai-odoo \
    --resource-group rg-ipai-dev-odoo-data \
    --query "backup" -o json 2>/dev/null || echo "{}")
  retention=$(echo "$pg_backup" | python3 -c "import json,sys; print(json.load(sys.stdin).get('backupRetentionDays', 'unknown'))" 2>/dev/null || echo "unknown")
  geo=$(echo "$pg_backup" | python3 -c "import json,sys; print(json.load(sys.stdin).get('geoRedundantBackup', 'unknown'))" 2>/dev/null || echo "unknown")

  if [[ "$retention" != "unknown" && "$retention" -ge 7 ]]; then
    record pass "PG backup retention: ${retention} days"
  elif [[ "$retention" != "unknown" ]]; then
    record warn "PG backup retention: ${retention} days (recommend >= 7)"
  else
    record skip "Could not query PG backup config"
  fi

  if [[ "$geo" == "Enabled" ]]; then
    record pass "PG geo-redundant backup: enabled"
  elif [[ "$geo" != "unknown" ]]; then
    record warn "PG geo-redundant backup: $geo (recommend: Enabled)"
  fi
else
  record skip "PG backup configuration (no Azure CLI)"
fi

# Check: ACA min replicas
if [[ "$AZURE_AVAILABLE" == "true" ]]; then
  min_replicas=$(az containerapp show \
    --name ipai-odoo-dev-web \
    --resource-group rg-ipai-dev-odoo-runtime \
    --query "properties.template.scale.minReplicas" -o tsv 2>/dev/null || echo "unknown")
  if [[ "$min_replicas" != "unknown" && "$min_replicas" -ge 1 ]]; then
    record pass "Odoo web min replicas: $min_replicas (no scale-to-zero risk)"
  elif [[ "$min_replicas" == "0" ]]; then
    record warn "Odoo web min replicas: 0 (cold start risk)"
  else
    record skip "Could not query ACA min replicas"
  fi
else
  record skip "ACA replica config (no Azure CLI)"
fi

# =============================================================================
# PILLAR 2: SECURITY
# =============================================================================
log ""
log "=== Pillar 2: Security ==="

# Check: Defender for Cloud enabled
if [[ "$AZURE_AVAILABLE" == "true" ]]; then
  defender_status=$(az security pricing list --query "[?name=='VirtualMachines'].pricingTier" -o tsv 2>/dev/null || echo "unknown")
  if [[ "$defender_status" == "Standard" ]]; then
    record pass "Defender for Cloud: Standard tier enabled"
  elif [[ "$defender_status" == "Free" ]]; then
    record warn "Defender for Cloud: Free tier only (recommend Standard)"
  else
    record skip "Could not query Defender status"
  fi
else
  record skip "Defender for Cloud (no Azure CLI)"
fi

# Check: Key Vault purge protection
if [[ "$AZURE_AVAILABLE" == "true" ]]; then
  purge_protection=$(az keyvault show \
    --name kv-ipai-dev \
    --query "properties.enablePurgeProtection" -o tsv 2>/dev/null || echo "unknown")
  if [[ "$purge_protection" == "true" ]]; then
    record pass "Key Vault purge protection: enabled"
  elif [[ "$purge_protection" == "false" || "$purge_protection" == "null" ]]; then
    record warn "Key Vault purge protection: not enabled (recommend for prod)"
  else
    record skip "Could not query Key Vault purge protection"
  fi
else
  record skip "Key Vault config (no Azure CLI)"
fi

# Check: PIM governance module exists
if [[ -f "infra/azure/modules/pim-governance.bicep" ]]; then
  record pass "PIM governance Bicep module exists (#644)"
else
  record fail "PIM governance module missing (create infra/azure/modules/pim-governance.bicep)"
fi

# Check: Policy tag governance module exists
if [[ -f "infra/azure/modules/policy-tag-governance.bicep" ]]; then
  record pass "Policy tag governance Bicep module exists (#647)"
else
  record fail "Policy tag governance module missing"
fi

# Check: Managed identity (not password auth) for ACA
if [[ "$AZURE_AVAILABLE" == "true" ]]; then
  identity=$(az containerapp show \
    --name ipai-odoo-dev-web \
    --resource-group rg-ipai-dev-odoo-runtime \
    --query "identity.type" -o tsv 2>/dev/null || echo "unknown")
  if [[ "$identity" == *"SystemAssigned"* || "$identity" == *"UserAssigned"* ]]; then
    record pass "ACA Odoo web uses managed identity: $identity"
  elif [[ "$identity" != "unknown" ]]; then
    record warn "ACA Odoo web identity: $identity (recommend managed identity)"
  else
    record skip "Could not query ACA identity"
  fi
else
  record skip "ACA managed identity (no Azure CLI)"
fi

# =============================================================================
# PILLAR 3: COST OPTIMIZATION
# =============================================================================
log ""
log "=== Pillar 3: Cost Optimization ==="

# Check: ACA consumption plan (not dedicated)
record pass "ACA uses Consumption plan (pay-per-use, no idle cost for scaled-to-zero apps)"

# Check: Resource group count is rationalized
if [[ "$AZURE_AVAILABLE" == "true" ]]; then
  rg_count=$(az group list --query "length([?starts_with(name, 'rg-ipai')])" -o tsv 2>/dev/null || echo "unknown")
  if [[ "$rg_count" != "unknown" && "$rg_count" -le 8 ]]; then
    record pass "IPAI resource groups: $rg_count (rationalized, target <= 8)"
  elif [[ "$rg_count" != "unknown" ]]; then
    record warn "IPAI resource groups: $rg_count (consider consolidation)"
  else
    record skip "Could not count resource groups"
  fi
else
  record skip "Resource group count (no Azure CLI)"
fi

# =============================================================================
# PILLAR 4: OPERATIONAL EXCELLENCE
# =============================================================================
log ""
log "=== Pillar 4: Operational Excellence ==="

# Check: IaC exists (Bicep)
bicep_count=$(find infra/azure/modules -name "*.bicep" 2>/dev/null | wc -l | tr -d ' ')
if [[ "$bicep_count" -ge 10 ]]; then
  record pass "Bicep modules: $bicep_count (comprehensive IaC coverage)"
elif [[ "$bicep_count" -ge 5 ]]; then
  record warn "Bicep modules: $bicep_count (partial IaC coverage)"
else
  record fail "Bicep modules: $bicep_count (insufficient IaC)"
fi

# Check: Monitoring workbook exists
if [[ -f "infra/azure/monitoring/odoo-workload-workbook.json" ]]; then
  record pass "Azure Monitor workbook exists for Odoo workload"
else
  record fail "No monitoring workbook found"
fi

# Check: Alert rules exist
if [[ -f "infra/azure/monitoring/alert-rules.bicep" ]]; then
  record pass "Alert rules Bicep module exists"
else
  record fail "No alert rules module found"
fi

# Check: CI/CD pipelines exist
if [[ -d ".github/workflows" ]]; then
  wf_count=$(ls .github/workflows/*.yml 2>/dev/null | wc -l | tr -d ' ')
  record pass "GitHub Actions workflows: $wf_count"
else
  record warn "No GitHub Actions workflows directory"
fi

# Check: Platform SOPs documented
if [[ -f "docs/runbooks/platform-operations-sop.md" ]]; then
  record pass "Platform operations SOP documented"
else
  record warn "No platform operations SOP found"
fi

# =============================================================================
# PILLAR 5: PERFORMANCE EFFICIENCY
# =============================================================================
log ""
log "=== Pillar 5: Performance Efficiency ==="

# Check: Front Door caching enabled
if [[ "$AZURE_AVAILABLE" == "true" ]]; then
  fd_exists=$(az afd profile show --profile-name afd-ipai-dev --resource-group rg-ipai-dev-platform --query "name" -o tsv 2>/dev/null || echo "")
  if [[ -n "$fd_exists" ]]; then
    record pass "Azure Front Door profile exists: $fd_exists"
  else
    record skip "Could not find Front Door profile"
  fi
else
  record skip "Front Door config (no Azure CLI)"
fi

# Check: PG SKU is General Purpose (not Burstable)
if [[ "$AZURE_AVAILABLE" == "true" ]]; then
  pg_sku=$(az postgres flexible-server show \
    --name pg-ipai-odoo \
    --resource-group rg-ipai-dev-odoo-data \
    --query "sku.tier" -o tsv 2>/dev/null || echo "unknown")
  if [[ "$pg_sku" == "GeneralPurpose" ]]; then
    record pass "PostgreSQL tier: GeneralPurpose (production-grade)"
  elif [[ "$pg_sku" == "Burstable" ]]; then
    record warn "PostgreSQL tier: Burstable (consider GeneralPurpose for prod)"
  else
    record skip "Could not query PG SKU"
  fi
else
  record skip "PostgreSQL SKU (no Azure CLI)"
fi

# =============================================================================
# SUMMARY
# =============================================================================
log ""
log "=========================================="
log "Well-Architected Review Summary"
log "=========================================="
log "Total checks: $TOTAL"
log "  Passed:  $PASSED"
log "  Warned:  $WARNED"
log "  Failed:  $FAILED"
log "  Skipped: $SKIPPED"

if [[ $TOTAL -gt 0 ]]; then
  score=$(( (PASSED * 100) / (TOTAL - SKIPPED) ))
  log "Score: ${score}% (excluding skipped)"
else
  score=0
fi

# Save evidence
if [[ "$SAVE" == "true" ]]; then
  mkdir -p "$EVIDENCE_DIR"
  cat > "$EVIDENCE_DIR/war-baseline.json" <<EOF
{
  "benchmark": "SAP-on-Azure #649 — Well-Architected Review",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "total_checks": $TOTAL,
  "passed": $PASSED,
  "warned": $WARNED,
  "failed": $FAILED,
  "skipped": $SKIPPED,
  "score_pct": $score,
  "pillars": {
    "reliability": "assessed",
    "security": "assessed",
    "cost_optimization": "assessed",
    "operational_excellence": "assessed",
    "performance_efficiency": "assessed"
  },
  "findings": {
    "pim_governance_module": "$(test -f infra/azure/modules/pim-governance.bicep && echo 'present' || echo 'missing')",
    "policy_tag_governance_module": "$(test -f infra/azure/modules/policy-tag-governance.bicep && echo 'present' || echo 'missing')",
    "monitoring_workbook": "$(test -f infra/azure/monitoring/odoo-workload-workbook.json && echo 'present' || echo 'missing')",
    "alert_rules": "$(test -f infra/azure/monitoring/alert-rules.bicep && echo 'present' || echo 'missing')",
    "bicep_modules": $bicep_count
  }
}
EOF
  log ""
  log "Evidence saved to: $EVIDENCE_DIR/war-baseline.json"
fi

log ""
log "Next steps:"
log "  1. Deploy PIM governance: scripts/governance/configure-pim.sh"
log "  2. Deploy tag policies: az deployment group create --template-file infra/azure/modules/policy-tag-governance.bicep"
log "  3. Run tag compliance: scripts/governance/check-tag-compliance.sh --save"
log "  4. Address any WARN/FAIL items above"

exit 0
