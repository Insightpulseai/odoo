#!/usr/bin/env bash
# =============================================================================
# Model Repo Scanner - Adopt Baseline Automation
# =============================================================================
# Generates a patch set to adopt baseline automation from a model repository
# into a target repository. Creates a branch with the necessary changes.
#
# Usage:
#   ./scripts/adopt_model_repo.sh <target-repo-path> [options]
#
# Options:
#   -m, --model <repo>    Model repo to copy from (default: auto-detect from scores)
#   -b, --branch <name>   Branch name (default: adopt-model-automation)
#   -n, --dry-run         Show what would be copied without making changes
#   -h, --help            Show help
#
# Output:
#   Creates branch with baseline automation files
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Defaults
ARTIFACTS_DIR="${BASE_DIR}/artifacts"
CACHE_DIR="${BASE_DIR}/.cache/repos"
BRANCH_NAME="adopt-model-automation"
MODEL_REPO=""
DRY_RUN=false

# =============================================================================
# Functions
# =============================================================================
log() { echo -e "${BLUE}[INFO]${NC} $*"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*" >&2; }

show_help() {
    cat << 'EOF'
Model Repo Scanner - Adopt Baseline Automation

USAGE:
    adopt_model_repo.sh <target-repo-path> [options]

OPTIONS:
    -m, --model <repo>    Model repo to copy from (default: auto-detect)
    -b, --branch <name>   Branch name (default: adopt-model-automation)
    -n, --dry-run         Show what would be copied without making changes
    -h, --help            Show help

EXAMPLE:
    # Adopt automation from top-scored model repo
    ./scripts/adopt_model_repo.sh /path/to/my-repo

    # Adopt from specific model repo
    ./scripts/adopt_model_repo.sh /path/to/my-repo -m odoo-ce
EOF
}

get_top_model_repo() {
    if [[ -f "${ARTIFACTS_DIR}/model-repo-scores.json" ]]; then
        jq -r 'sort_by(-.total_score) | .[0].repo' "${ARTIFACTS_DIR}/model-repo-scores.json"
    else
        echo ""
    fi
}

# Files to adopt from model repo
ADOPT_FILES=(
    # CI Scripts
    "scripts/ci/run_all.sh"
    "scripts/verify.sh"
    "scripts/repo_health.sh"

    # GitHub workflows
    ".github/workflows/ci.yml"
    ".github/workflows/repo-structure.yml"

    # Governance
    ".github/pull_request_template.md"
    ".github/ISSUE_TEMPLATE/bug_report.md"
    ".github/ISSUE_TEMPLATE/feature_request.md"

    # Spec Kit base
    "spec/README.md"

    # Claude config
    ".claude/settings.json"
)

# Template files to generate (not copy)
generate_codeowners() {
    local target="$1"
    cat > "$target/CODEOWNERS" << 'EOF'
# Default code owners
* @maintainers

# CI/CD
.github/ @platform-team
scripts/ @platform-team

# Documentation
docs/ @docs-team
*.md @docs-team
EOF
}

generate_spec_template() {
    local target="$1"
    mkdir -p "$target/spec/_template"

    cat > "$target/spec/_template/constitution.md" << 'EOF'
# Constitution

## Non-Negotiables

1. [Define critical constraints]
2. [Define security requirements]
3. [Define compliance requirements]

## Governance

- Owner: [team/person]
- Reviewers: [list]
- Approval: [process]
EOF

    cat > "$target/spec/_template/prd.md" << 'EOF'
# Product Requirements Document

## Overview

[Brief description]

## Goals

1. [Goal 1]
2. [Goal 2]

## Requirements

### Functional

- [ ] [Requirement 1]
- [ ] [Requirement 2]

### Non-Functional

- [ ] Performance: [target]
- [ ] Security: [requirements]
EOF

    cat > "$target/spec/_template/plan.md" << 'EOF'
# Implementation Plan

## Phases

### Phase 1: [Name]

- [ ] Task 1
- [ ] Task 2

### Phase 2: [Name]

- [ ] Task 3
- [ ] Task 4

## Verification

- [ ] Tests pass
- [ ] CI green
- [ ] Documentation updated

## Rollback

[Describe rollback procedure]
EOF

    cat > "$target/spec/_template/tasks.md" << 'EOF'
# Tasks

## In Progress

- [ ] [Task description] (@assignee)

## Pending

- [ ] [Task description]

## Completed

- [x] [Task description] (completed: YYYY-MM-DD)
EOF
}

generate_ci_workflow() {
    local target="$1"
    mkdir -p "$target/.github/workflows"

    cat > "$target/.github/workflows/ci.yml" << 'EOF'
name: CI

on:
  push:
    branches: [main, master]
  pull_request:
    branches: [main, master]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run linters
        run: |
          echo "Add your lint commands here"
          # npm run lint
          # python -m flake8

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run tests
        run: |
          echo "Add your test commands here"
          # npm test
          # pytest

  build:
    runs-on: ubuntu-latest
    needs: [lint, test]
    steps:
      - uses: actions/checkout@v4

      - name: Build
        run: |
          echo "Add your build commands here"
          # npm run build
EOF
}

generate_pr_template() {
    local target="$1"
    mkdir -p "$target/.github"

    cat > "$target/.github/pull_request_template.md" << 'EOF'
## Summary
<!-- What changed and why? Keep it brief. -->

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Checklist
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] CI passes
EOF
}

adopt_file() {
    local model_path="$1"
    local target_path="$2"
    local file="$3"

    local source="${model_path}/${file}"
    local dest="${target_path}/${file}"

    if [[ ! -f "$source" ]]; then
        warn "Source file not found: $file"
        return 1
    fi

    if [[ -f "$dest" ]]; then
        warn "Target file exists, skipping: $file"
        return 0
    fi

    if [[ "$DRY_RUN" == "true" ]]; then
        echo "  Would copy: $file"
        return 0
    fi

    mkdir -p "$(dirname "$dest")"
    cp "$source" "$dest"
    log "Copied: $file"
}

# =============================================================================
# Main
# =============================================================================
main() {
    local target_path=""

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -m|--model)
                MODEL_REPO="$2"
                shift 2
                ;;
            -b|--branch)
                BRANCH_NAME="$2"
                shift 2
                ;;
            -n|--dry-run)
                DRY_RUN=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            -*)
                error "Unknown option: $1"
                show_help
                exit 1
                ;;
            *)
                if [[ -z "$target_path" ]]; then
                    target_path="$1"
                else
                    error "Unexpected argument: $1"
                    exit 1
                fi
                shift
                ;;
        esac
    done

    # Validate target path
    if [[ -z "$target_path" ]]; then
        error "Target repository path required"
        show_help
        exit 1
    fi

    if [[ ! -d "$target_path" ]]; then
        error "Target path does not exist: $target_path"
        exit 1
    fi

    if [[ ! -d "$target_path/.git" ]]; then
        error "Target path is not a git repository: $target_path"
        exit 1
    fi

    # Get model repo
    if [[ -z "$MODEL_REPO" ]]; then
        MODEL_REPO=$(get_top_model_repo)
        if [[ -z "$MODEL_REPO" ]]; then
            warn "No model repo scores found, using templates only"
        else
            log "Auto-detected model repo: $MODEL_REPO"
        fi
    fi

    local model_path="${CACHE_DIR}/${MODEL_REPO}"

    log "Adopting baseline automation"
    log "  Target: $target_path"
    log "  Model: ${MODEL_REPO:-templates}"
    log "  Branch: $BRANCH_NAME"
    [[ "$DRY_RUN" == "true" ]] && log "  Mode: DRY RUN"
    echo ""

    # Create branch
    if [[ "$DRY_RUN" != "true" ]]; then
        (
            cd "$target_path"
            git checkout -b "$BRANCH_NAME" 2>/dev/null || {
                warn "Branch $BRANCH_NAME already exists, switching to it"
                git checkout "$BRANCH_NAME"
            }
        )
    fi

    # Track what we're adding
    local added_files=()

    # Copy files from model repo if available
    if [[ -d "$model_path" ]]; then
        log "Copying files from model repo..."
        for file in "${ADOPT_FILES[@]}"; do
            if adopt_file "$model_path" "$target_path" "$file"; then
                added_files+=("$file")
            fi
        done
    fi

    # Generate template files
    log "Generating template files..."

    if [[ ! -f "$target_path/CODEOWNERS" ]] && [[ ! -f "$target_path/.github/CODEOWNERS" ]]; then
        if [[ "$DRY_RUN" == "true" ]]; then
            echo "  Would generate: CODEOWNERS"
        else
            generate_codeowners "$target_path"
            added_files+=("CODEOWNERS")
            log "Generated: CODEOWNERS"
        fi
    fi

    if [[ ! -d "$target_path/spec" ]]; then
        if [[ "$DRY_RUN" == "true" ]]; then
            echo "  Would generate: spec/_template/*"
        else
            generate_spec_template "$target_path"
            added_files+=("spec/_template/*")
            log "Generated: spec/_template/*"
        fi
    fi

    if [[ ! -f "$target_path/.github/workflows/ci.yml" ]]; then
        if [[ "$DRY_RUN" == "true" ]]; then
            echo "  Would generate: .github/workflows/ci.yml"
        else
            generate_ci_workflow "$target_path"
            added_files+=(".github/workflows/ci.yml")
            log "Generated: .github/workflows/ci.yml"
        fi
    fi

    if [[ ! -f "$target_path/.github/pull_request_template.md" ]]; then
        if [[ "$DRY_RUN" == "true" ]]; then
            echo "  Would generate: .github/pull_request_template.md"
        else
            generate_pr_template "$target_path"
            added_files+=(".github/pull_request_template.md")
            log "Generated: .github/pull_request_template.md"
        fi
    fi

    # Commit changes
    if [[ "$DRY_RUN" != "true" ]] && [[ ${#added_files[@]} -gt 0 ]]; then
        (
            cd "$target_path"
            git add .
            git commit -m "chore: adopt baseline automation from model repo

Added files:
$(printf '  - %s\n' "${added_files[@]}")

Generated by Model Repo Scanner
Model: ${MODEL_REPO:-templates}
"
        )
    fi

    # Summary
    echo ""
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}  Adoption Complete${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "Files added/generated: ${#added_files[@]}"
    echo ""

    if [[ "$DRY_RUN" != "true" ]]; then
        echo "Next steps:"
        echo "  1. Review changes: cd $target_path && git diff HEAD~1"
        echo "  2. Push branch: git push -u origin $BRANCH_NAME"
        echo "  3. Create PR for review"
    fi
}

main "$@"
