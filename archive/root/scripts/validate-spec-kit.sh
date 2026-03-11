#!/usr/bin/env bash
# =============================================================================
# Spec Kit Validation Script (All-Green Gate)
# Validates spec bundles follow the required structure and content standards.
#
# Usage:
#   ./scripts/validate-spec-kit.sh           # Validate all bundles
#   ./scripts/validate-spec-kit.sh --strict  # Fail on warnings too
#   ./scripts/validate-spec-kit.sh <slug>    # Validate specific bundle
#
# Exit codes:
#   0 - All checks passed
#   1 - Errors found (spec kit invalid)
#   2 - Warnings found (--strict mode)
# =============================================================================
set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Parse arguments
STRICT=false
TARGET_SLUG=""
for arg in "$@"; do
  case $arg in
    --strict)
      STRICT=true
      ;;
    --help|-h)
      echo "Usage: $0 [--strict] [<slug>]"
      echo ""
      echo "Options:"
      echo "  --strict    Fail on warnings"
      echo "  <slug>      Validate specific spec bundle"
      exit 0
      ;;
    *)
      TARGET_SLUG="$arg"
      ;;
  esac
done

# Counters
errors=0
warnings=0
bundles_checked=0

echo "== Spec Kit Validation =="
echo ""

# Check spec/ directory exists
if [ ! -d "spec" ]; then
  echo -e "${YELLOW}INFO: No spec/ directory found${NC}"
  exit 0
fi

# Required files for each bundle
REQUIRED_FILES=("constitution.md" "prd.md" "plan.md" "tasks.md")

# Placeholder patterns to detect
PLACEHOLDER_PATTERNS="TODO|TBD|PLACEHOLDER|LOREM|FILL.?ME.?IN|\\[INSERT\\]|XXX"

# Minimum content lines
MIN_LINES=10

# Function to validate a single bundle
validate_bundle() {
  local slug_dir="$1"
  local slug_name
  slug_name=$(basename "$slug_dir")

  echo "Checking: $slug_name"
  local bundle_errors=0
  local bundle_warnings=0

  # Check required files
  for file in "${REQUIRED_FILES[@]}"; do
    local path="${slug_dir}/${file}"

    if [ ! -f "$path" ]; then
      echo -e "  ${RED}ERROR: Missing ${file}${NC}"
      bundle_errors=$((bundle_errors + 1))
      continue
    fi

    # Check minimum content
    local non_empty
    non_empty=$(grep -Ev '^\s*$' "$path" | grep -Ev '^\s*#' | wc -l | tr -d ' ')

    if [ "$non_empty" -lt "$MIN_LINES" ]; then
      echo -e "  ${RED}ERROR: ${file} too small (${non_empty} lines, need ≥${MIN_LINES})${NC}"
      bundle_errors=$((bundle_errors + 1))
    else
      echo -e "  ${GREEN}OK: ${file} (${non_empty} lines)${NC}"
    fi

    # Check for placeholders
    if grep -Eqi "$PLACEHOLDER_PATTERNS" "$path" 2>/dev/null; then
      local matches
      matches=$(grep -Eic "$PLACEHOLDER_PATTERNS" "$path" 2>/dev/null || echo "0")
      echo -e "  ${YELLOW}WARN: ${file} contains placeholders (${matches} matches)${NC}"
      bundle_warnings=$((bundle_warnings + 1))
    fi
  done

  # Check for capability-registry.yaml (optional but validate if present)
  if [ -f "${slug_dir}/capability-registry.yaml" ]; then
    if python3 -c "import yaml; yaml.safe_load(open('${slug_dir}/capability-registry.yaml'))" 2>/dev/null; then
      echo -e "  ${GREEN}OK: capability-registry.yaml (valid YAML)${NC}"
    else
      echo -e "  ${RED}ERROR: capability-registry.yaml has invalid YAML syntax${NC}"
      bundle_errors=$((bundle_errors + 1))
    fi
  fi

  # Check for api-contract.yaml (optional but validate if present)
  if [ -f "${slug_dir}/api-contract.yaml" ]; then
    if python3 -c "import yaml; yaml.safe_load(open('${slug_dir}/api-contract.yaml'))" 2>/dev/null; then
      echo -e "  ${GREEN}OK: api-contract.yaml (valid YAML)${NC}"
    else
      echo -e "  ${RED}ERROR: api-contract.yaml has invalid YAML syntax${NC}"
      bundle_errors=$((bundle_errors + 1))
    fi
  fi

  # Constitution-specific checks
  if [ -f "${slug_dir}/constitution.md" ]; then
    if ! grep -qi "non.?negotiable\|invariant\|MUST" "${slug_dir}/constitution.md" 2>/dev/null; then
      echo -e "  ${YELLOW}WARN: constitution.md missing Non-Negotiables section${NC}"
      bundle_warnings=$((bundle_warnings + 1))
    fi
  fi

  # Tasks-specific checks
  if [ -f "${slug_dir}/tasks.md" ]; then
    if ! grep -q '\- \[' "${slug_dir}/tasks.md" 2>/dev/null; then
      echo -e "  ${YELLOW}WARN: tasks.md has no checkbox items${NC}"
      bundle_warnings=$((bundle_warnings + 1))
    fi
  fi

  # Plan-specific checks
  if [ -f "${slug_dir}/plan.md" ]; then
    if ! grep -qi "file\|verif" "${slug_dir}/plan.md" 2>/dev/null; then
      echo -e "  ${YELLOW}WARN: plan.md missing Files to Change or Verification sections${NC}"
      bundle_warnings=$((bundle_warnings + 1))
    fi
  fi

  errors=$((errors + bundle_errors))
  warnings=$((warnings + bundle_warnings))
  bundles_checked=$((bundles_checked + 1))

  echo ""
}

# Find and validate bundles
if [ -n "$TARGET_SLUG" ]; then
  # Validate specific bundle
  if [ -d "spec/${TARGET_SLUG}" ]; then
    validate_bundle "spec/${TARGET_SLUG}"
  else
    echo -e "${RED}ERROR: spec/${TARGET_SLUG} not found${NC}"
    exit 1
  fi
else
  # Validate all bundles (directories with constitution.md)
  while IFS= read -r cfile; do
    slug_dir=$(dirname "$cfile")
    validate_bundle "$slug_dir"
  done < <(find spec -mindepth 2 -maxdepth 2 -type f -name constitution.md -print 2>/dev/null | sort)
fi

# Check CLAUDE.md exists
echo "== Repository Checks =="
if [ -f "CLAUDE.md" ]; then
  echo -e "${GREEN}OK: CLAUDE.md exists${NC}"
else
  echo -e "${RED}ERROR: Missing CLAUDE.md${NC}"
  errors=$((errors + 1))
fi

# Check .continue directory
if [ -d ".continue" ]; then
  echo -e "${GREEN}OK: .continue/ directory exists${NC}"

  # Check config.json
  if [ -f ".continue/config.json" ]; then
    if python3 -c "import json; json.load(open('.continue/config.json'))" 2>/dev/null; then
      echo -e "${GREEN}OK: .continue/config.json (valid JSON)${NC}"
    else
      echo -e "${RED}ERROR: .continue/config.json has invalid JSON syntax${NC}"
      errors=$((errors + 1))
    fi
  else
    echo -e "${YELLOW}WARN: Missing .continue/config.json${NC}"
    warnings=$((warnings + 1))
  fi

  # Check rules directory
  if [ -d ".continue/rules" ]; then
    rule_count=$(find .continue/rules -type f \( -name "*.yaml" -o -name "*.yml" -o -name "*.md" \) 2>/dev/null | wc -l | tr -d ' ')
    echo -e "${GREEN}OK: .continue/rules/ has ${rule_count} rule files${NC}"
  else
    echo -e "${YELLOW}WARN: Missing .continue/rules/ directory${NC}"
    warnings=$((warnings + 1))
  fi
else
  echo -e "${YELLOW}WARN: Missing .continue/ directory${NC}"
  warnings=$((warnings + 1))
fi

echo ""
echo "== Validation Summary =="
echo "Bundles checked: $bundles_checked"
echo -e "Errors: ${errors}"
echo -e "Warnings: ${warnings}"

# Exit with appropriate code
if [ "$errors" -gt 0 ]; then
  echo ""
  echo -e "${RED}FAIL: Validation errors found${NC}"
  exit 1
fi

if [ "$STRICT" = true ] && [ "$warnings" -gt 0 ]; then
  echo ""
  echo -e "${YELLOW}FAIL: Strict mode enabled and warnings found${NC}"
  exit 2
fi

echo ""
echo -e "${GREEN}PASS: All checks passed${NC}"
exit 0
