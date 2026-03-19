#!/bin/bash
# =============================================================================
# OCA Template Bootstrap Script
# =============================================================================
# Purpose: Bootstrap a new OCA-style addon repository using the official
#          OCA template (https://github.com/OCA/oca-addons-repo-template)
#
# Usage:
#   ./scripts/oca-template-bootstrap.sh <repo-name> [odoo-version]
#
# Examples:
#   ./scripts/oca-template-bootstrap.sh odoo-ipai-addons
#   ./scripts/oca-template-bootstrap.sh odoo-ipai-addons 18.0
#
# Requirements:
#   - pipx (for copier and pre-commit)
#   - git
#
# =============================================================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Configuration
OCA_TEMPLATE_URL="https://github.com/OCA/oca-addons-repo-template.git"
DEFAULT_ODOO_VERSION="18.0"

# Parse arguments
REPO_NAME="${1:-}"
ODOO_VERSION="${2:-$DEFAULT_ODOO_VERSION}"

if [[ -z "$REPO_NAME" ]]; then
    log_error "Usage: $0 <repo-name> [odoo-version]"
    log_error "Example: $0 odoo-ipai-addons 18.0"
    exit 1
fi

log_info "=== OCA Template Bootstrap ==="
log_info "Repository: $REPO_NAME"
log_info "Odoo Version: $ODOO_VERSION"

# =============================================================================
# Step 1: Check prerequisites
# =============================================================================
log_info "Checking prerequisites..."

check_command() {
    if ! command -v "$1" &> /dev/null; then
        log_error "$1 is not installed. Please install it first."
        exit 1
    fi
    log_info "  ✓ $1 found"
}

check_command git
check_command pipx

# Install copier and pre-commit if not available
if ! command -v copier &> /dev/null; then
    log_warn "copier not found, installing via pipx..."
    pipx install copier
fi
log_info "  ✓ copier found"

if ! command -v pre-commit &> /dev/null; then
    log_warn "pre-commit not found, installing via pipx..."
    pipx install pre-commit
fi
log_info "  ✓ pre-commit found"

# Ensure pipx path is in PATH
pipx ensurepath &>/dev/null || true

# =============================================================================
# Step 2: Generate repository from template
# =============================================================================
log_info "Generating repository from OCA template..."

if [[ -d "$REPO_NAME" ]]; then
    log_error "Directory '$REPO_NAME' already exists. Remove it or use a different name."
    exit 1
fi

# Run copier with non-interactive defaults
# Note: --UNSAFE is required for running post-generation hooks
copier copy --UNSAFE "$OCA_TEMPLATE_URL" "$REPO_NAME" \
    --data "odoo_version=$ODOO_VERSION" \
    --data "repo_name=$REPO_NAME" \
    --data "repo_description=IPAI addon repository for Odoo $ODOO_VERSION" \
    --data "github_org=jgtolentino" \
    --data "repo_slug=$REPO_NAME" \
    --defaults

cd "$REPO_NAME"

# =============================================================================
# Step 3: Initialize git and pre-commit
# =============================================================================
log_info "Initializing git repository..."
git init

log_info "Installing pre-commit hooks..."
pre-commit install
pre-commit install --hook-type commit-msg

# Run pre-commit on all files
log_info "Running pre-commit on all files (may take a moment)..."
pre-commit run -a || true

# Initial commit
log_info "Creating initial commit..."
git add .
git commit -m "chore(oca): bootstrap from OCA oca-addons-repo-template

- Generated using OCA template for Odoo $ODOO_VERSION
- Pre-commit hooks configured
- Ready for addon development"

# =============================================================================
# Step 4: Create version branches
# =============================================================================
log_info "Creating version branches..."

# Rename default branch to match Odoo version
git branch -M "$ODOO_VERSION"

# Create additional version branches if needed
if [[ "$ODOO_VERSION" == "18.0" ]]; then
    git checkout -b "19.0"
    git checkout "$ODOO_VERSION"
    log_info "  ✓ Created 18.0 and 19.0 branches"
elif [[ "$ODOO_VERSION" == "19.0" ]]; then
    git checkout -b "18.0"
    git checkout "$ODOO_VERSION"
    log_info "  ✓ Created 18.0 and 19.0 branches"
fi

# =============================================================================
# Step 5: Create addon skeletons (optional)
# =============================================================================
log_info "Creating sample addon directories..."

mkdir -p src/ipai_sample_addon/{models,views,security,tests,data}

cat > src/ipai_sample_addon/__manifest__.py << 'MANIFEST'
# -*- coding: utf-8 -*-
{
    "name": "IPAI Sample Addon",
    "version": "18.0.1.0.0",
    "category": "InsightPulse",
    "summary": "Sample addon template",
    "description": """
Sample Addon
============

This is a sample addon created by the OCA template bootstrap script.
Replace this with your actual implementation.
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.com",
    "license": "AGPL-3",
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
    ],
    "demo": [],
    "installable": True,
    "application": False,
    "auto_install": False,
}
MANIFEST

cat > src/ipai_sample_addon/__init__.py << 'INIT'
# -*- coding: utf-8 -*-
from . import models
INIT

cat > src/ipai_sample_addon/models/__init__.py << 'MODELINIT'
# -*- coding: utf-8 -*-
# from . import sample_model
MODELINIT

cat > src/ipai_sample_addon/security/ir.model.access.csv << 'SECURITY'
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
SECURITY

git add src/
git commit -m "feat(ipai): add sample addon skeleton"

# =============================================================================
# Step 6: Summary
# =============================================================================
log_info ""
log_info "=== Bootstrap Complete ==="
log_info ""
log_info "Repository created at: $(pwd)"
log_info "Current branch: $ODOO_VERSION"
log_info ""
log_info "Next steps:"
log_info "  1. Add your addons to src/"
log_info "  2. Set up remote: git remote add origin git@github.com:jgtolentino/$REPO_NAME.git"
log_info "  3. Push branches: git push -u origin $ODOO_VERSION"
log_info ""
log_info "To create new addons with mrbob:"
log_info "  pipx install mrbob"
log_info "  pipx inject mrbob bobtemplates.odoo"
log_info "  cd src && mrbob bobtemplates.odoo:addon"
log_info ""
log_info "To update from OCA template:"
log_info "  copier update --UNSAFE"
log_info ""
