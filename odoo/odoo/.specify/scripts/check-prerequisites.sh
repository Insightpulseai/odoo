#!/usr/bin/env bash
# Check prerequisites for spec-kit workflow phases.
#
# Usage:
#   ./check-prerequisites.sh [OPTIONS]
#
# OPTIONS:
#   --json              Output in JSON format
#   --require-tasks     Require tasks.md to exist (for implementation phase)
#   --paths-only        Only output path variables (no validation)
#   --slug <name>       Override feature slug (instead of deriving from branch)
#
# OUTPUTS:
#   JSON: {"FEATURE_DIR":"...","AVAILABLE_DOCS":["..."]}
#   Text: FEATURE_DIR:... \n AVAILABLE_DOCS: \n ✓/✗ file.md

set -euo pipefail

JSON_MODE=false
REQUIRE_TASKS=false
PATHS_ONLY=false
SLUG_OVERRIDE=""

for arg in "$@"; do
    case "$arg" in
        --json) JSON_MODE=true ;;
        --require-tasks) REQUIRE_TASKS=true ;;
        --paths-only) PATHS_ONLY=true ;;
        --slug)
            shift
            SLUG_OVERRIDE="$1"
            ;;
        --help|-h)
            echo "Usage: $0 [--json] [--require-tasks] [--paths-only] [--slug <name>]"
            exit 0
            ;;
    esac
done

SCRIPT_DIR="$(CDPATH="" cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

eval "$(get_feature_paths)"

# Override slug if provided
if [[ -n "$SLUG_OVERRIDE" ]]; then
    FEATURE_SLUG="$SLUG_OVERRIDE"
    FEATURE_DIR="$(get_spec_dir "$REPO_ROOT" "$SLUG_OVERRIDE")"
    FEATURE_SPEC="$FEATURE_DIR/prd.md"
    IMPL_PLAN="$FEATURE_DIR/plan.md"
    TASKS="$FEATURE_DIR/tasks.md"
    CONSTITUTION="$FEATURE_DIR/constitution.md"
    RESEARCH="$FEATURE_DIR/research.md"
    CHECKLIST="$FEATURE_DIR/checklist.md"
fi

# Paths-only mode
if $PATHS_ONLY; then
    if $JSON_MODE; then
        printf '{"REPO_ROOT":"%s","BRANCH":"%s","FEATURE_SLUG":"%s","FEATURE_DIR":"%s","FEATURE_SPEC":"%s","IMPL_PLAN":"%s","TASKS":"%s","CONSTITUTION":"%s"}\n' \
            "$REPO_ROOT" "$CURRENT_BRANCH" "$FEATURE_SLUG" "$FEATURE_DIR" "$FEATURE_SPEC" "$IMPL_PLAN" "$TASKS" "$CONSTITUTION"
    else
        echo "REPO_ROOT: $REPO_ROOT"
        echo "BRANCH: $CURRENT_BRANCH"
        echo "FEATURE_SLUG: $FEATURE_SLUG"
        echo "FEATURE_DIR: $FEATURE_DIR"
        echo "FEATURE_SPEC: $FEATURE_SPEC"
        echo "IMPL_PLAN: $IMPL_PLAN"
        echo "TASKS: $TASKS"
        echo "CONSTITUTION: $CONSTITUTION"
    fi
    exit 0
fi

# Validate feature directory
if [[ ! -d "$FEATURE_DIR" ]]; then
    die "Feature directory not found: $FEATURE_DIR. Run /speckit.specify first."
fi

# Validate plan exists
if [[ ! -f "$IMPL_PLAN" ]]; then
    die "plan.md not found in $FEATURE_DIR. Run /speckit.plan first."
fi

# Validate tasks if required
if $REQUIRE_TASKS && [[ ! -f "$TASKS" ]]; then
    die "tasks.md not found in $FEATURE_DIR. Run /speckit.tasks first."
fi

# Build available docs list
docs=()
[[ -f "$CONSTITUTION" ]] && docs+=("constitution.md")
[[ -f "$FEATURE_SPEC" ]] && docs+=("prd.md")
# Accept spec.md as alternative
[[ ! -f "$FEATURE_SPEC" && -f "$FEATURE_DIR/spec.md" ]] && docs+=("spec.md")
[[ -f "$RESEARCH" ]] && docs+=("research.md")
[[ -f "$CHECKLIST" ]] && docs+=("checklist.md")
[[ -f "$TASKS" ]] && docs+=("tasks.md")

if $JSON_MODE; then
    if [[ ${#docs[@]} -eq 0 ]]; then
        json_docs="[]"
    else
        json_docs=$(printf '"%s",' "${docs[@]}")
        json_docs="[${json_docs%,}]"
    fi
    printf '{"FEATURE_DIR":"%s","FEATURE_SLUG":"%s","AVAILABLE_DOCS":%s}\n' \
        "$FEATURE_DIR" "$FEATURE_SLUG" "$json_docs"
else
    echo "FEATURE_DIR: $FEATURE_DIR"
    echo "FEATURE_SLUG: $FEATURE_SLUG"
    echo "AVAILABLE_DOCS:"
    check_file "$CONSTITUTION" "constitution.md"
    check_file "$FEATURE_SPEC" "prd.md"
    check_file "$IMPL_PLAN" "plan.md"
    check_file "$TASKS" "tasks.md"
    check_file "$RESEARCH" "research.md"
    check_file "$CHECKLIST" "checklist.md"
fi
