#!/usr/bin/env bash
# =============================================================================
# Docs Refresh Script
# =============================================================================
# Regenerates all deterministic documentation artifacts.
# Run this before committing to ensure docs are up-to-date.
#
# Usage: ./scripts/docs_refresh.sh
# =============================================================================

set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

success() { echo -e "${GREEN}✓${NC} $1"; }
warn() { echo -e "${YELLOW}!${NC} $1"; }
info() { echo -e "${BLUE}→${NC} $1"; }

echo "========================================"
echo "  Docs Refresh"
echo "  $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "========================================"
echo ""

# ==============================================================================
# 1. Regenerate Data Model Artifacts
# ==============================================================================
echo "== Regenerating data model =="
if [ -f scripts/generate_odoo_dbml.py ]; then
    info "Running scripts/generate_odoo_dbml.py"
    if python3 scripts/generate_odoo_dbml.py 2>/dev/null; then
        success "Data model artifacts regenerated"
    else
        warn "Data model generation had issues"
    fi
else
    warn "scripts/generate_odoo_dbml.py not found"
fi
echo ""

# ==============================================================================
# 2. Regenerate Finance Seed Data
# ==============================================================================
echo "== Regenerating finance seed data =="
if [ -f scripts/seed_finance_close_from_xlsx.py ]; then
    info "Running scripts/seed_finance_close_from_xlsx.py"
    if python3 scripts/seed_finance_close_from_xlsx.py 2>/dev/null; then
        success "Finance seed data regenerated"
    else
        warn "Finance seed generation had issues"
    fi
else
    warn "scripts/seed_finance_close_from_xlsx.py not found"
fi
echo ""

# ==============================================================================
# 3. Regenerate SITEMAP.md and TREE.md (if local script exists)
# ==============================================================================
echo "== Regenerating SITEMAP.md and TREE.md =="
if [ -f scripts/generate_sitemap_tree.sh ]; then
    info "Running scripts/generate_sitemap_tree.sh"
    if bash scripts/generate_sitemap_tree.sh 2>/dev/null; then
        success "SITEMAP.md and TREE.md regenerated"
    else
        warn "Sitemap/tree generation had issues"
    fi
else
    # Generate TREE.md locally if tree command available
    if command -v tree &> /dev/null; then
        info "Generating TREE.md with tree command"
        {
            echo "# Repository Structure"
            echo ""
            echo "> Auto-generated. Last update: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
            echo ""
            echo '```'
            tree -a -I '.git|node_modules|__pycache__|*.pyc|.DS_Store|.env|*.egg-info|dist|build|.mypy_cache|.pytest_cache|.coverage|htmlcov|*.lock' --dirsfirst -L 3
            echo '```'
        } > TREE.md 2>/dev/null && success "TREE.md regenerated" || warn "TREE.md generation failed"
    else
        warn "Neither generate_sitemap_tree.sh nor tree command available"
    fi
fi
echo ""

# ==============================================================================
# 4. Regenerate spec.md (if gen_repo_tree.sh exists)
# ==============================================================================
echo "== Updating spec.md tree =="
if [ -f scripts/gen_repo_tree.sh ]; then
    info "Running scripts/gen_repo_tree.sh"
    if bash scripts/gen_repo_tree.sh 2>/dev/null; then
        success "spec.md tree updated"
    else
        warn "spec.md tree update had issues"
    fi
else
    warn "scripts/gen_repo_tree.sh not found"
fi
echo ""

# ==============================================================================
# 5. Build MkDocs (validation)
# ==============================================================================
echo "== Validating MkDocs build =="
if [ -f mkdocs.yml ]; then
    if command -v mkdocs &> /dev/null || python3 -m mkdocs --version &> /dev/null; then
        info "Running mkdocs build --strict"
        if python3 -m mkdocs build --strict 2>/dev/null; then
            success "MkDocs build validated"
            # Clean up site directory (we just validated, don't need it)
            rm -rf site/ 2>/dev/null || true
        else
            warn "MkDocs build failed - check for broken links or missing nav entries"
        fi
    else
        warn "mkdocs not installed"
    fi
else
    warn "No mkdocs.yml found"
fi
echo ""

# ==============================================================================
# Summary
# ==============================================================================
echo "========================================"
echo "  Docs Refresh Complete"
echo "========================================"
echo ""

# Show what changed
echo "Changed files:"
git status --porcelain docs/ SITEMAP.md TREE.md spec.md 2>/dev/null | head -20 || echo "  (no changes)"
echo ""

echo "To commit these changes:"
echo "  git add docs/ SITEMAP.md TREE.md spec.md"
echo "  git commit -m 'docs: refresh generated documentation'"
echo ""
