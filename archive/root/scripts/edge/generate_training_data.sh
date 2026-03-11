#!/usr/bin/env bash
# =============================================================================
# generate_training_data.sh — Convert edge drift report into agent training data
# =============================================================================
# Reads ssot/edge/drift_report.json and ssot/edge/nginx_cloudflare_map.yaml
# to produce labeled troubleshooting examples for smol-LLM fine-tuning.
#
# Usage:
#   bash scripts/edge/generate_training_data.sh
#
# Output:
#   datasets/agent_troubleshoot/edge/<timestamp>.json
# =============================================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
DRIFT_JSON="${REPO_ROOT}/ssot/edge/drift_report.json"
SSOT_FILE="${REPO_ROOT}/ssot/edge/nginx_cloudflare_map.yaml"
TIMESTAMP="$(date +%Y%m%d-%H%M%z)"
OUTPUT_DIR="${REPO_ROOT}/datasets/agent_troubleshoot/edge"
OUTPUT_FILE="${OUTPUT_DIR}/${TIMESTAMP}.json"

if [[ ! -f "$DRIFT_JSON" ]]; then
  echo "ERROR: drift_report.json not found. Run audit_nginx_cloudflare.sh first."
  exit 1
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "ERROR: jq required. Install: brew install jq"
  exit 1
fi

mkdir -p "$OUTPUT_DIR"

# Extract failure modes from SSOT (simple grep-based YAML extraction)
failure_modes_json="[]"
if [[ -f "$SSOT_FILE" ]]; then
  # Extract FM IDs and titles
  fm_ids=()
  fm_titles=()
  while IFS= read -r line; do
    if [[ "$line" =~ ^[[:space:]]*-\ id:\ (.+) ]]; then
      fm_ids+=("${BASH_REMATCH[1]}")
    fi
    if [[ "$line" =~ ^[[:space:]]*title:\ \"(.+)\" ]]; then
      fm_titles+=("${BASH_REMATCH[1]}")
    fi
  done < <(sed -n '/^failure_modes:/,/^[a-z]/p' "$SSOT_FILE")

  # Build JSON array of failure modes
  fm_json="["
  for i in "${!fm_ids[@]}"; do
    title="${fm_titles[$i]:-unknown}"
    fm_json="${fm_json}{\"id\":\"${fm_ids[$i]}\",\"title\":\"${title}\"},"
  done
  fm_json="${fm_json%,}]"
  failure_modes_json="$fm_json"
fi

# Extract drift items (FAIL status) from drift report
drift_items=$(jq '[.items[] | select(.status == "FAIL")]' "$DRIFT_JSON" 2>/dev/null || echo "[]")
pass_items=$(jq '[.items[] | select(.status == "PASS")]' "$DRIFT_JSON" 2>/dev/null || echo "[]")
skip_items=$(jq '[.items[] | select(.status == "SKIP")]' "$DRIFT_JSON" 2>/dev/null || echo "[]")

# Build training document
cat > "$OUTPUT_FILE" <<ENDJSON
{
  "metadata": {
    "generated": "${TIMESTAMP}",
    "source_drift_report": "ssot/edge/drift_report.json",
    "source_ssot": "ssot/edge/nginx_cloudflare_map.yaml",
    "purpose": "Agent troubleshooting training data for edge infrastructure"
  },
  "drift_summary": $(jq '.summary' "$DRIFT_JSON"),
  "failure_items": ${drift_items},
  "pass_items": ${pass_items},
  "skip_items": ${skip_items},
  "failure_mode_catalog": ${failure_modes_json},
  "recommended_fixes": [
    {
      "drift_id": "VHOST-*",
      "pattern": "dns-exists-vhost-missing",
      "fix": "Create nginx vhost config at infra/nginx/<hostname>.conf, deploy to /etc/nginx/sites-enabled/, run certbot, reload nginx",
      "verification": "curl -sI https://<hostname> should return 200"
    },
    {
      "drift_id": "VHOST-*-HTTPS",
      "pattern": "commented-out",
      "fix": "Uncomment HTTPS server block, run certbot --nginx -d <hostname> on prod, reload nginx",
      "verification": "curl -sI https://<hostname> should show TLS handshake"
    },
    {
      "drift_id": "CF-DRIFT-*",
      "pattern": "ssot=CNAME,cf=A",
      "fix": "Update Cloudflare DNS via Terraform (edit infra/dns/subdomain-registry.yaml, run generate-dns-artifacts.sh, terraform apply)",
      "verification": "dig +short <hostname> should return CNAME target"
    }
  ],
  "evidence_paths": {
    "drift_report": "ssot/edge/drift_report.json",
    "evidence_markdown": "docs/evidence/edge_drift_*.md",
    "ssot_map": "ssot/edge/nginx_cloudflare_map.yaml",
    "runbook": "docs/runbooks/EDGE_NGINX_CLOUDFLARE.md"
  }
}
ENDJSON

echo "Training data: ${OUTPUT_FILE}"
echo "Items: $(jq '.failure_items | length' "$OUTPUT_FILE") failures, $(jq '.pass_items | length' "$OUTPUT_FILE") passes, $(jq '.skip_items | length' "$OUTPUT_FILE") skips"
echo "Failure modes: $(echo "$failure_modes_json" | jq 'length')"
