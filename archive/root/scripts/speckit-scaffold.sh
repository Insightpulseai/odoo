#!/usr/bin/env bash
# ============================================================================
# Spec-Kit Bundle Scaffold
#
# Creates a new spec bundle from templates.
#
# Usage:
#   ./scripts/speckit-scaffold.sh <feature-slug>
#
# Example:
#   ./scripts/speckit-scaffold.sh ipai-finance-ppm
#
# Creates:
#   spec/<feature-slug>/
#   ├── constitution.md
#   ├── prd.md
#   ├── plan.md
#   └── tasks.md
# ============================================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SPEC_DIR="$REPO_ROOT/spec"
TEMPLATE_DIR="$REPO_ROOT/.specify/templates"

usage() {
  echo "Usage: $0 <feature-slug>"
  echo ""
  echo "Creates a new spec bundle from templates."
  echo ""
  echo "Examples:"
  echo "  $0 ipai-finance-ppm"
  echo "  $0 odoo-19-migration"
  exit 1
}

die() {
  echo "[speckit-scaffold] FAIL: $*" >&2
  exit 1
}

# Validate arguments
[ $# -eq 1 ] || usage
SLUG="$1"

# Validate slug format (lowercase, hyphens, no special chars)
if ! echo "$SLUG" | grep -qE '^[a-z0-9][a-z0-9-]*[a-z0-9]$'; then
  die "Invalid slug '$SLUG'. Use lowercase alphanumeric with hyphens (e.g., 'my-feature')."
fi

BUNDLE_DIR="$SPEC_DIR/$SLUG"

# Check if bundle already exists
if [ -d "$BUNDLE_DIR" ]; then
  die "Bundle already exists: $BUNDLE_DIR"
fi

# Check templates exist
if [ ! -d "$TEMPLATE_DIR" ]; then
  die "Template directory missing: $TEMPLATE_DIR"
fi

# Create bundle directory
mkdir -p "$BUNDLE_DIR"

# Copy and customize templates
DATE=$(date +%Y-%m-%d)
FEATURE_TITLE=$(echo "$SLUG" | sed 's/-/ /g' | sed 's/\b\(.\)/\u\1/g')

for template in constitution spec plan tasks; do
  src="$TEMPLATE_DIR/${template}-template.md"
  case "$template" in
    spec) dst="$BUNDLE_DIR/prd.md" ;;
    *)    dst="$BUNDLE_DIR/${template}.md" ;;
  esac

  if [ -f "$src" ]; then
    sed \
      -e "s/\[FEATURE NAME\]/$FEATURE_TITLE/g" \
      -e "s/\[FEATURE_SLUG\]/$SLUG/g" \
      -e "s/\[PROJECT NAME\]/$FEATURE_TITLE/g" \
      -e "s/\[DATE\]/$DATE/g" \
      "$src" > "$dst"
    echo "[speckit-scaffold] Created: $dst"
  else
    echo "[speckit-scaffold] WARN: Template missing: $src"
    touch "$dst"
  fi
done

echo ""
echo "[speckit-scaffold] Bundle created: $BUNDLE_DIR/"
echo ""
echo "Next steps:"
echo "  /speckit.constitution $SLUG"
echo "  /speckit.specify $SLUG"
echo "  /speckit.plan $SLUG"
echo "  /speckit.tasks $SLUG"
