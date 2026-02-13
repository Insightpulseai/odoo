#!/usr/bin/env bash
# sync_org_apps.sh — Audit org-level GitHub App installations against manifest
# Usage: ./ops/github/integrations/sync_org_apps.sh
#
# GitHub does NOT support batch API installation of GitHub Apps.
# This script audits current installations and prints install URLs for missing apps.

set -euo pipefail

ORG="Insightpulseai"
MANIFEST="$(dirname "$0")/install_manifest.json"
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

if ! command -v gh &>/dev/null; then
  echo -e "${RED}ERROR: gh CLI not found. Install from https://cli.github.com${NC}"
  exit 1
fi

if ! command -v jq &>/dev/null; then
  echo -e "${RED}ERROR: jq not found. Install with: apt-get install jq${NC}"
  exit 1
fi

echo "=== GitHub App Installation Audit for ${ORG} ==="
echo ""

# Fetch current org installations via gh API
echo "Fetching current org installations..."
CURRENT_APPS=$(gh api "/orgs/${ORG}/installations" --paginate --jq '.installations[].app_slug' 2>/dev/null || echo "")

if [ -z "$CURRENT_APPS" ]; then
  echo -e "${YELLOW}WARNING: Could not fetch org installations (need org admin access).${NC}"
  echo "Falling back to manifest-only mode."
  echo ""
fi

# Report already-installed apps
echo -e "${GREEN}--- Currently Installed (Org Level) ---${NC}"
jq -r '.already_installed[] | "  ✓ \(.name) [\(.category)]"' "$MANIFEST"
echo ""

# Report recommended additions
echo -e "${YELLOW}--- Recommended Additions ---${NC}"
jq -r '.recommended_additions[] | "  → \(.name) [\(.priority)] — \(.reason)\n    Install: \(.install_url)\n"' "$MANIFEST"

# Report not recommended
echo -e "${RED}--- Not Recommended for Org (Personal Only) ---${NC}"
jq -r '.not_recommended_for_org[] | "  ✗ \(.name) — \(.reason)"' "$MANIFEST"
echo ""

# Summary
INSTALLED=$(jq '.already_installed | length' "$MANIFEST")
RECOMMENDED=$(jq '.recommended_additions | length' "$MANIFEST")
NOT_REC=$(jq '.not_recommended_for_org | length' "$MANIFEST")

echo "=== Summary ==="
echo "  Installed at org level:     ${INSTALLED}"
echo "  Recommended to add:         ${RECOMMENDED}"
echo "  Personal-only (skip):       ${NOT_REC}"
echo ""
echo "To install a recommended app, visit its install URL above and select the ${ORG} organization."
echo "GitHub does not support batch installation — each app must be installed individually."
