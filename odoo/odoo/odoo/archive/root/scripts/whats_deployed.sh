#!/bin/bash
# =============================================================================
# whats_deployed.sh - Thin wrapper for whats_deployed.py
# =============================================================================
# Validates environment, runs Python script, reports output paths.
#
# Usage:
#   export GITHUB_TOKEN=ghp_...
#   ./scripts/whats_deployed.sh
#
# Environment Variables:
#   GITHUB_TOKEN (required): GitHub PAT or App token with repo + actions:read
#   GITHUB_OWNER (default: jgtolentino): Repository owner
#   GITHUB_REPO (default: odoo-ce): Repository name
#   PROD_ENV (default: production): Deployment environment name
#   RELEASE_TAG_PREFIX (default: prod-): Release tag prefix to match
#   WORKFLOW_NAME_HINT (default: Deploy to Production): Workflow name pattern
# =============================================================================

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Script location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/whats_deployed.py"

# Validate Python script exists
if [[ ! -f "$PYTHON_SCRIPT" ]]; then
    echo -e "${RED}ERROR: Python script not found: $PYTHON_SCRIPT${NC}"
    exit 1
fi

# Validate GITHUB_TOKEN
if [[ -z "${GITHUB_TOKEN:-}" ]]; then
    echo -e "${YELLOW}WARNING: GITHUB_TOKEN not set${NC}"
    echo "API rate limits will apply (60 requests/hour for unauthenticated)."
    echo ""
    echo "To set token:"
    echo "  export GITHUB_TOKEN=ghp_your_token_here"
    echo ""
    read -p "Continue anyway? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 1
    fi
else
    # Validate token format (basic check)
    if [[ ! "${GITHUB_TOKEN}" =~ ^(ghp_|gho_|ghu_|ghs_|ghr_|github_pat_) ]]; then
        echo -e "${YELLOW}WARNING: GITHUB_TOKEN may not be valid (unexpected prefix)${NC}"
    fi
fi

# Set defaults for optional env vars
export GITHUB_OWNER="${GITHUB_OWNER:-jgtolentino}"
export GITHUB_REPO="${GITHUB_REPO:-odoo-ce}"
export PROD_ENV="${PROD_ENV:-production}"
export RELEASE_TAG_PREFIX="${RELEASE_TAG_PREFIX:-prod-}"
export WORKFLOW_NAME_HINT="${WORKFLOW_NAME_HINT:-Deploy to Production}"

echo -e "${GREEN}=== What's Deployed ===${NC}"
echo "Repository: $GITHUB_OWNER/$GITHUB_REPO"
echo "Tag Prefix: $RELEASE_TAG_PREFIX"
echo "Environment: $PROD_ENV"
echo ""

# Run Python script
cd "$REPO_ROOT"
python3 "$PYTHON_SCRIPT"
exit_code=$?

if [[ $exit_code -ne 0 ]]; then
    echo -e "${RED}ERROR: Python script failed with exit code $exit_code${NC}"
    exit $exit_code
fi

# Verify outputs
RELEASES_DIR="$REPO_ROOT/docs/releases"
PROOFS_DIR="$RELEASES_DIR/DEPLOYMENT_PROOFS"

echo ""
echo -e "${GREEN}=== Verification ===${NC}"

# Check JSON is valid
if [[ -f "$RELEASES_DIR/WHAT_DEPLOYED.json" ]]; then
    if python3 -c "import json; json.load(open('$RELEASES_DIR/WHAT_DEPLOYED.json'))" 2>/dev/null; then
        echo -e "  ${GREEN}[PASS]${NC} WHAT_DEPLOYED.json is valid JSON"
    else
        echo -e "  ${RED}[FAIL]${NC} WHAT_DEPLOYED.json is invalid JSON"
        exit 1
    fi
else
    echo -e "  ${RED}[FAIL]${NC} WHAT_DEPLOYED.json not found"
    exit 1
fi

# Check MD exists and non-empty
if [[ -s "$RELEASES_DIR/WHAT_DEPLOYED.md" ]]; then
    echo -e "  ${GREEN}[PASS]${NC} WHAT_DEPLOYED.md exists and non-empty"
else
    echo -e "  ${RED}[FAIL]${NC} WHAT_DEPLOYED.md missing or empty"
    exit 1
fi

# Check proof files
proof_count=$(find "$PROOFS_DIR" -name "*.json" 2>/dev/null | wc -l)
if [[ $proof_count -gt 0 ]]; then
    echo -e "  ${GREEN}[PASS]${NC} $proof_count proof file(s) in DEPLOYMENT_PROOFS/"
else
    echo -e "  ${YELLOW}[WARN]${NC} No proof files in DEPLOYMENT_PROOFS/"
fi

echo ""
echo -e "${GREEN}=== Output Paths ===${NC}"
echo "  $RELEASES_DIR/WHAT_DEPLOYED.md"
echo "  $RELEASES_DIR/WHAT_DEPLOYED.json"
echo "  $PROOFS_DIR/"
echo ""
echo -e "${GREEN}Done.${NC}"
