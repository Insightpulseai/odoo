#!/bin/bash
# =============================================================================
# OCA Vendor Sync Script
# =============================================================================
# Syncs OCA repositories to addons/oca/ based on vendor/oca.lock
#
# Usage:
#   ./vendor/oca-sync.sh sync     # Clone/update OCA repos to pinned versions
#   ./vendor/oca-sync.sh verify   # Verify repos match lockfile
#   ./vendor/oca-sync.sh update   # Update lockfile with current HEAD commits
#   ./vendor/oca-sync.sh list     # List all OCA repos and their status
#
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOCKFILE="$SCRIPT_DIR/oca.lock"
TARGET_DIR="$REPO_ROOT/addons/oca"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Parse YAML lockfile (simplified - uses grep/awk)
# For production, consider using yq or a proper YAML parser
parse_repos() {
    local in_repos=false
    local current_repo=""
    local current_url=""
    local current_branch=""
    local current_commit=""

    while IFS= read -r line; do
        # Skip comments and empty lines
        [[ "$line" =~ ^[[:space:]]*# ]] && continue
        [[ -z "${line// }" ]] && continue

        # Check if we're in repos section
        if [[ "$line" == "repos:" ]]; then
            in_repos=true
            continue
        fi

        if $in_repos; then
            # New repo entry (no leading spaces, ends with :)
            if [[ "$line" =~ ^[[:space:]]{2}([a-zA-Z0-9_-]+):$ ]]; then
                # Output previous repo if exists
                if [[ -n "$current_repo" ]]; then
                    echo "$current_repo|$current_url|$current_branch|$current_commit"
                fi
                current_repo="${BASH_REMATCH[1]}"
                current_url=""
                current_branch=""
                current_commit=""
            elif [[ "$line" =~ ^[[:space:]]+url:[[:space:]]*(.*) ]]; then
                current_url="${BASH_REMATCH[1]}"
            elif [[ "$line" =~ ^[[:space:]]+branch:[[:space:]]*\"?([^\"]+)\"? ]]; then
                current_branch="${BASH_REMATCH[1]}"
            elif [[ "$line" =~ ^[[:space:]]+commit:[[:space:]]*(.*) ]]; then
                current_commit="${BASH_REMATCH[1]}"
                [[ "$current_commit" == "null" ]] && current_commit=""
            fi
        fi
    done < "$LOCKFILE"

    # Output last repo
    if [[ -n "$current_repo" ]]; then
        echo "$current_repo|$current_url|$current_branch|$current_commit"
    fi
}

sync_repo() {
    local name="$1"
    local url="$2"
    local branch="$3"
    local commit="$4"
    local repo_dir="$TARGET_DIR/$name"

    log_info "Syncing $name..."

    if [[ -d "$repo_dir" ]]; then
        # Update existing repo
        cd "$repo_dir"
        git fetch origin

        if [[ -n "$commit" ]]; then
            git checkout "$commit"
        else
            git checkout "origin/$branch"
        fi

        log_success "$name synced to ${commit:-$branch}"
    else
        # Clone new repo
        git clone --depth 1 --branch "$branch" "$url" "$repo_dir"

        if [[ -n "$commit" ]]; then
            cd "$repo_dir"
            git fetch --depth 1 origin "$commit"
            git checkout "$commit"
        fi

        log_success "$name cloned"
    fi
}

verify_repo() {
    local name="$1"
    local url="$2"
    local branch="$3"
    local commit="$4"
    local repo_dir="$TARGET_DIR/$name"

    if [[ ! -d "$repo_dir" ]]; then
        log_error "$name: Not found"
        return 1
    fi

    cd "$repo_dir"
    local current_commit=$(git rev-parse HEAD)

    if [[ -n "$commit" ]]; then
        if [[ "$current_commit" == "$commit"* ]]; then
            log_success "$name: OK (pinned at $commit)"
            return 0
        else
            log_error "$name: Mismatch (expected $commit, got $current_commit)"
            return 1
        fi
    else
        log_warn "$name: Not pinned (currently at $current_commit)"
        return 0
    fi
}

update_lockfile() {
    local temp_file=$(mktemp)
    local in_repos=false
    local current_repo=""

    while IFS= read -r line; do
        if [[ "$line" == "repos:" ]]; then
            in_repos=true
            echo "$line" >> "$temp_file"
            continue
        fi

        if $in_repos; then
            if [[ "$line" =~ ^[[:space:]]{2}([a-zA-Z0-9_-]+):$ ]]; then
                current_repo="${BASH_REMATCH[1]}"
                echo "$line" >> "$temp_file"
            elif [[ "$line" =~ ^[[:space:]]+commit: ]]; then
                local repo_dir="$TARGET_DIR/$current_repo"
                if [[ -d "$repo_dir" ]]; then
                    cd "$repo_dir"
                    local current_commit=$(git rev-parse HEAD)
                    echo "    commit: $current_commit" >> "$temp_file"
                    log_info "Updated $current_repo commit to $current_commit"
                else
                    echo "$line" >> "$temp_file"
                fi
            else
                echo "$line" >> "$temp_file"
            fi
        else
            echo "$line" >> "$temp_file"
        fi
    done < "$LOCKFILE"

    mv "$temp_file" "$LOCKFILE"
    log_success "Lockfile updated"
}

list_repos() {
    echo ""
    echo "OCA Repositories in lockfile:"
    echo "=============================="

    parse_repos | while IFS='|' read -r name url branch commit; do
        local repo_dir="$TARGET_DIR/$name"
        local status="NOT CLONED"

        if [[ -d "$repo_dir" ]]; then
            cd "$repo_dir"
            local current_commit=$(git rev-parse --short HEAD)
            status="CLONED ($current_commit)"
        fi

        printf "%-25s %-10s %s\n" "$name" "$branch" "$status"
    done

    echo ""
}

# Main command dispatcher
case "${1:-help}" in
    sync)
        log_info "Syncing OCA repositories to $TARGET_DIR"
        mkdir -p "$TARGET_DIR"

        parse_repos | while IFS='|' read -r name url branch commit; do
            sync_repo "$name" "$url" "$branch" "$commit"
        done

        log_success "All OCA repositories synced"
        ;;

    verify)
        log_info "Verifying OCA repositories against lockfile"

        errors=0
        parse_repos | while IFS='|' read -r name url branch commit; do
            verify_repo "$name" "$url" "$branch" "$commit" || ((errors++))
        done

        if [[ $errors -gt 0 ]]; then
            log_error "$errors repositories failed verification"
            exit 1
        else
            log_success "All OCA repositories verified"
        fi
        ;;

    update)
        log_info "Updating lockfile with current commits"
        update_lockfile
        ;;

    list)
        list_repos
        ;;

    *)
        echo "OCA Vendor Sync Script"
        echo ""
        echo "Usage: $0 <command>"
        echo ""
        echo "Commands:"
        echo "  sync    Clone/update OCA repos to versions in oca.lock"
        echo "  verify  Check if repos match lockfile"
        echo "  update  Update lockfile with current HEAD commits"
        echo "  list    List all OCA repos and status"
        echo ""
        ;;
esac
