#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ./scripts/crawl_site.sh <base_url> <out_dir>
#
# Notes:
# - Respects basic politeness (rate limit).
# - Captures HTML + assets enough for offline parsing.
# - If target blocks crawling, you still get whatever is fetchable.

BASE_URL="${1:?base_url required}"
OUT_DIR="${2:?out_dir required}"

mkdir -p "$OUT_DIR"

# Wget mirror with sane throttles.
wget \
  --mirror \
  --page-requisites \
  --adjust-extension \
  --convert-links \
  --no-parent \
  --wait=1 \
  --random-wait \
  --timeout=20 \
  --tries=2 \
  --user-agent="Mozilla/5.0 (compatible; IPAI-CatalogBot/1.0)" \
  --directory-prefix="$OUT_DIR" \
  "$BASE_URL"
