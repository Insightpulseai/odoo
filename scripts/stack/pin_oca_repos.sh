#!/usr/bin/env bash
# pin_oca_repos.sh - Pin OCA repositories to exact commits
# Usage: ./scripts/stack/pin_oca_repos.sh [--update]
#
# This script clones OCA repos (if not present) and records their HEAD commits
# to a lockfile for reproducible builds.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
OCA_DIR="$REPO_ROOT/addons/oca"
LOCKFILE="$REPO_ROOT/oca19.lock.json"
STACK_MANIFEST="$REPO_ROOT/stack/odoo19_stack.yaml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Parse arguments
UPDATE_MODE=false
if [[ "${1:-}" == "--update" ]]; then
    UPDATE_MODE=true
    log_info "Running in update mode - will fetch latest commits"
fi

# Extract repository list from stack manifest
if [[ ! -f "$STACK_MANIFEST" ]]; then
    log_error "Stack manifest not found: $STACK_MANIFEST"
    exit 1
fi

# OCA repositories to pin (extracted from stack manifest)
declare -A OCA_REPOS=(
    ["server-tools"]="https://github.com/OCA/server-tools"
    ["server-ux"]="https://github.com/OCA/server-ux"
    ["server-backend"]="https://github.com/OCA/server-backend"
    ["web"]="https://github.com/OCA/web"
    ["queue"]="https://github.com/OCA/queue"
    ["reporting-engine"]="https://github.com/OCA/reporting-engine"
    ["mis-builder"]="https://github.com/OCA/mis-builder"
    ["account-financial-reporting"]="https://github.com/OCA/account-financial-reporting"
    ["account-financial-tools"]="https://github.com/OCA/account-financial-tools"
    ["spreadsheet"]="https://github.com/OCA/spreadsheet"
    ["dms"]="https://github.com/OCA/dms"
    ["knowledge"]="https://github.com/OCA/knowledge"
    ["rest-framework"]="https://github.com/OCA/rest-framework"
    ["social"]="https://github.com/OCA/social"
    ["account-reconcile"]="https://github.com/OCA/account-reconcile"
    ["purchase-workflow"]="https://github.com/OCA/purchase-workflow"
    ["sale-workflow"]="https://github.com/OCA/sale-workflow"
    ["project"]="https://github.com/OCA/project"
    ["hr-expense"]="https://github.com/OCA/hr-expense"
    ["timesheet"]="https://github.com/OCA/timesheet"
    ["contract"]="https://github.com/OCA/contract"
    ["multi-company"]="https://github.com/OCA/multi-company"
    ["bank-payment"]="https://github.com/OCA/bank-payment"
    ["connector"]="https://github.com/OCA/connector"
    ["storage"]="https://github.com/OCA/storage"
    ["ai"]="https://github.com/OCA/ai"
)

BRANCH="19.0"

# Create OCA directory if needed
mkdir -p "$OCA_DIR"

# Initialize lockfile
echo "{" > "$LOCKFILE.tmp"
echo '  "version": "1.0.0",' >> "$LOCKFILE.tmp"
echo '  "odoo_version": "19.0",' >> "$LOCKFILE.tmp"
echo "  \"generated\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"," >> "$LOCKFILE.tmp"
echo '  "repositories": {' >> "$LOCKFILE.tmp"

FIRST=true
FAILED_REPOS=()

for repo_name in "${!OCA_REPOS[@]}"; do
    repo_url="${OCA_REPOS[$repo_name]}"
    repo_path="$OCA_DIR/$repo_name"

    log_info "Processing $repo_name..."

    # Clone or update
    if [[ -d "$repo_path" ]]; then
        if $UPDATE_MODE; then
            log_info "  Fetching latest from $BRANCH..."
            cd "$repo_path"
            git fetch origin "$BRANCH" 2>/dev/null || {
                log_warn "  Failed to fetch $repo_name - branch may not exist"
                FAILED_REPOS+=("$repo_name")
                cd "$REPO_ROOT"
                continue
            }
            git checkout "$BRANCH" 2>/dev/null || git checkout -b "$BRANCH" "origin/$BRANCH" 2>/dev/null
            git pull origin "$BRANCH" 2>/dev/null || true
            cd "$REPO_ROOT"
        fi
    else
        log_info "  Cloning $repo_url..."
        git clone --depth 1 --branch "$BRANCH" "$repo_url" "$repo_path" 2>/dev/null || {
            log_warn "  Failed to clone $repo_name - branch $BRANCH may not exist"
            FAILED_REPOS+=("$repo_name")
            continue
        }
    fi

    # Get commit SHA
    if [[ -d "$repo_path/.git" ]]; then
        cd "$repo_path"
        COMMIT=$(git rev-parse HEAD)
        cd "$REPO_ROOT"

        # Add to lockfile
        if ! $FIRST; then
            echo "," >> "$LOCKFILE.tmp"
        fi
        FIRST=false

        cat >> "$LOCKFILE.tmp" << EOF
    "$repo_name": {
      "url": "$repo_url",
      "branch": "$BRANCH",
      "commit": "$COMMIT"
    }
EOF
        log_info "  Pinned to $COMMIT"
    fi
done

# Close JSON
echo "" >> "$LOCKFILE.tmp"
echo "  }" >> "$LOCKFILE.tmp"
echo "}" >> "$LOCKFILE.tmp"

mv "$LOCKFILE.tmp" "$LOCKFILE"

log_info "Lockfile written to: $LOCKFILE"

# Report failures
if [[ ${#FAILED_REPOS[@]} -gt 0 ]]; then
    log_warn "The following repos failed (may not have 19.0 branch yet):"
    for repo in "${FAILED_REPOS[@]}"; do
        log_warn "  - $repo"
    done
fi

# Summary
PINNED_COUNT=$((${#OCA_REPOS[@]} - ${#FAILED_REPOS[@]}))
log_info "Successfully pinned $PINNED_COUNT/${#OCA_REPOS[@]} repositories"
