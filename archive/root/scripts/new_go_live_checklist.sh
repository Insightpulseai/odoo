#!/usr/bin/env bash
# Generate a new Go-Live Checklist from the Well-Architected template
#
# Usage:
#   ./scripts/new_go_live_checklist.sh <release-slug>
#   ./scripts/new_go_live_checklist.sh v2.0.0
#   ./scripts/new_go_live_checklist.sh prod-20260125
#
# Output:
#   docs/releases/go-live/GO_LIVE_<release-slug>.md

set -euo pipefail

# Configuration
TEMPLATE_PATH="docs/releases/GO_LIVE_WELL_ARCHITECTED_TEMPLATE.md"
OUT_DIR="docs/releases/go-live"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m'

usage() {
  cat <<EOF
Generate a new Go-Live Checklist from the Well-Architected template

Usage: $0 <release-slug>

Examples:
  $0 v2.0.0
  $0 prod-20260125
  $0 hotfix-auth-fix

Output:
  docs/releases/go-live/GO_LIVE_<release-slug>.md
EOF
  exit 1
}

# Validate input
RELEASE="${1:-}"

if [[ -z "$RELEASE" ]]; then
  echo -e "${RED}Error: Release slug required${NC}"
  usage
fi

# Sanitize release slug (alphanumeric, dash, underscore, dot)
RELEASE_SAFE=$(echo "$RELEASE" | tr -cd '[:alnum:]._-')

if [[ "$RELEASE" != "$RELEASE_SAFE" ]]; then
  echo -e "${YELLOW}Warning: Sanitized release slug to: ${RELEASE_SAFE}${NC}"
  RELEASE="$RELEASE_SAFE"
fi

# Check template exists
if [[ ! -f "$TEMPLATE_PATH" ]]; then
  echo -e "${RED}Error: Template not found: ${TEMPLATE_PATH}${NC}"
  exit 1
fi

# Create output directory
mkdir -p "$OUT_DIR"

# Output file
OUT_FILE="${OUT_DIR}/GO_LIVE_${RELEASE}.md"

# Check if already exists
if [[ -f "$OUT_FILE" ]]; then
  echo -e "${YELLOW}Already exists: ${OUT_FILE}${NC}"
  read -p "Overwrite? [y/N] " confirm
  if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
    echo "Aborted"
    exit 0
  fi
fi

# Copy template
cp "$TEMPLATE_PATH" "$OUT_FILE"

# Pre-fill release metadata
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
DATE_ONLY=$(date -u +"%Y-%m-%d")

# Update Release Name/Version field
sed -i "s/| Release Name \/ Version |.*/| Release Name \/ Version | ${RELEASE} |/" "$OUT_FILE"

# Add generation timestamp as a comment at the top
sed -i "1i <!-- Generated: ${TIMESTAMP} from ${TEMPLATE_PATH} -->" "$OUT_FILE"

echo -e "${GREEN}Created: ${OUT_FILE}${NC}"
echo ""
echo "Next steps:"
echo "  1. Edit the checklist: $OUT_FILE"
echo "  2. Complete all applicable items"
echo "  3. Collect sign-offs"
echo "  4. Commit with release artifacts"
echo ""
echo "Commands:"
echo "  code $OUT_FILE"
echo "  git add $OUT_FILE && git commit -m 'release: add go-live checklist for ${RELEASE}'"
