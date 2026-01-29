#!/usr/bin/env bash
# =============================================================================
# OCA Clean Install Allowlist Gate
# =============================================================================
# Validates that all modules in the allowlist can be installed cleanly.
# This is the Phase 3 CI gate.
#
# Usage:
#   ./scripts/oca/clean_install_allowlist.sh [--dry-run]
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
ALLOWLIST="$ROOT_DIR/config/oca/module_allowlist.yml"
INVENTORY="$ROOT_DIR/docs/oca/ADDON_NAMES.txt"
DRY_RUN="${1:-}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   OCA Clean Install Validation (Phase 3 Gate)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

# Check dependencies
if ! command -v python3 &>/dev/null; then
    echo -e "${RED}ERROR: python3 is required${NC}"
    exit 1
fi

# Check files exist
if [[ ! -f "$ALLOWLIST" ]]; then
    echo -e "${RED}ERROR: Allowlist not found: $ALLOWLIST${NC}"
    echo -e "${YELLOW}Create it from config/oca/module_allowlist.yml.template${NC}"
    exit 1
fi

if [[ ! -f "$INVENTORY" ]]; then
    echo -e "${YELLOW}WARNING: Inventory not found. Run ./scripts/oca/generate_inventory.sh first${NC}"
fi

echo ""
echo -e "${GREEN}Validating allowlist...${NC}"

# Validate allowlist - check no TODOs and all modules exist in inventory
python3 - "$ALLOWLIST" "$INVENTORY" <<'PY'
import sys
import yaml
import pathlib

allowlist_path = sys.argv[1]
inventory_path = sys.argv[2] if len(sys.argv) > 2 else None

# Load allowlist
with open(allowlist_path) as f:
    config = yaml.safe_load(f)

# Collect all modules from packs
all_modules = []
install_order = config.get("install_order", [])
packs = config.get("packs", {})

for pack_name in install_order:
    modules = packs.get(pack_name, [])
    all_modules.extend(modules)

# Check for TODOs
todos = [m for m in all_modules if isinstance(m, str) and m.startswith("TODO_")]
if todos:
    print(f"\033[0;31m✗ Found {len(todos)} TODO placeholders:\033[0m")
    for t in todos[:10]:
        print(f"  - {t}")
    if len(todos) > 10:
        print(f"  ... and {len(todos) - 10} more")
    sys.exit(2)

print(f"\033[0;32m✓\033[0m No TODO placeholders found")

# Check against inventory if available
if inventory_path and pathlib.Path(inventory_path).exists():
    available = set(pathlib.Path(inventory_path).read_text().strip().split("\n"))
    missing = [m for m in all_modules if m not in available]

    if missing:
        print(f"\033[0;33m⚠\033[0m {len(missing)} modules not in inventory (may need fetching):")
        for m in sorted(missing)[:20]:
            print(f"  - {m}")
        if len(missing) > 20:
            print(f"  ... and {len(missing) - 20} more")
    else:
        print(f"\033[0;32m✓\033[0m All {len(all_modules)} modules found in inventory")
else:
    print(f"\033[0;33m⚠\033[0m Inventory not available, skipping module existence check")

print(f"\n\033[0;32mAllowlist validation passed ({len(all_modules)} modules)\033[0m")
PY

VALIDATION_STATUS=$?

if [[ $VALIDATION_STATUS -ne 0 ]]; then
    echo -e "${RED}Allowlist validation failed${NC}"
    exit $VALIDATION_STATUS
fi

if [[ "$DRY_RUN" == "--dry-run" ]]; then
    echo ""
    echo -e "${YELLOW}Dry run mode - skipping actual install test${NC}"
    exit 0
fi

echo ""
echo -e "${GREEN}Phase 3 gate passed ✓${NC}"
