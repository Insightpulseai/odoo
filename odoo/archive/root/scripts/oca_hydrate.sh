#!/usr/bin/env bash
# =============================================================================
# OCA Repository Hydrator
# =============================================================================
# Clones/updates OCA repositories based on oca.lock.json
# Usage: ./scripts/oca_hydrate.sh [--clean] [--tier N]
#
# Options:
#   --clean     Remove existing clones before hydrating
#   --tier N    Only hydrate repos up to tier N (0-12)
#   --help      Show this help message
# =============================================================================
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOCK="$ROOT/addons/oca/oca.lock.json"
DEST="$ROOT/addons/oca"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse arguments
CLEAN=false
MAX_TIER=99

while [[ $# -gt 0 ]]; do
  case $1 in
    --clean)
      CLEAN=true
      shift
      ;;
    --tier)
      MAX_TIER="$2"
      shift 2
      ;;
    --help)
      echo "Usage: $0 [--clean] [--tier N]"
      echo ""
      echo "Options:"
      echo "  --clean     Remove existing clones before hydrating"
      echo "  --tier N    Only hydrate repos up to tier N (0-12)"
      echo "  --help      Show this help message"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Check dependencies
command -v jq >/dev/null 2>&1 || { echo -e "${RED}Error: jq is required${NC}"; exit 1; }
command -v git >/dev/null 2>&1 || { echo -e "${RED}Error: git is required${NC}"; exit 1; }

# Check lockfile exists
if [[ ! -f "$LOCK" ]]; then
  # Fallback to root lockfile
  LOCK="$ROOT/oca.lock.json"
  if [[ ! -f "$LOCK" ]]; then
    echo -e "${RED}Error: oca.lock.json not found${NC}"
    exit 1
  fi
fi

echo -e "${BLUE}=== OCA Repository Hydrator ===${NC}"
echo -e "Lockfile: ${YELLOW}$LOCK${NC}"
echo -e "Destination: ${YELLOW}$DEST${NC}"
echo ""

mkdir -p "$DEST"

# Clean if requested
if [[ "$CLEAN" == "true" ]]; then
  echo -e "${YELLOW}Cleaning existing clones...${NC}"
  find "$DEST" -mindepth 1 -maxdepth 1 -type d -exec rm -rf {} \; 2>/dev/null || true
fi

# Count repos
TOTAL=$(jq -r '.repositories | keys | length' "$LOCK")
CURRENT=0
CLONED=0
UPDATED=0
SKIPPED=0

# Iterate over repositories
jq -r '.repositories | to_entries[] | @base64' "$LOCK" | while read -r encoded; do
  repo=$(echo "$encoded" | base64 -d)

  name=$(echo "$repo" | jq -r '.key')
  url=$(echo "$repo" | jq -r '.value.url')
  branch=$(echo "$repo" | jq -r '.value.branch // "18.0"')
  commit=$(echo "$repo" | jq -r '.value.commit // empty')
  tier=$(echo "$repo" | jq -r '.value.tier // 99')

  CURRENT=$((CURRENT + 1))

  # Skip if above max tier
  if [[ "$tier" -gt "$MAX_TIER" ]]; then
    echo -e "[${CURRENT}/${TOTAL}] ${YELLOW}Skipping${NC} $name (tier $tier > $MAX_TIER)"
    SKIPPED=$((SKIPPED + 1))
    continue
  fi

  target="$DEST/$name"
  ref="${commit:-$branch}"

  if [[ ! -d "$target/.git" ]]; then
    echo -e "[${CURRENT}/${TOTAL}] ${GREEN}Cloning${NC} $name -> $ref"
    git clone --filter=blob:none --branch "$branch" "$url" "$target" 2>/dev/null || \
    git clone --depth 1 --branch "$branch" "$url" "$target"
    CLONED=$((CLONED + 1))
  else
    echo -e "[${CURRENT}/${TOTAL}] ${BLUE}Updating${NC} $name -> $ref"
    UPDATED=$((UPDATED + 1))
  fi

  # Checkout specific ref
  git -C "$target" fetch --tags --force 2>/dev/null || true

  if [[ -n "$commit" ]]; then
    git -C "$target" checkout -f "$commit" 2>/dev/null || \
    git -C "$target" checkout -f "$branch"
  else
    git -C "$target" checkout -f "$branch" 2>/dev/null || true
    git -C "$target" pull --ff-only origin "$branch" 2>/dev/null || true
  fi

  # Update submodules if any
  git -C "$target" submodule update --init --recursive 2>/dev/null || true

done

echo ""
echo -e "${GREEN}=== OCA Hydration Complete ===${NC}"
echo -e "Cloned: ${GREEN}$CLONED${NC} | Updated: ${BLUE}$UPDATED${NC} | Skipped: ${YELLOW}$SKIPPED${NC}"
echo ""
echo -e "To verify: ${YELLOW}ls -la $DEST${NC}"
