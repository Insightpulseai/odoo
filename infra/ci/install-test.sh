#!/bin/bash
# =============================================================================
# Module Install Test
# =============================================================================
# Tests that IPAI modules can be installed headlessly.
#
# Usage:
#   ./infra/ci/install-test.sh                    # Install core modules
#   ./infra/ci/install-test.sh ipai_ppm           # Install specific module
#   ./infra/ci/install-test.sh --all              # Install all IPAI modules
#
# Environment:
#   DB_NAME     - Database name (default: test_install)
#   ODOO_BIN    - Path to odoo-bin (default: ./odoo-bin)
#   ADDONS_PATH - Odoo addons path (auto-detected)
#   LOG_LEVEL   - Log level (default: warn)
#
# Returns:
#   0 - All modules installed successfully
#   1 - Installation failed
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Defaults
DB_NAME="${DB_NAME:-test_install}"
ODOO_BIN="${ODOO_BIN:-$REPO_ROOT/odoo-bin}"
LOG_LEVEL="${LOG_LEVEL:-warn}"

# Core modules to always install
CORE_MODULES="ipai_ppm,ipai_advisor"

# Build addons path
build_addons_path() {
    local paths=()

    # IPAI modules
    if [[ -d "$REPO_ROOT/addons/ipai" ]]; then
        paths+=("$REPO_ROOT/addons/ipai")
    elif [[ -d "$REPO_ROOT/addons" ]]; then
        # Legacy flat structure
        paths+=("$REPO_ROOT/addons")
    fi

    # OCA modules
    if [[ -d "$REPO_ROOT/addons/oca" ]]; then
        for oca_repo in "$REPO_ROOT/addons/oca"/*/; do
            if [[ -d "$oca_repo" ]]; then
                paths+=("$oca_repo")
            fi
        done
    fi

    # OCA-addons (legacy)
    if [[ -d "$REPO_ROOT/oca-addons" ]]; then
        for oca_repo in "$REPO_ROOT/oca-addons"/*/; do
            if [[ -d "$oca_repo" ]]; then
                paths+=("$oca_repo")
            fi
        done
    fi

    # External source (legacy)
    if [[ -d "$REPO_ROOT/external-src" ]]; then
        for ext_repo in "$REPO_ROOT/external-src"/*/; do
            if [[ -d "$ext_repo" ]]; then
                paths+=("$ext_repo")
            fi
        done
    fi

    # Join with commas
    local IFS=','
    echo "${paths[*]}"
}

# Find all IPAI modules
find_all_ipai_modules() {
    local modules=()

    # New structure
    if [[ -d "$REPO_ROOT/addons/ipai" ]]; then
        for module_dir in "$REPO_ROOT/addons/ipai"/*/; do
            if [[ -f "$module_dir/__manifest__.py" ]]; then
                modules+=("$(basename "$module_dir")")
            fi
        done
    fi

    # Legacy structure
    if [[ -d "$REPO_ROOT/addons" ]]; then
        for module_dir in "$REPO_ROOT/addons"/ipai_*/; do
            if [[ -f "$module_dir/__manifest__.py" ]]; then
                modules+=("$(basename "$module_dir")")
            fi
        done
    fi

    # Join with commas
    local IFS=','
    echo "${modules[*]}"
}

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo -e "${BLUE}IPAI Module Install Test${NC}"
echo "========================"
echo ""

# Determine modules to install
MODULES=""
case "${1:-}" in
    --all)
        MODULES=$(find_all_ipai_modules)
        echo "Installing ALL IPAI modules..."
        ;;
    "")
        MODULES="$CORE_MODULES"
        echo "Installing CORE modules..."
        ;;
    *)
        MODULES="$1"
        echo "Installing specified modules..."
        ;;
esac

# Build addons path
ADDONS_PATH="${ADDONS_PATH:-$(build_addons_path)}"

echo "Database:    $DB_NAME"
echo "Modules:     $MODULES"
echo "Addons Path: $ADDONS_PATH"
echo "Log Level:   $LOG_LEVEL"
echo ""

# Check if odoo-bin exists
if [[ ! -f "$ODOO_BIN" ]]; then
    echo -e "${RED}ERROR${NC}: odoo-bin not found at $ODOO_BIN"
    echo "Set ODOO_BIN environment variable or ensure odoo-bin is in repo root."
    exit 1
fi

# Make executable
chmod +x "$ODOO_BIN"

# Run install test
echo "Running install test..."
echo ""

START_TIME=$(date +%s)

"$ODOO_BIN" \
    -d "$DB_NAME" \
    -i "$MODULES" \
    --stop-after-init \
    --log-level="$LOG_LEVEL" \
    --addons-path="$ADDONS_PATH"

EXIT_CODE=$?
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo ""
if [[ $EXIT_CODE -eq 0 ]]; then
    echo -e "${GREEN}SUCCESS${NC}: All modules installed successfully"
    echo "Duration: ${DURATION}s"
    exit 0
else
    echo -e "${RED}FAILED${NC}: Module installation failed (exit code: $EXIT_CODE)"
    echo "Duration: ${DURATION}s"
    exit 1
fi
