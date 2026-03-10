#!/bin/bash
# Wiki Sync Script
# Syncs docs/wiki/ content to GitHub Wiki repository
#
# Usage:
#   ./scripts/wiki_sync.sh              # Sync to wiki
#   ./scripts/wiki_sync.sh --check      # Check for differences
#   ./scripts/wiki_sync.sh --local      # Preview changes locally

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
WIKI_SOURCE="$REPO_ROOT/docs/wiki"
WIKI_CLONE="$REPO_ROOT/.wiki-clone"
GITHUB_REPO="${GITHUB_REPOSITORY:-jgtolentino/odoo-ce}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Parse arguments
CHECK_MODE=false
LOCAL_MODE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --check)
            CHECK_MODE=true
            shift
            ;;
        --local)
            LOCAL_MODE=true
            shift
            ;;
        *)
            log_error "Unknown option: $1"
            echo "Usage: $0 [--check|--local]"
            exit 1
            ;;
    esac
done

# Verify source directory
if [ ! -d "$WIKI_SOURCE" ]; then
    log_error "Wiki source directory not found: $WIKI_SOURCE"
    exit 1
fi

# Count source files
SOURCE_COUNT=$(find "$WIKI_SOURCE" -name "*.md" | wc -l)
log_info "Found $SOURCE_COUNT wiki pages in $WIKI_SOURCE"

if [ "$LOCAL_MODE" = true ]; then
    log_info "Local preview mode - listing files:"
    find "$WIKI_SOURCE" -name "*.md" -exec basename {} \;
    exit 0
fi

# Clone or update wiki repo
if [ -d "$WIKI_CLONE/.git" ]; then
    log_info "Updating existing wiki clone..."
    cd "$WIKI_CLONE"
    git fetch origin
    git reset --hard origin/master 2>/dev/null || git reset --hard origin/main
else
    log_info "Cloning wiki repository..."
    rm -rf "$WIKI_CLONE"
    git clone "https://github.com/$GITHUB_REPO.wiki.git" "$WIKI_CLONE" 2>/dev/null || {
        log_warn "Wiki not initialized. Creating empty wiki..."
        mkdir -p "$WIKI_CLONE"
        cd "$WIKI_CLONE"
        git init
        git remote add origin "https://github.com/$GITHUB_REPO.wiki.git"
    }
fi

cd "$WIKI_CLONE"

# Copy files
log_info "Copying wiki files..."
cp -r "$WIKI_SOURCE"/* .

# Fix relative links for GitHub Wiki
log_info "Fixing relative links..."
for file in *.md; do
    if [ -f "$file" ]; then
        # Convert relative spec links to blob links
        sed -i "s|\.\./spec/|https://github.com/$GITHUB_REPO/blob/main/spec/|g" "$file"
        # Convert diagram links to raw URLs
        sed -i "s|\.\./docs/diagrams/|https://raw.githubusercontent.com/$GITHUB_REPO/main/docs/diagrams/|g" "$file"
    fi
done

# Check for changes
if git diff --quiet && git diff --cached --quiet; then
    log_info "No changes to sync"
    exit 0
fi

if [ "$CHECK_MODE" = true ]; then
    log_warn "Wiki has pending changes:"
    git status --short
    git diff --stat
    exit 1
fi

# Commit and push
log_info "Committing changes..."
git add -A
git commit -m "Sync wiki from main repository ($(date +%Y-%m-%d))"

log_info "Pushing to wiki..."
git push origin HEAD:master 2>/dev/null || git push origin HEAD:main

log_info "Wiki sync complete!"
