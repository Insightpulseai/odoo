#!/usr/bin/env bash
# =============================================================================
# sync-fluent-tokens.sh
# =============================================================================
# Builds Fluent 2 design tokens and syncs to Odoo module
#
# Usage:
#   ./scripts/sync-fluent-tokens.sh        # Build and sync
#   ./scripts/sync-fluent-tokens.sh --check  # Check if in sync (CI mode)
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
TOKENS_PKG="$ROOT_DIR/packages/ipai-design-tokens"
ODOO_MODULE="$ROOT_DIR/addons/ipai/ipai_theme_fluent2/static/src/css"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() { echo -e "${GREEN}✓${NC} $1"; }
log_warn() { echo -e "${YELLOW}!${NC} $1"; }
log_error() { echo -e "${RED}✗${NC} $1"; }

# Check mode (for CI)
CHECK_MODE=false
if [[ "${1:-}" == "--check" ]]; then
    CHECK_MODE=true
fi

# Ensure we're in the right directory
cd "$ROOT_DIR"

# Check if pnpm is available
if ! command -v pnpm &> /dev/null; then
    log_error "pnpm is not installed. Please install it first."
    exit 1
fi

# Install dependencies if needed
if [[ ! -d "$TOKENS_PKG/node_modules" ]]; then
    log_info "Installing dependencies..."
    pnpm install --filter @ipai/design-tokens
fi

# Build tokens
log_info "Building Fluent 2 tokens..."
pnpm -C "$TOKENS_PKG" build

# Check if output exists
if [[ ! -f "$TOKENS_PKG/dist/fluent.css" ]]; then
    log_error "Build failed: dist/fluent.css not found"
    exit 1
fi

# Ensure target directory exists
mkdir -p "$ODOO_MODULE"

# Check mode: compare files
if [[ "$CHECK_MODE" == true ]]; then
    if [[ -f "$ODOO_MODULE/fluent2.css" ]]; then
        if diff -q "$TOKENS_PKG/dist/fluent.css" "$ODOO_MODULE/fluent2.css" > /dev/null 2>&1; then
            log_info "Tokens are in sync"
            exit 0
        else
            log_error "Tokens are out of sync!"
            log_error "Run './scripts/sync-fluent-tokens.sh' to update"
            exit 1
        fi
    else
        log_error "fluent2.css not found in Odoo module"
        log_error "Run './scripts/sync-fluent-tokens.sh' to generate"
        exit 1
    fi
fi

# Sync to Odoo module
log_info "Syncing to Odoo module..."
cp "$TOKENS_PKG/dist/fluent.css" "$ODOO_MODULE/fluent2.css"

# Verify copy
if [[ -f "$ODOO_MODULE/fluent2.css" ]]; then
    LINES=$(wc -l < "$ODOO_MODULE/fluent2.css")
    log_info "Synced fluent2.css ($LINES lines)"
else
    log_error "Sync failed: fluent2.css not created"
    exit 1
fi

# Summary
echo ""
echo "=== Build Summary ==="
log_info "dist/fluent.css           → Fluent 2 CSS variables"
log_info "dist/tokens.json          → Raw tokens JSON"
log_info "dist/tailwind-preset.cjs  → Tailwind CSS preset"
log_info "Odoo module synced        → ipai_theme_fluent2"
echo ""
echo "Next steps:"
echo "  1. Install the module: docker compose exec odoo-core odoo -d odoo_core -i ipai_theme_fluent2"
echo "  2. Reference tokens in CSS: var(--colorBrandBackground)"
echo ""
