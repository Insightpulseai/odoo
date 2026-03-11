#!/usr/bin/env bash
# ==================================================
# verify_local.sh — Local CI verification (mirrors CI)
# ==================================================
# Runs all verification checks locally to ensure
# changes pass CI before pushing.
#
# Usage: ./scripts/verify_local.sh
# ==================================================

set -euo pipefail

echo "======================================"
echo "  Local Verification Suite"
echo "======================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

success() { echo -e "${GREEN}✓${NC} $1"; }
error() { echo -e "${RED}✗${NC} $1"; }
warn() { echo -e "${YELLOW}!${NC} $1"; }

# Track overall status
FAILED=0

# ----------------------------------------------
# 1. Pre-commit hooks
# ----------------------------------------------
echo "== pre-commit =="
if command -v pre-commit &> /dev/null; then
    if pre-commit run -a; then
        success "pre-commit checks passed"
    else
        error "pre-commit checks failed"
        FAILED=1
    fi
else
    warn "pre-commit not installed, skipping (pip install pre-commit)"
fi
echo ""

# ----------------------------------------------
# 2. Deterministic data-model check
# ----------------------------------------------
echo "== deterministic data-model =="
if [ -f scripts/generate_odoo_dbml.py ]; then
    python scripts/generate_odoo_dbml.py 2>/dev/null || true
    if git diff --exit-code docs/data-model/ > /dev/null 2>&1; then
        success "docs/data-model/ is up-to-date"
    else
        error "docs/data-model drift detected. Regenerate and commit."
        git diff --stat docs/data-model/
        FAILED=1
    fi
else
    warn "scripts/generate_odoo_dbml.py not found, skipping data-model check"
fi
echo ""

# ----------------------------------------------
# 3. Seed drift checks (if present)
# ----------------------------------------------
echo "== seed drift checks =="
if [ -f scripts/seed_finance_close_from_xlsx.py ]; then
    python scripts/seed_finance_close_from_xlsx.py 2>/dev/null || true
    if git diff --exit-code addons/ipai_finance_close_seed/ > /dev/null 2>&1; then
        success "Finance close seed data is up-to-date"
    else
        error "Seed drift detected in addons/ipai_finance_close_seed/. Regenerate and commit."
        git diff --stat addons/ipai_finance_close_seed/
        FAILED=1
    fi
else
    warn "scripts/seed_finance_close_from_xlsx.py not found, skipping seed drift check"
fi
echo ""

# ----------------------------------------------
# 4. Repo health check
# ----------------------------------------------
echo "== repo health =="
if [ -f scripts/repo_health.sh ]; then
    if ./scripts/repo_health.sh; then
        success "Repo health check passed"
    else
        error "Repo health check failed"
        FAILED=1
    fi
else
    warn "scripts/repo_health.sh not found, skipping"
fi
echo ""

# ----------------------------------------------
# 5. Spec validation
# ----------------------------------------------
echo "== spec validation =="
if [ -f scripts/spec_validate.sh ]; then
    if ./scripts/spec_validate.sh; then
        success "Spec validation passed"
    else
        error "Spec validation failed"
        FAILED=1
    fi
else
    warn "scripts/spec_validate.sh not found, skipping"
fi
echo ""

# ----------------------------------------------
# Summary
# ----------------------------------------------
echo "======================================"
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}All checks passed!${NC}"
    echo "======================================"
    exit 0
else
    echo -e "${RED}Some checks failed. Please fix before committing.${NC}"
    echo "======================================"
    exit 1
fi
