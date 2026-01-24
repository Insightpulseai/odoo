#!/usr/bin/env bash
# ============================================================================
# Spec-Kit Bundle Validator
#
# Validates that all spec bundles contain required files:
# - constitution.md
# - prd.md
# - plan.md
# - tasks.md
#
# Also validates PRD structure with required sections.
# ============================================================================
set -euo pipefail

SPEC_DIR="${SPEC_DIR:-spec}"
REQUIRED_FILES="constitution.md prd.md plan.md tasks.md"

die() {
  echo "[spec-kit] FAIL: $*" >&2
  exit 1
}

warn() {
  echo "[spec-kit] WARN: $*" >&2
}

# Check spec directory exists
if [ ! -d "$SPEC_DIR" ]; then
  die "Missing $SPEC_DIR/ directory"
fi

# Count spec bundles
bundle_count=0
missing_count=0
invalid_prd_count=0

# Find all spec bundle directories (subdirectories of spec/)
for d in "$SPEC_DIR"/*/; do
  [ -d "$d" ] || continue

  bundle_name=$(basename "$d")
  bundle_count=$((bundle_count + 1))

  echo "[spec-kit] Checking bundle: $bundle_name"

  # Check for required files
  for f in $REQUIRED_FILES; do
    filepath="$d$f"
    if [ ! -f "$filepath" ]; then
      echo "  - Missing: $f"
      missing_count=$((missing_count + 1))
    elif [ ! -s "$filepath" ]; then
      echo "  - Empty: $f"
      missing_count=$((missing_count + 1))
    else
      echo "  - Found: $f"
    fi
  done

  # Validate PRD structure (optional but recommended)
  prd_file="$d/prd.md"
  if [ -f "$prd_file" ] && [ -s "$prd_file" ]; then
    # Check for recommended sections (warn if missing, don't fail)
    if ! grep -qE '^##\s+(Problem|Overview|Problem Alignment)' "$prd_file" 2>/dev/null; then
      warn "PRD missing problem section: $bundle_name/prd.md"
    fi
    if ! grep -qE '^##\s+(Solution|Solution Alignment|Architecture)' "$prd_file" 2>/dev/null; then
      warn "PRD missing solution section: $bundle_name/prd.md"
    fi
  fi
done

if [ "$bundle_count" -eq 0 ]; then
  die "No spec bundles found in $SPEC_DIR/"
fi

echo ""
echo "[spec-kit] Summary:"
echo "  - Bundles checked: $bundle_count"
echo "  - Missing/empty files: $missing_count"

if [ "$missing_count" -gt 0 ]; then
  die "Spec-kit validation failed: $missing_count missing or empty files"
fi

echo "[spec-kit] OK"
