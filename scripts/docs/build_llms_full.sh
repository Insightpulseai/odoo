#!/usr/bin/env bash
# Build consolidated llms-full.txt for LLM context injection
# Combines internal docs + external llms pack index
#
# Usage:
#   ./scripts/docs/build_llms_full.sh [output_file]
#
# Output:
#   docs/llms-full.txt (default)

set -euo pipefail

OUT="${1:-docs/llms-full.txt}"

# Files to include (in order)
# Add more as needed
INTERNAL_FILES=(
  "CLAUDE.md"
  "README.md"
  "docs/architecture/EXT_AGENT_TOOL_CAPABILITIES.md"
  "docs/prompts/DUMP_REVIEW_TO_STACK_UPGRADES.md"
)

# Generate header
{
  cat <<EOF
================================================================================
InsightPulseAI — llms-full.txt
================================================================================

Generated: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
Repository: odoo-ce
Purpose: Consolidated documentation for LLM context injection

This file contains:
1. Internal documentation (CLAUDE.md, architecture docs)
2. Index of external llms packs (fetched separately)

================================================================================
TABLE OF CONTENTS
================================================================================

EOF

  # TOC
  idx=1
  for f in "${INTERNAL_FILES[@]}"; do
    if [[ -f "$f" ]]; then
      echo "$idx. $f"
      ((idx++))
    fi
  done

  if [[ -d "docs/llms/external" ]]; then
    echo "$idx. External LLMs Pack Index (docs/llms/external/)"
  fi

  echo ""
  echo "================================================================================"
  echo ""

  # Include each internal file
  for f in "${INTERNAL_FILES[@]}"; do
    if [[ -f "$f" ]]; then
      echo "================================================================================"
      echo "FILE: $f"
      echo "================================================================================"
      echo ""
      # Remove carriage returns, preserve content
      sed -e 's/\r$//' "$f"
      echo ""
      echo ""
    fi
  done

  # Index external packs (don't inline them — just list)
  if [[ -d "docs/llms/external" ]]; then
    echo "================================================================================"
    echo "EXTERNAL LLMS PACKS INDEX"
    echo "================================================================================"
    echo ""
    echo "Location: docs/llms/external/"
    echo "Fetched via: ./scripts/docs/fetch_external_llms_packs.sh"
    echo ""
    echo "Available packs:"
    find docs/llms/external -maxdepth 1 -type f -name "*.txt" ! -name "*FETCH_FAILED*" 2>/dev/null | sort | while read -r pack; do
      size=$(wc -c < "$pack" | tr -d ' ')
      echo "  - $(basename "$pack") (${size} bytes)"
    done
    echo ""
    echo "Failed fetches:"
    find docs/llms/external -maxdepth 1 -type f -name "*FETCH_FAILED*" 2>/dev/null | sort | while read -r fail; do
      echo "  - $(basename "$fail" | sed 's/__FETCH_FAILED.txt//')"
    done
    echo ""
  fi

  echo "================================================================================"
  echo "END OF llms-full.txt"
  echo "================================================================================"

} > "$OUT"

# Report
SIZE=$(wc -c < "$OUT" | tr -d ' ')
LINES=$(wc -l < "$OUT" | tr -d ' ')
echo "Generated: $OUT"
echo "Size: ${SIZE} bytes, ${LINES} lines"
