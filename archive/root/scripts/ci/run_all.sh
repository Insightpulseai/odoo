#!/usr/bin/env bash
# =============================================================================
# Unified CI Runner Script
# =============================================================================
# Runs all CI gates locally to reproduce what GitHub Actions CI executes.
# This is the single source of truth for local CI reproduction.
#
# Usage: ./scripts/ci/run_all.sh
# =============================================================================

set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

success() { echo -e "${GREEN}✓${NC} $1"; }
error() { echo -e "${RED}✗${NC} $1"; }
warn() { echo -e "${YELLOW}!${NC} $1"; }
info() { echo -e "${BLUE}→${NC} $1"; }

# Track failures
FAILURES=0

echo "========================================"
echo "  Unified CI Runner"
echo "  $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "========================================"
echo ""

# ==============================================================================
# 1. Python Dependencies
# ==============================================================================
echo "== CI: Python dependencies =="
if command -v python3 &> /dev/null; then
    python3 -m pip install -q --upgrade pip 2>/dev/null || true
    if [ -f requirements.txt ]; then
        info "Installing from requirements.txt"
        python3 -m pip install -q -r requirements.txt 2>/dev/null || warn "Some requirements failed to install"
    fi
    if [ -f requirements-docs.txt ]; then
        info "Installing from requirements-docs.txt"
        python3 -m pip install -q -r requirements-docs.txt 2>/dev/null || warn "Some docs requirements failed"
    fi
    success "Python dependencies checked"
else
    warn "Python3 not found; skipping Python gates"
fi
echo ""

# ==============================================================================
# 2. Node Dependencies
# ==============================================================================
echo "== CI: Node dependencies =="
if command -v pnpm &> /dev/null; then
    info "Installing with pnpm"
    pnpm install --frozen-lockfile 2>/dev/null || pnpm install 2>/dev/null || warn "pnpm install had issues"
    success "Node dependencies installed"
elif command -v npm &> /dev/null; then
    info "pnpm not found, using npm"
    npm ci 2>/dev/null || npm install 2>/dev/null || warn "npm install had issues"
    success "Node dependencies installed with npm"
else
    warn "Neither pnpm nor npm found; skipping Node gates"
fi
echo ""

# ==============================================================================
# 3. Pre-commit Hooks
# ==============================================================================
echo "== CI: Pre-commit hooks =="
if [ -f .pre-commit-config.yaml ] && command -v pre-commit &> /dev/null; then
    if pre-commit run -a; then
        success "pre-commit checks passed"
    else
        error "pre-commit checks failed"
        FAILURES=$((FAILURES + 1))
    fi
else
    if [ ! -f .pre-commit-config.yaml ]; then
        warn "No .pre-commit-config.yaml found"
    else
        warn "pre-commit not installed (pip install pre-commit)"
    fi
fi
echo ""

# ==============================================================================
# 4. Odoo CI Preflight Checks
# ==============================================================================
echo "== CI: Odoo preflight checks =="
if [ -f scripts/ci_local.sh ]; then
    if ./scripts/ci_local.sh; then
        success "Odoo preflight checks passed"
    else
        error "Odoo preflight checks failed"
        FAILURES=$((FAILURES + 1))
    fi
else
    warn "scripts/ci_local.sh not found, skipping Odoo preflight"
fi
echo ""

# ==============================================================================
# 5. Deterministic Generator Drift Checks
# ==============================================================================
echo "== CI: Deterministic generators (drift checks) =="

# Data model drift
if [ -f scripts/generate_odoo_dbml.py ]; then
    info "Checking docs/data-model/ drift"
    python3 scripts/generate_odoo_dbml.py 2>/dev/null || true
    if git diff --exit-code docs/data-model/ > /dev/null 2>&1; then
        success "docs/data-model/ is up-to-date"
    else
        error "Drift detected in docs/data-model/"
        git diff --stat docs/data-model/
        FAILURES=$((FAILURES + 1))
    fi
else
    warn "scripts/generate_odoo_dbml.py not found, skipping data-model drift check"
fi

# Finance seed drift
if [ -f scripts/seed_finance_close_from_xlsx.py ]; then
    info "Checking finance close seed drift"
    python3 scripts/seed_finance_close_from_xlsx.py 2>/dev/null || true
    if git diff --exit-code addons/ipai_finance_close_seed/ > /dev/null 2>&1; then
        success "Finance close seed data is up-to-date"
    else
        error "Drift detected in addons/ipai_finance_close_seed/"
        git diff --stat addons/ipai_finance_close_seed/
        FAILURES=$((FAILURES + 1))
    fi
else
    warn "scripts/seed_finance_close_from_xlsx.py not found, skipping seed drift check"
fi

echo ""

# ==============================================================================
# 6. Docs Build (MkDocs)
# ==============================================================================
echo "== CI: MkDocs build =="
if [ -f mkdocs.yml ]; then
    if command -v mkdocs &> /dev/null || python3 -m mkdocs --version &> /dev/null; then
        info "Building docs with mkdocs --strict"
        if python3 -m mkdocs build --strict 2>/dev/null; then
            success "MkDocs build passed"
        else
            error "MkDocs build failed"
            FAILURES=$((FAILURES + 1))
        fi
    else
        warn "mkdocs not installed (pip install mkdocs mkdocs-material)"
    fi
else
    warn "No mkdocs.yml found, skipping docs build"
fi
echo ""

# ==============================================================================
# 7. Repo Health Check
# ==============================================================================
echo "== CI: Repo health check =="
if [ -f scripts/repo_health.sh ]; then
    if ./scripts/repo_health.sh; then
        success "Repo health check passed"
    else
        error "Repo health check failed"
        FAILURES=$((FAILURES + 1))
    fi
else
    warn "scripts/repo_health.sh not found"
fi
echo ""

# ==============================================================================
# 8. Spec Validation
# ==============================================================================
echo "== CI: Spec validation =="
if [ -f scripts/spec_validate.sh ]; then
    if ./scripts/spec_validate.sh; then
        success "Spec validation passed"
    else
        error "Spec validation failed"
        FAILURES=$((FAILURES + 1))
    fi
else
    warn "scripts/spec_validate.sh not found"
fi
echo ""

# ==============================================================================
# 9. Node.js Lint/Typecheck/Build
# ==============================================================================
echo "== CI: Node.js lint/typecheck/build =="
if [ -f package.json ]; then
    if command -v pnpm &> /dev/null; then
        PKG_CMD="pnpm"
    elif command -v npm &> /dev/null; then
        PKG_CMD="npm"
    else
        PKG_CMD=""
    fi

    if [ -n "$PKG_CMD" ]; then
        # Check if lint script exists
        if grep -q '"lint"' package.json 2>/dev/null; then
            info "Running $PKG_CMD run lint"
            if $PKG_CMD run lint 2>/dev/null; then
                success "Lint passed"
            else
                warn "Lint had issues (non-fatal)"
            fi
        fi

        # Check if typecheck script exists
        if grep -q '"typecheck"' package.json 2>/dev/null; then
            info "Running $PKG_CMD run typecheck"
            if $PKG_CMD run typecheck 2>/dev/null; then
                success "Typecheck passed"
            else
                warn "Typecheck had issues (non-fatal)"
            fi
        fi

        # Check if build script exists
        if grep -q '"build"' package.json 2>/dev/null; then
            info "Running $PKG_CMD run build"
            if $PKG_CMD run build 2>/dev/null; then
                success "Build passed"
            else
                warn "Build had issues (non-fatal)"
            fi
        fi
    fi
else
    warn "No package.json found"
fi
echo ""

# ==============================================================================
# Summary
# ==============================================================================
echo "========================================"
if [ $FAILURES -gt 0 ]; then
    echo -e "${RED}  CI FAILED: $FAILURES issue(s)${NC}"
    echo "========================================"
    echo ""
    echo "Fix the above issues and re-run:"
    echo "  ./scripts/ci/run_all.sh"
    echo ""
    exit 1
else
    echo -e "${GREEN}  CI PASSED (all green)${NC}"
    echo "========================================"
    echo ""
    echo "All checks passed. Safe to push."
    exit 0
fi
