#!/bin/bash
# =============================================================================
# OCA Vendor Sync Script v2.0
# =============================================================================
# Syncs OCA repositories to addons/oca/ based on vendor/oca.lock.json
#
# Usage:
#   ./vendor/oca-sync.sh sync     # Clone/update OCA repos to pinned versions
#   ./vendor/oca-sync.sh verify   # Verify repos match lockfile
#   ./vendor/oca-sync.sh update   # Update lockfile with current HEAD commits
#   ./vendor/oca-sync.sh list     # List all OCA repos and their status
#   ./vendor/oca-sync.sh export   # Export modules for Docker build (no .git)
#
# Requirements:
#   - jq (for JSON parsing)
#   - git
#
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOCKFILE="$SCRIPT_DIR/oca.lock.json"
TARGET_DIR="$REPO_ROOT/addons/oca"
EXPORT_DIR="$REPO_ROOT/.build/oca-modules"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_debug() { [[ "${DEBUG:-}" == "1" ]] && echo -e "${CYAN}[DEBUG]${NC} $1" || true; }

# Check dependencies
check_deps() {
    if ! command -v jq &> /dev/null; then
        log_error "jq is required but not installed. Install with: apt install jq"
        exit 1
    fi
    if ! command -v git &> /dev/null; then
        log_error "git is required but not installed."
        exit 1
    fi
}

# Get repository list from lockfile
get_repos() {
    jq -c '.repos[]' "$LOCKFILE"
}

# Sync a single repository
sync_repo() {
    local name url ref commit repo_dir
    name=$(echo "$1" | jq -r '.name')
    url=$(echo "$1" | jq -r '.url')
    ref=$(echo "$1" | jq -r '.ref')
    commit=$(echo "$1" | jq -r '.commit')

    local short_name
    short_name=$(echo "$name" | cut -d'/' -f2)
    repo_dir="$TARGET_DIR/$short_name"

    log_info "Syncing $name..."

    if [[ -d "$repo_dir/.git" ]]; then
        # Update existing repo
        cd "$repo_dir"
        git fetch origin --quiet

        if [[ "$commit" != "HEAD" && "$commit" != "null" && -n "$commit" ]]; then
            git checkout "$commit" --quiet 2>/dev/null || {
                log_warn "$name: fetching full history for commit $commit"
                git fetch --unshallow origin 2>/dev/null || true
                git checkout "$commit" --quiet
            }
            log_success "$name synced to commit $commit"
        else
            git checkout "origin/$ref" --quiet
            log_success "$name synced to $ref HEAD"
        fi
    else
        # Clone new repo
        mkdir -p "$TARGET_DIR"

        if [[ "$commit" != "HEAD" && "$commit" != "null" && -n "$commit" ]]; then
            # Clone and checkout specific commit
            git clone --branch "$ref" "$url" "$repo_dir" --quiet
            cd "$repo_dir"
            git checkout "$commit" --quiet
            log_success "$name cloned at commit $commit"
        else
            # Shallow clone at branch HEAD
            git clone --depth 1 --branch "$ref" "$url" "$repo_dir" --quiet
            log_success "$name cloned at $ref HEAD"
        fi
    fi
}

# Verify a single repository
verify_repo() {
    local name url ref commit repo_dir errors=0
    name=$(echo "$1" | jq -r '.name')
    url=$(echo "$1" | jq -r '.url')
    ref=$(echo "$1" | jq -r '.ref')
    commit=$(echo "$1" | jq -r '.commit')

    local short_name
    short_name=$(echo "$name" | cut -d'/' -f2)
    repo_dir="$TARGET_DIR/$short_name"

    if [[ ! -d "$repo_dir/.git" ]]; then
        log_error "$name: Not found at $repo_dir"
        return 1
    fi

    cd "$repo_dir"
    local current_commit
    current_commit=$(git rev-parse HEAD)

    if [[ "$commit" != "HEAD" && "$commit" != "null" && -n "$commit" ]]; then
        if [[ "$current_commit" == "$commit"* ]]; then
            log_success "$name: OK (pinned at ${commit:0:12})"
            return 0
        else
            log_error "$name: Mismatch (expected ${commit:0:12}, got ${current_commit:0:12})"
            return 1
        fi
    else
        log_warn "$name: Not pinned (currently at ${current_commit:0:12})"
        return 0
    fi
}

# Verify all modules listed in lockfile exist in the cloned repos
verify_modules() {
    local errors=0

    log_info "Verifying module availability..."

    while read -r repo; do
        local short_name modules repo_dir
        short_name=$(echo "$repo" | jq -r '.name' | cut -d'/' -f2)
        modules=$(echo "$repo" | jq -r '.modules[]' 2>/dev/null || echo "")
        repo_dir="$TARGET_DIR/$short_name"

        for module in $modules; do
            if [[ -d "$repo_dir/$module" ]]; then
                log_debug "  $short_name/$module: found"
            else
                log_error "  $short_name/$module: MISSING"
                ((errors++))
            fi
        done
    done < <(get_repos)

    if [[ $errors -gt 0 ]]; then
        log_error "$errors module(s) missing from lockfile definition"
        return 1
    else
        log_success "All modules verified"
        return 0
    fi
}

# Update lockfile with current HEAD commits
update_lockfile() {
    local temp_file
    temp_file=$(mktemp)

    log_info "Updating lockfile with current commits..."

    # Read the lockfile and update commits
    jq --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" '.generated_at = $timestamp' "$LOCKFILE" > "$temp_file"

    while read -r repo; do
        local name short_name repo_dir current_commit
        name=$(echo "$repo" | jq -r '.name')
        short_name=$(echo "$name" | cut -d'/' -f2)
        repo_dir="$TARGET_DIR/$short_name"

        if [[ -d "$repo_dir/.git" ]]; then
            cd "$repo_dir"
            current_commit=$(git rev-parse HEAD)

            # Update the commit in temp file
            jq --arg name "$name" --arg commit "$current_commit" \
               '(.repos[] | select(.name == $name) | .commit) = $commit' \
               "$temp_file" > "${temp_file}.new"
            mv "${temp_file}.new" "$temp_file"

            log_info "  $name: ${current_commit:0:12}"
        else
            log_warn "  $name: not cloned, skipping"
        fi
    done < <(get_repos)

    mv "$temp_file" "$LOCKFILE"
    log_success "Lockfile updated with pinned commits"
}

# List all repos and their status
list_repos() {
    echo ""
    echo "OCA Repositories in lockfile:"
    echo "=============================="
    printf "%-30s %-10s %-15s %s\n" "Repository" "Branch" "Status" "Commit"
    printf "%-30s %-10s %-15s %s\n" "----------" "------" "------" "------"

    while read -r repo; do
        local name short_name ref commit repo_dir status current_commit
        name=$(echo "$repo" | jq -r '.name')
        short_name=$(echo "$name" | cut -d'/' -f2)
        ref=$(echo "$repo" | jq -r '.ref')
        commit=$(echo "$repo" | jq -r '.commit')
        repo_dir="$TARGET_DIR/$short_name"

        if [[ -d "$repo_dir/.git" ]]; then
            cd "$repo_dir"
            current_commit=$(git rev-parse --short HEAD)

            if [[ "$commit" != "HEAD" && "$commit" != "null" && -n "$commit" ]]; then
                if [[ "$(git rev-parse HEAD)" == "$commit"* ]]; then
                    status="PINNED"
                else
                    status="DRIFT"
                fi
            else
                status="UNPINNED"
            fi
        else
            status="NOT CLONED"
            current_commit="-"
        fi

        printf "%-30s %-10s %-15s %s\n" "$short_name" "$ref" "$status" "$current_commit"
    done < <(get_repos)

    echo ""
}

# Export modules for Docker build (without .git directories)
export_modules() {
    log_info "Exporting OCA modules for Docker build..."

    rm -rf "$EXPORT_DIR"
    mkdir -p "$EXPORT_DIR"

    while read -r repo; do
        local short_name modules repo_dir
        short_name=$(echo "$repo" | jq -r '.name' | cut -d'/' -f2)
        modules=$(echo "$repo" | jq -r '.modules[]' 2>/dev/null || echo "")
        repo_dir="$TARGET_DIR/$short_name"

        for module in $modules; do
            if [[ -d "$repo_dir/$module" ]]; then
                log_debug "  Exporting $short_name/$module"
                rsync -a --delete "$repo_dir/$module/" "$EXPORT_DIR/$module/"
            else
                log_warn "  Skipping missing module: $short_name/$module"
            fi
        done
    done < <(get_repos)

    # Remove any .git directories
    find "$EXPORT_DIR" -name ".git" -type d -exec rm -rf {} + 2>/dev/null || true

    local module_count
    module_count=$(find "$EXPORT_DIR" -maxdepth 1 -type d | wc -l)
    ((module_count--)) # subtract 1 for the directory itself

    log_success "Exported $module_count modules to $EXPORT_DIR"
}

# Show help
show_help() {
    echo "OCA Vendor Sync Script v2.0"
    echo ""
    echo "Usage: $0 <command>"
    echo ""
    echo "Commands:"
    echo "  sync      Clone/update OCA repos to versions in oca.lock.json"
    echo "  verify    Check if repos match lockfile (commits + modules)"
    echo "  update    Update lockfile with current HEAD commits"
    echo "  list      List all OCA repos and their status"
    echo "  export    Export modules for Docker build (no .git)"
    echo ""
    echo "Lockfile: $LOCKFILE"
    echo "Target:   $TARGET_DIR"
    echo ""
    echo "Environment:"
    echo "  DEBUG=1   Enable debug output"
    echo ""
}

# Main command dispatcher
main() {
    check_deps

    case "${1:-help}" in
        sync)
            log_info "Syncing OCA repositories to $TARGET_DIR"
            mkdir -p "$TARGET_DIR"

            while read -r repo; do
                sync_repo "$repo"
            done < <(get_repos)

            log_success "All OCA repositories synced"
            ;;

        verify)
            log_info "Verifying OCA repositories against lockfile"

            local errors=0
            while read -r repo; do
                verify_repo "$repo" || ((errors++))
            done < <(get_repos)

            verify_modules || ((errors++))

            if [[ $errors -gt 0 ]]; then
                log_error "$errors verification issue(s) found"
                exit 1
            else
                log_success "All OCA repositories verified"
            fi
            ;;

        update)
            update_lockfile
            ;;

        list)
            list_repos
            ;;

        export)
            export_modules
            ;;

        help|--help|-h)
            show_help
            ;;

        *)
            log_error "Unknown command: $1"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
