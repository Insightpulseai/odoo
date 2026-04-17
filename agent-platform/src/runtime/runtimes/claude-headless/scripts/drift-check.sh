#!/usr/bin/env bash
# Compare Azure Resource Graph live state against SSOT YAML and report drift.
# Usage: drift-check.sh <scope> [output.json]
#   scope = azure-runtime | ssot-modules | dns
set -euo pipefail

SCOPE="${1:?scope required: azure-runtime | ssot-modules | dns}"
OUT="${2:-/dev/stdout}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
source "$SCRIPT_DIR/../lib/run.sh"

case "$SCOPE" in
  azure-runtime)
    LIVE=$(az graph query -q "Resources | where resourceGroup startswith 'rg-ipai-' | project name, type, location, tags" -o json 2>/dev/null || echo '[]')
    SSOT="$ROOT/ssot/azure/runtime-inventory.yaml"
    ;;
  ssot-modules)
    LIVE=$(find "$ROOT/addons/ipai" -maxdepth 1 -type d -mindepth 1 | xargs -n1 basename | jq -R -s -c 'split("\n") | map(select(length>0))')
    SSOT="$ROOT/ssot/odoo/module_install_manifest.yaml"
    ;;
  dns)
    LIVE=$(az network dns record-set list -g rg-ipai-dns -z insightpulseai.com -o json 2>/dev/null || echo '[]')
    SSOT="$ROOT/infra/dns/subdomain-registry.yaml"
    ;;
  *)
    echo "error: unknown scope $SCOPE" >&2; exit 2
    ;;
esac

PROMPT=$(cat <<EOF
Compare live state against SSOT and report drift.

Scope: $SCOPE
SSOT file: $SSOT
Live state (JSON):
$LIVE

For each resource, determine if it is in_sync, added (in live but not SSOT),
removed (in SSOT but not live), modified (exists in both but config differs),
or misconfigured (violates policy).

Return a structured JSON report matching the schema.
EOF
)

claude_bare_json \
  "$PROMPT" \
  "$SCRIPT_DIR/../schemas/drift-check.json" \
  --allowedTools "Read" \
  --append-system-prompt "You are an infrastructure drift auditor. Be literal. Do not infer remediation beyond what is unambiguous." \
  > "$OUT"
