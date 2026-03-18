#!/usr/bin/env bash
# Create a new spec bundle for a feature.
#
# Usage:
#   ./create-new-feature.sh [--json] <feature-slug>
#
# Creates:
#   spec/<feature-slug>/
#   ├── constitution.md  (from template)
#   ├── prd.md           (from template)
#   ├── plan.md          (from template)
#   └── tasks.md         (from template)

set -euo pipefail

JSON_MODE=false
SLUG=""

for arg in "$@"; do
    case "$arg" in
        --json) JSON_MODE=true ;;
        --help|-h)
            echo "Usage: $0 [--json] <feature-slug>"
            exit 0
            ;;
        *) SLUG="$arg" ;;
    esac
done

if [[ -z "$SLUG" ]]; then
    echo "Usage: $0 [--json] <feature-slug>" >&2
    exit 1
fi

SCRIPT_DIR="$(CDPATH="" cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

REPO_ROOT="$(get_repo_root)"
SPEC_DIR="$REPO_ROOT/spec/$SLUG"
TEMPLATE_DIR="$REPO_ROOT/.specify/templates"

# Validate slug
if ! echo "$SLUG" | grep -qE '^[a-z0-9][a-z0-9-]*[a-z0-9]$'; then
    die "Invalid slug '$SLUG'. Use lowercase alphanumeric with hyphens."
fi

if [[ -d "$SPEC_DIR" ]]; then
    die "Bundle already exists: $SPEC_DIR"
fi

mkdir -p "$SPEC_DIR"

DATE=$(date +%Y-%m-%d)
FEATURE_TITLE=$(echo "$SLUG" | sed 's/-/ /g' | sed 's/\b\(.\)/\u\1/g')

for template in constitution spec plan tasks; do
    src="$TEMPLATE_DIR/${template}-template.md"
    case "$template" in
        spec) dst="$SPEC_DIR/prd.md" ;;
        *)    dst="$SPEC_DIR/${template}.md" ;;
    esac

    if [[ -f "$src" ]]; then
        sed \
            -e "s/\[FEATURE NAME\]/$FEATURE_TITLE/g" \
            -e "s/\[FEATURE_SLUG\]/$SLUG/g" \
            -e "s/\[PROJECT NAME\]/$FEATURE_TITLE/g" \
            -e "s/\[DATE\]/$DATE/g" \
            "$src" > "$dst"
    else
        touch "$dst"
    fi
done

export SPECIFY_FEATURE="$SLUG"

if $JSON_MODE; then
    printf '{"FEATURE_SLUG":"%s","SPEC_DIR":"%s","PRD_FILE":"%s"}\n' \
        "$SLUG" "$SPEC_DIR" "$SPEC_DIR/prd.md"
else
    echo "FEATURE_SLUG: $SLUG"
    echo "SPEC_DIR: $SPEC_DIR"
    echo "PRD_FILE: $SPEC_DIR/prd.md"
fi
