#!/usr/bin/env bash
# =============================================================================
# OCA Fetch and Pin Script for Odoo 19
# =============================================================================
# Fetches OCA repositories and pins them to specific commits for reproducibility.
# Uses the canonical lockfile at vendor/oca.lock.ce19.json
#
# Usage:
#   ./scripts/oca/fetch_and_pin.sh [--force]
#
# Options:
#   --force    Re-clone even if directory exists
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
LOCKFILE="$ROOT_DIR/vendor/oca.lock.ce19.json"
TARGET_DIR="$ROOT_DIR/third_party/oca"
FORCE_RECLONE="${1:-}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   OCA Fetch and Pin (Odoo 19)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

# Check dependencies
if ! command -v jq &>/dev/null; then
    echo -e "${RED}ERROR: jq is required. Install with: brew install jq${NC}"
    exit 1
fi

if ! command -v git &>/dev/null; then
    echo -e "${RED}ERROR: git is required${NC}"
    exit 1
fi

# Check lockfile
if [[ ! -f "$LOCKFILE" ]]; then
    echo -e "${RED}ERROR: Lockfile not found: $LOCKFILE${NC}"
    exit 1
fi

# Create target directory
mkdir -p "$TARGET_DIR"

# Parse lockfile
ODOO_VERSION=$(jq -r '.odoo_version' "$LOCKFILE")
REPO_COUNT=$(jq '.repos | length' "$LOCKFILE")

echo -e "${GREEN}Lockfile:${NC} $LOCKFILE"
echo -e "${GREEN}Odoo Version:${NC} $ODOO_VERSION"
echo -e "${GREEN}Repositories:${NC} $REPO_COUNT"
echo -e "${GREEN}Target:${NC} $TARGET_DIR"
echo ""

CLONED=0
SKIPPED=0
FAILED=0

# Process each repository
jq -c '.repos[]' "$LOCKFILE" | while read -r repo; do
    name=$(echo "$repo" | jq -r '.name')
    url=$(echo "$repo" | jq -r '.url')
    ref=$(echo "$repo" | jq -r '.ref')
    commit=$(echo "$repo" | jq -r '.commit')

    # Extract repo short name (e.g., "OCA/server-tools" -> "server-tools")
    short_name=$(basename "$name")
    repo_path="$TARGET_DIR/$short_name"

    echo -e "${YELLOW}Processing:${NC} $name ($ref)"

    # Skip if exists and not forcing
    if [[ -d "$repo_path/.git" ]] && [[ "$FORCE_RECLONE" != "--force" ]]; then
        echo -e "  ${GREEN}✓${NC} Already exists, skipping"
        SKIPPED=$((SKIPPED + 1))
        continue
    fi

    # Remove existing if forcing
    if [[ -d "$repo_path" ]] && [[ "$FORCE_RECLONE" == "--force" ]]; then
        echo -e "  ${YELLOW}Removing existing...${NC}"
        rm -rf "$repo_path"
    fi

    # Clone
    echo -e "  ${BLUE}Cloning...${NC}"
    if git clone --depth 1 --single-branch --branch "$ref" "$url" "$repo_path" 2>/dev/null; then
        # Get the actual commit SHA
        actual_sha=$(cd "$repo_path" && git rev-parse HEAD)
        echo -e "  ${GREEN}✓${NC} Cloned at $actual_sha"
        CLONED=$((CLONED + 1))
    else
        echo -e "  ${RED}✗${NC} Failed to clone (branch $ref may not exist)"
        FAILED=$((FAILED + 1))
    fi
done

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   Summary${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Cloned:${NC}  $CLONED"
echo -e "${YELLOW}Skipped:${NC} $SKIPPED"
echo -e "${RED}Failed:${NC}  $FAILED"

if [[ $FAILED -gt 0 ]]; then
    echo ""
    echo -e "${YELLOW}Some repos failed. This may be expected if 19.0 branches don't exist yet.${NC}"
    echo -e "${YELLOW}Check https://github.com/OCA for branch availability.${NC}"
fi

echo ""
echo -e "${GREEN}Done. Run ./scripts/oca/generate_inventory.sh to update inventory.${NC}"
