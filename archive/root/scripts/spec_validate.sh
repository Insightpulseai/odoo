#!/usr/bin/env bash
# =============================================================================
# Spec Kit Validation Script
# Validates spec bundles follow the required structure and content standards.
#
# Usage:
#   ./scripts/spec_validate.sh           # Validate all bundles
#   ./scripts/spec_validate.sh --strict  # Fail on warnings too
# =============================================================================
set -euo pipefail

STRICT="${1:-}"
fail=0
warn=0

echo "== Spec Kit Validation =="

# Check spec/ directory exists
if [ ! -d "spec" ]; then
  echo "INFO: No spec/ directory found"
  exit 0
fi

# Find all spec bundles (directories with constitution.md)
bundles=$(find spec -mindepth 2 -maxdepth 2 -type f -name constitution.md -print 2>/dev/null | wc -l | tr -d ' ')
if [ "$bundles" -lt 1 ]; then
  echo "INFO: No spec bundles found (expected spec/<slug>/constitution.md)"
  exit 0
fi

echo "Found $bundles spec bundle(s)"
echo ""

# Validate each bundle
while IFS= read -r cfile; do
  slug_dir="$(dirname "$cfile")"
  slug_name="$(basename "$slug_dir")"

  echo "Validating bundle: $slug_name"

  # Check required files
  for f in constitution.md prd.md plan.md tasks.md; do
    path="$slug_dir/$f"
    if [ ! -f "$path" ]; then
      echo "  ERROR: Missing $f"
      fail=1
      continue
    fi

    # Check minimum content
    non_empty="$(grep -Ev '^\s*$' "$path" | wc -l | tr -d ' ')"
    if [ "$non_empty" -lt 10 ]; then
      echo "  ERROR: $f too small ($non_empty lines, need >=10)"
      fail=1
    else
      echo "  OK: $f ($non_empty lines)"
    fi

    # Check for placeholders (warning)
    if grep -Eqi '(TODO|TBD|PLACEHOLDER|FILL\s+ME\s+IN|LOREM\s+IPSUM)' "$path"; then
      echo "  WARN: $f contains placeholders"
      warn=1
    fi
  done

  # Check for optional capability-registry.yaml
  if [ -f "$slug_dir/capability-registry.yaml" ]; then
    echo "  OK: capability-registry.yaml found"
    # Validate YAML syntax
    if ! python3 -c "import yaml; yaml.safe_load(open('$slug_dir/capability-registry.yaml'))" 2>/dev/null; then
      echo "  ERROR: capability-registry.yaml has invalid YAML syntax"
      fail=1
    fi
  fi

  echo ""
done < <(find spec -mindepth 2 -maxdepth 2 -type f -name constitution.md -print 2>/dev/null)

# Check CLAUDE.md
if [ -f "CLAUDE.md" ]; then
  echo "OK: CLAUDE.md exists"
else
  echo "ERROR: Missing CLAUDE.md"
  fail=1
fi

# Check .claude directory
if [ -d ".claude" ]; then
  echo "OK: .claude/ directory exists"

  if [ -f ".claude/settings.json" ] || [ -f ".claude/settings.local.json" ]; then
    echo "OK: Claude settings found"
  else
    echo "WARN: No .claude/settings.json or .claude/settings.local.json"
    warn=1
  fi
else
  echo "WARN: Missing .claude/ directory"
  warn=1
fi

# Check verification scripts
if [ -f "scripts/verify.sh" ] || [ -f "scripts/ci_local.sh" ]; then
  echo "OK: Verification script found"
else
  echo "WARN: No verification script (scripts/verify.sh or scripts/ci_local.sh)"
  warn=1
fi

echo ""
echo "== Validation Summary =="
echo "Errors: $fail"
echo "Warnings: $warn"

if [ "$STRICT" == "--strict" ] && [ "$warn" -gt 0 ]; then
  echo "FAIL: Strict mode enabled and warnings found"
  exit 1
fi

if [ "$fail" -gt 0 ]; then
  echo "FAIL: Validation errors found"
  exit 1
fi

echo "PASS: All checks passed"
exit 0
