#!/usr/bin/env bash
# scripts/azure/audit-tags.sh
#
# Detects tag drift across the IPAI Azure subscription against
# ssot/azure/tagging-standard.yaml. Writes an evidence bundle to
# docs/evidence/<YYYYMMDD-HHMM>/azure-tags/ per IPAI operating contract.
#
# Run:
#   bash scripts/azure/audit-tags.sh
#
# Exits 0 on PASS (zero drift), 1 on FAIL (any drift found).
# Suitable for CI (GitHub Actions scheduled run twice weekly) and
# pre-deploy gate on infra/azure/** changes.

set -euo pipefail

SUBSCRIPTION_ID="${AZURE_SUBSCRIPTION_ID:-536d8cf6-89e1-4815-aef3-d5f2c5f4d070}"
REQUIRED_TAGS=(env app costcenter owner data-classification)
FORBIDDEN_KEYS=(Environment environment ENV Owner OWNER CostCenter Cost-Center Project Service Stack workload managedBy ManagedBy managed_by Managed-By)

STAMP="$(date -u +%Y%m%d-%H%M)"
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT_DIR="${REPO_ROOT}/docs/evidence/${STAMP}/azure-tags"
mkdir -p "${OUT_DIR}/logs"

echo "[CONTEXT]"
echo "  repo:         ${REPO_ROOT}"
echo "  subscription: ${SUBSCRIPTION_ID}"
echo "  stamp:        ${STAMP}"
echo "  out:          ${OUT_DIR}"
echo ""

# ─── 1. Enumerate all resources with missing required tags ──────────────────
echo "=== Drift query (resources missing required tags) ==="
az graph query -q "
  resources
  | where subscriptionId == '${SUBSCRIPTION_ID}'
  | project id, type, name, resourceGroup, location, tags
  | extend missing_env = iif(isnull(tags['env']),1,0),
           missing_app = iif(isnull(tags['app']),1,0),
           missing_costcenter = iif(isnull(tags['costcenter']),1,0),
           missing_owner = iif(isnull(tags['owner']),1,0),
           missing_classification = iif(isnull(tags['data-classification']),1,0)
  | extend drift_score = missing_env + missing_app + missing_costcenter + missing_owner + missing_classification
  | where drift_score > 0
  | order by drift_score desc, type asc
" --first 1000 -o json > "${OUT_DIR}/drift-missing.json"

MISSING_COUNT=$(jq 'length' "${OUT_DIR}/drift-missing.json")
echo "  resources missing >=1 required tag: ${MISSING_COUNT}"

# ─── 2. Enumerate resources with forbidden (case-drift) keys ────────────────
echo ""
echo "=== Forbidden-key query (case-drift of canonical keys) ==="
FORBIDDEN_EXPR=$(printf '"%s",' "${FORBIDDEN_KEYS[@]}" | sed 's/,$//')
az graph query -q "
  resources
  | where subscriptionId == '${SUBSCRIPTION_ID}'
  | project id, type, name, resourceGroup, tags
  | mv-expand tagKV = tags
  | extend tagKey = tostring(tagKV)
  | where tagKey in (${FORBIDDEN_EXPR})
  | summarize resource_count = count() by tagKey
  | order by resource_count desc
" -o json > "${OUT_DIR}/drift-forbidden-keys.json"

FORBIDDEN_COUNT=$(jq '[.[].resource_count] | add // 0' "${OUT_DIR}/drift-forbidden-keys.json")
echo "  uses of forbidden case-variant keys: ${FORBIDDEN_COUNT}"

# ─── 3. Policy compliance state ─────────────────────────────────────────────
echo ""
echo "=== Policy assignment compliance ==="
az policy state summarize --subscription "${SUBSCRIPTION_ID}" \
  --filter "startswith(PolicyAssignmentName, 'ipai-')" \
  -o json > "${OUT_DIR}/policy-compliance.json" 2>/dev/null || {
    echo "  (policy assignments not yet deployed — see infra/azure/policy/tagging-baseline.bicep)"
}

# ─── 4. Unique key inventory (surfaces drift over time) ─────────────────────
echo ""
echo "=== Unique tag keys observed ==="
az resource list --subscription "${SUBSCRIPTION_ID}" --query "[].tags" -o json 2>/dev/null | \
  python3 -c "
import json, sys
from collections import Counter
data = json.load(sys.stdin)
keys = Counter()
for r in data or []:
    if r:
        for k in r.keys():
            keys[k] += 1
print(json.dumps({'total_unique_keys': len(keys), 'by_usage': dict(keys.most_common(50))}, indent=2))
" > "${OUT_DIR}/unique-keys.json"
UNIQUE=$(jq -r '.total_unique_keys' "${OUT_DIR}/unique-keys.json")
echo "  total unique keys across subscription: ${UNIQUE}"

# ─── 5. Summary + exit code ─────────────────────────────────────────────────
echo ""
{
  echo "=== audit-tags summary — ${STAMP} ==="
  echo "subscription:        ${SUBSCRIPTION_ID}"
  echo "unique keys:         ${UNIQUE}"
  echo "missing required:    ${MISSING_COUNT} resources"
  echo "forbidden case-drift: ${FORBIDDEN_COUNT} uses"
  echo ""
  if [ "${MISSING_COUNT}" -eq 0 ] && [ "${FORBIDDEN_COUNT}" -eq 0 ]; then
    echo "result: PASS"
  else
    echo "result: FAIL"
    echo ""
    echo "=== Top 10 missing-required resources ==="
    jq -r '.[] | "  - [\(.drift_score)] \(.type) \(.name) (\(.resourceGroup))"' "${OUT_DIR}/drift-missing.json" | head -10
    echo ""
    echo "=== Forbidden keys in use ==="
    jq -r '.[] | "  - \(.tagKey): \(.resource_count) uses"' "${OUT_DIR}/drift-forbidden-keys.json"
  fi
} | tee "${OUT_DIR}/logs/summary.txt"

if [ "${MISSING_COUNT}" -eq 0 ] && [ "${FORBIDDEN_COUNT}" -eq 0 ]; then
  exit 0
else
  exit 1
fi
