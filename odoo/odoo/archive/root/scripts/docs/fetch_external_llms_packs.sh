#!/usr/bin/env bash
# Fetch external llms.txt / llms-full.txt packs from documentation sites
# Best-effort fetch; records failures explicitly rather than silently skipping
#
# Usage:
#   ./scripts/docs/fetch_external_llms_packs.sh [output_dir]
#
# Output:
#   docs/llms/external/<source>__llms-full.txt  (if available)
#   docs/llms/external/<source>__llms.txt       (if available)
#   docs/llms/external/<source>__FETCH_FAILED.txt (if both fail)

set -euo pipefail

OUT_DIR="${1:-docs/llms/external}"
mkdir -p "$OUT_DIR"

# User agent for requests
UA="${UA:-Mozilla/5.0 (compatible; IPAI-Bot/1.0; +https://insightpulseai.com)}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[fetch-llms]${NC} $*"; }
warn() { echo -e "${YELLOW}[fetch-llms]${NC} $*"; }
fail() { echo -e "${RED}[fetch-llms]${NC} $*"; }

# Fetch one source, trying llms-full.txt then llms.txt
fetch_one() {
  local base="$1"
  local name="$2"

  # URL patterns to try (in order of preference)
  local urls=(
    "${base%/}/llms-full.txt"
    "${base%/}/llms.txt"
    "${base%/}/docs/llms-full.txt"
    "${base%/}/docs/llms.txt"
  )

  for u in "${urls[@]}"; do
    local filename
    filename=$(basename "$u")
    local out="${OUT_DIR}/${name}__${filename}"

    local status
    status=$(curl -A "$UA" -L -s -o "$out" -w "%{http_code}" --max-time 30 "$u" 2>/dev/null || echo "000")

    if [[ "$status" == "200" ]] && [[ -s "$out" ]]; then
      local size
      size=$(wc -c < "$out" | tr -d ' ')
      log "${GREEN}${status}${NC}  $u  →  $out (${size} bytes)"
      return 0
    fi

    rm -f "$out" 2>/dev/null || true
  done

  # All attempts failed — record failure marker
  local fail_file="${OUT_DIR}/${name}__FETCH_FAILED.txt"
  {
    echo "FAILED: ${base}"
    echo "Attempted URLs:"
    for u in "${urls[@]}"; do
      echo "  - $u"
    done
    echo "Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  } > "$fail_file"

  fail "FAILED  $base (no llms*.txt reachable)"
  return 0  # Don't fail the script
}

# Header
log "Fetching external llms packs to ${OUT_DIR}/"
log "User-Agent: $UA"
echo ""

# Curated sources (extend as needed)
# Format: fetch_one "base_url" "short_name"

# Developer tools
fetch_one "https://vercel.com/docs" "vercel_docs"
fetch_one "https://docs.n8n.io" "n8n_docs"
fetch_one "https://sdk.vercel.ai" "vercel_ai_sdk"
fetch_one "https://ai-sdk.dev" "ai_sdk_dev"

# Odoo / OCA
fetch_one "https://www.odoo-community.org" "oca_odoo_community"
fetch_one "https://www.odoo.com/documentation/18.0" "odoo_docs_18"

# Cloud providers
fetch_one "https://docs.digitalocean.com" "digitalocean_docs"
fetch_one "https://supabase.com/docs" "supabase_docs"

# Enterprise docs
fetch_one "https://learn.microsoft.com" "microsoft_learn"
fetch_one "https://docs.github.com" "github_docs"
fetch_one "https://help.sap.com" "sap_help"

# AI/Agent tools
fetch_one "https://jules.google/docs" "google_jules"
fetch_one "https://docs.anthropic.com" "anthropic_docs"

# Summary
echo ""
log "Done. Results in: ${OUT_DIR}/"
echo ""

# List results
echo "=== Successful fetches ==="
find "$OUT_DIR" -name "*.txt" ! -name "*FETCH_FAILED*" -type f 2>/dev/null | sort || echo "(none)"
echo ""

echo "=== Failed fetches ==="
find "$OUT_DIR" -name "*FETCH_FAILED*" -type f 2>/dev/null | sort || echo "(none)"
