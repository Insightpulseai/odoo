#!/usr/bin/env bash
# =============================================================================
# Check Azure Tag Compliance
# =============================================================================
# SAP Benchmark #647: Query tag compliance across IPAI resource groups.
#
# Usage:
#   ./scripts/governance/check-tag-compliance.sh [--output json|table] [--save]
#
# Requires: az cli logged in
# =============================================================================
set -euo pipefail

OUTPUT_FORMAT="table"
SAVE=false
EVIDENCE_DIR="docs/evidence/$(date -u +%Y%m%d-%H%M)/governance"

while [[ $# -gt 0 ]]; do
  case $1 in
    --output) OUTPUT_FORMAT="$2"; shift 2 ;;
    --save) SAVE=true; shift ;;
    *) echo "Unknown flag: $1"; exit 1 ;;
  esac
done

log() { echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*"; }

REQUIRED_TAGS=("Environment" "Project" "ManagedBy")
IPAI_RGS=(
  "rg-ipai-dev-odoo-runtime"
  "rg-ipai-dev-odoo-data"
  "rg-ipai-dev-platform"
  "rg-ipai-ai-dev"
  "rg-ipai-agents-dev"
)

log "=== Tag Compliance Check — SAP Benchmark #647 ==="

total_resources=0
compliant_resources=0
noncompliant_resources=0
noncompliant_list=""

for rg in "${IPAI_RGS[@]}"; do
  log "Checking resource group: $rg"

  # Get all resources in RG with their tags
  resources=$(az resource list --resource-group "$rg" --query "[].{name:name, type:type, tags:tags}" -o json 2>/dev/null || echo "[]")

  count=$(echo "$resources" | python3 -c "import json,sys; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")

  if [[ "$count" == "0" ]]; then
    log "  No resources found (RG may not exist or is empty)"
    continue
  fi

  # Check each resource for required tags
  while IFS= read -r resource; do
    name=$(echo "$resource" | python3 -c "import json,sys; print(json.load(sys.stdin)['name'])")
    rtype=$(echo "$resource" | python3 -c "import json,sys; print(json.load(sys.stdin)['type'])")
    tags_json=$(echo "$resource" | python3 -c "import json,sys; d=json.load(sys.stdin); print(json.dumps(d.get('tags') or {}))")

    total_resources=$((total_resources + 1))
    missing_tags=""

    for tag in "${REQUIRED_TAGS[@]}"; do
      has_tag=$(echo "$tags_json" | python3 -c "import json,sys; print('yes' if '$tag' in json.load(sys.stdin) else 'no')")
      if [[ "$has_tag" == "no" ]]; then
        missing_tags="${missing_tags}${tag},"
      fi
    done

    if [[ -z "$missing_tags" ]]; then
      compliant_resources=$((compliant_resources + 1))
    else
      noncompliant_resources=$((noncompliant_resources + 1))
      noncompliant_list="${noncompliant_list}\n  ${rg}/${name} (${rtype}) — missing: ${missing_tags%,}"
    fi
  done < <(echo "$resources" | python3 -c "
import json, sys
for r in json.load(sys.stdin):
    print(json.dumps(r))
")
done

# Summary
log ""
log "=== Compliance Summary ==="
log "Total resources checked: $total_resources"
log "Compliant: $compliant_resources"
log "Non-compliant: $noncompliant_resources"

if [[ $total_resources -gt 0 ]]; then
  pct=$((compliant_resources * 100 / total_resources))
  log "Compliance rate: ${pct}%"
else
  pct=0
  log "Compliance rate: N/A (no resources found)"
fi

if [[ $noncompliant_resources -gt 0 ]]; then
  log ""
  log "Non-compliant resources:"
  echo -e "$noncompliant_list"
fi

# Save evidence
if [[ "$SAVE" == "true" ]]; then
  mkdir -p "$EVIDENCE_DIR"
  cat > "$EVIDENCE_DIR/tag-compliance.json" <<EOF
{
  "benchmark": "SAP-on-Azure #647",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "total_resources": $total_resources,
  "compliant": $compliant_resources,
  "noncompliant": $noncompliant_resources,
  "compliance_rate_pct": $pct,
  "required_tags": $(printf '%s\n' "${REQUIRED_TAGS[@]}" | python3 -c "import json,sys; print(json.dumps([l.strip() for l in sys.stdin]))"),
  "resource_groups_checked": $(printf '%s\n' "${IPAI_RGS[@]}" | python3 -c "import json,sys; print(json.dumps([l.strip() for l in sys.stdin]))")
}
EOF
  log ""
  log "Evidence saved to: $EVIDENCE_DIR/tag-compliance.json"
fi

# Exit code reflects compliance
[[ $noncompliant_resources -eq 0 ]] && exit 0 || exit 1
