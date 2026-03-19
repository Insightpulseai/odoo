#!/usr/bin/env bash
# Set up the plan.md for a feature, copying from template if needed.
#
# Usage:
#   ./setup-plan.sh [--json] [--slug <name>]

set -euo pipefail

JSON_MODE=false
SLUG_OVERRIDE=""
i=1
while [ $i -le $# ]; do
    arg="${!i}"
    case "$arg" in
        --json) JSON_MODE=true ;;
        --slug)
            i=$((i + 1))
            SLUG_OVERRIDE="${!i}"
            ;;
        --help|-h)
            echo "Usage: $0 [--json] [--slug <name>]"
            exit 0
            ;;
    esac
    i=$((i + 1))
done

SCRIPT_DIR="$(CDPATH="" cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

eval "$(get_feature_paths)"

if [[ -n "$SLUG_OVERRIDE" ]]; then
    FEATURE_SLUG="$SLUG_OVERRIDE"
    FEATURE_DIR="$(get_spec_dir "$REPO_ROOT" "$SLUG_OVERRIDE")"
    FEATURE_SPEC="$FEATURE_DIR/prd.md"
    IMPL_PLAN="$FEATURE_DIR/plan.md"
fi

if [[ ! -d "$FEATURE_DIR" ]]; then
    die "Feature directory not found: $FEATURE_DIR"
fi

# Copy plan template if plan doesn't exist yet
TEMPLATE="$REPO_ROOT/.specify/templates/plan-template.md"
if [[ ! -f "$IMPL_PLAN" ]]; then
    if [[ -f "$TEMPLATE" ]]; then
        cp "$TEMPLATE" "$IMPL_PLAN"
    else
        touch "$IMPL_PLAN"
    fi
fi

if $JSON_MODE; then
    printf '{"FEATURE_SPEC":"%s","IMPL_PLAN":"%s","SPECS_DIR":"%s","BRANCH":"%s","HAS_GIT":"%s"}\n' \
        "$FEATURE_SPEC" "$IMPL_PLAN" "$FEATURE_DIR" "$CURRENT_BRANCH" "$HAS_GIT"
else
    echo "FEATURE_SPEC: $FEATURE_SPEC"
    echo "IMPL_PLAN: $IMPL_PLAN"
    echo "SPECS_DIR: $FEATURE_DIR"
    echo "BRANCH: $CURRENT_BRANCH"
    echo "HAS_GIT: $HAS_GIT"
fi
