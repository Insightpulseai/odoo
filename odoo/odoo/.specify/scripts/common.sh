#!/usr/bin/env bash
# Common functions and variables for spec-kit scripts
# Adapted from github/spec-kit for the Odoo IPAI project.
#
# Key differences from upstream:
#   - Uses spec/ (not specs/) as the bundle directory
#   - Uses prd.md (not spec.md) as the requirements file
#   - Feature slugs use lowercase-hyphen (not NNN- numbering)

# Get repository root
get_repo_root() {
    if git rev-parse --show-toplevel >/dev/null 2>&1; then
        git rev-parse --show-toplevel
    else
        local script_dir
        script_dir="$(CDPATH="" cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
        (cd "$script_dir/../.." && pwd)
    fi
}

# Get current branch, with fallback for non-git repos
get_current_branch() {
    if [[ -n "${SPECIFY_FEATURE:-}" ]]; then
        echo "$SPECIFY_FEATURE"
        return
    fi
    if git rev-parse --abbrev-ref HEAD >/dev/null 2>&1; then
        git rev-parse --abbrev-ref HEAD
        return
    fi
    echo "main"
}

has_git() {
    git rev-parse --show-toplevel >/dev/null 2>&1
}

# Derive feature slug from branch name
# Supports: feature/my-thing, claude/my-thing-ABC, NNN-my-thing, my-thing
get_feature_slug() {
    local branch="$1"
    local slug="$branch"

    # Strip common prefixes
    slug="${slug#feature/}"
    slug="${slug#feat/}"
    slug="${slug#claude/}"

    # Strip NNN- prefix if present
    slug="$(echo "$slug" | sed 's/^[0-9]\{3\}-//')"

    # Strip trailing session IDs (e.g., -PKRcZ)
    slug="$(echo "$slug" | sed 's/-[A-Za-z0-9]\{5\}$//')"

    echo "$slug"
}

# Get the spec directory for a given slug
get_spec_dir() {
    local repo_root="$1"
    local slug="$2"
    echo "$repo_root/spec/$slug"
}

# Find spec directory by searching for existing bundles
find_spec_dir() {
    local repo_root="$1"
    local branch="$2"
    local slug
    slug="$(get_feature_slug "$branch")"
    local spec_dir="$repo_root/spec/$slug"

    if [[ -d "$spec_dir" ]]; then
        echo "$spec_dir"
        return
    fi

    # Try exact branch name match
    if [[ -d "$repo_root/spec/$branch" ]]; then
        echo "$repo_root/spec/$branch"
        return
    fi

    # Fallback to slug-based path (will be created)
    echo "$spec_dir"
}

# Export all feature paths as shell variables
get_feature_paths() {
    local repo_root
    repo_root="$(get_repo_root)"
    local current_branch
    current_branch="$(get_current_branch)"
    local has_git_repo="false"
    has_git && has_git_repo="true"

    local slug
    slug="$(get_feature_slug "$current_branch")"
    local feature_dir
    feature_dir="$(find_spec_dir "$repo_root" "$current_branch")"

    cat <<EOF
REPO_ROOT='$repo_root'
CURRENT_BRANCH='$current_branch'
HAS_GIT='$has_git_repo'
FEATURE_SLUG='$slug'
FEATURE_DIR='$feature_dir'
FEATURE_SPEC='$feature_dir/prd.md'
IMPL_PLAN='$feature_dir/plan.md'
TASKS='$feature_dir/tasks.md'
CONSTITUTION='$feature_dir/constitution.md'
RESEARCH='$feature_dir/research.md'
CHECKLIST='$feature_dir/checklist.md'
SPECS_DIR='$repo_root/spec'
TEMPLATES_DIR='$repo_root/.specify/templates'
EOF
}

check_file() { [[ -f "$1" ]] && echo "  ✓ $2" || echo "  ✗ $2"; }
check_dir() { [[ -d "$1" && -n $(ls -A "$1" 2>/dev/null) ]] && echo "  ✓ $2" || echo "  ✗ $2"; }

die() {
    echo "[spec-kit] FAIL: $*" >&2
    exit 1
}

warn() {
    echo "[spec-kit] WARN: $*" >&2
}
