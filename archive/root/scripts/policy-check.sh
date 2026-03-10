#!/usr/bin/env bash
# =============================================================================
# Policy Check Script (All-Green Gate)
# Validates code changes comply with security and architectural policies.
#
# Usage:
#   ./scripts/policy-check.sh           # Check all policies
#   ./scripts/policy-check.sh --diff    # Check only changed files
#   ./scripts/policy-check.sh --fix     # Auto-fix where possible
#
# Exit codes:
#   0 - All checks passed
#   1 - Policy violations found
# =============================================================================
set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Parse arguments
DIFF_ONLY=false
AUTO_FIX=false
for arg in "$@"; do
  case $arg in
    --diff)
      DIFF_ONLY=true
      ;;
    --fix)
      AUTO_FIX=true
      ;;
    --help|-h)
      echo "Usage: $0 [--diff] [--fix]"
      echo ""
      echo "Options:"
      echo "  --diff    Check only changed files (git diff)"
      echo "  --fix     Auto-fix violations where possible"
      exit 0
      ;;
  esac
done

# Counters
errors=0
warnings=0
fixes=0

echo "== Policy Check =="
echo ""

# Get files to check
if [ "$DIFF_ONLY" = true ]; then
  echo "Mode: Checking changed files only"
  FILES=$(git diff --name-only HEAD~1 2>/dev/null || git diff --name-only --cached 2>/dev/null || find . -type f -name "*.py" -o -name "*.ts" -o -name "*.js" 2>/dev/null)
else
  echo "Mode: Checking all files"
  FILES=$(find . -type f \( -name "*.py" -o -name "*.ts" -o -name "*.js" -o -name "*.yaml" -o -name "*.yml" \) \
    -not -path "./node_modules/*" \
    -not -path "./.git/*" \
    -not -path "./dist/*" \
    -not -path "./.venv/*" \
    -not -path "./venv/*" \
    -not -path "./__pycache__/*" \
    2>/dev/null)
fi

echo ""

# =============================================================================
# POLICY 1: No Hardcoded Secrets
# =============================================================================
echo "== P1: No Hardcoded Secrets =="

SECRET_PATTERNS=(
  'API_KEY\s*=\s*["\x27][a-zA-Z0-9]'
  'SECRET\s*=\s*["\x27][a-zA-Z0-9]'
  'PASSWORD\s*=\s*["\x27][a-zA-Z0-9]'
  'TOKEN\s*=\s*["\x27][a-zA-Z0-9]'
  'NOTION_TOKEN\s*=\s*["\x27][^$]'
  'DATABRICKS_TOKEN\s*=\s*["\x27][^$]'
  'SUPABASE_SERVICE_ROLE_KEY\s*=\s*["\x27][^$]'
  'sk-[a-zA-Z0-9]{20,}'  # OpenAI-style keys
  'ghp_[a-zA-Z0-9]{36}'  # GitHub tokens
  'gho_[a-zA-Z0-9]{36}'  # GitHub OAuth tokens
)

secret_violations=0
for file in $FILES; do
  [ -f "$file" ] || continue
  # Skip .env files (expected to have secrets)
  [[ "$file" == *".env"* ]] && continue
  # Skip example files
  [[ "$file" == *".example"* ]] && continue
  [[ "$file" == *"_example"* ]] && continue

  for pattern in "${SECRET_PATTERNS[@]}"; do
    if grep -Eq "$pattern" "$file" 2>/dev/null; then
      echo -e "  ${RED}VIOLATION: $file contains potential hardcoded secret${NC}"
      echo -e "    Pattern: $pattern"
      secret_violations=$((secret_violations + 1))
    fi
  done
done

if [ "$secret_violations" -gt 0 ]; then
  echo -e "${RED}  Found $secret_violations potential secrets${NC}"
  errors=$((errors + secret_violations))
else
  echo -e "${GREEN}  PASS: No hardcoded secrets found${NC}"
fi

echo ""

# =============================================================================
# POLICY 2: No Enterprise Dependencies
# =============================================================================
echo "== P2: No Enterprise Dependencies =="

ENTERPRISE_PATTERNS=(
  'odoo.addons.enterprise'
  'from odoo.addons.hr_payroll'
  'from odoo.addons.sale_subscription'
  'from odoo.addons.helpdesk'
  'from odoo.addons.planning'
  'from odoo.addons.sign'
  'from odoo.addons.documents'
  '"license":\s*"OEEL-1"'
  "'license':\s*'OEEL-1'"
)

enterprise_violations=0
for file in $FILES; do
  [ -f "$file" ] || continue
  [[ "$file" != *".py" ]] && [[ "$file" != *"manifest"* ]] && continue

  for pattern in "${ENTERPRISE_PATTERNS[@]}"; do
    if grep -Eq "$pattern" "$file" 2>/dev/null; then
      echo -e "  ${RED}VIOLATION: $file has Enterprise dependency${NC}"
      echo -e "    Pattern: $pattern"
      enterprise_violations=$((enterprise_violations + 1))
    fi
  done
done

# Check __manifest__.py files specifically
for manifest in $(find addons -name "__manifest__.py" 2>/dev/null || true); do
  if grep -q "OEEL-1\|LGPL-EE" "$manifest" 2>/dev/null; then
    echo -e "  ${RED}VIOLATION: $manifest has Enterprise license${NC}"
    enterprise_violations=$((enterprise_violations + 1))
  fi
done

if [ "$enterprise_violations" -gt 0 ]; then
  echo -e "${RED}  Found $enterprise_violations Enterprise dependencies${NC}"
  errors=$((errors + enterprise_violations))
else
  echo -e "${GREEN}  PASS: No Enterprise dependencies found${NC}"
fi

echo ""

# =============================================================================
# POLICY 3: No odoo.com References
# =============================================================================
echo "== P3: No odoo.com References =="

odoo_com_violations=0
for file in $FILES; do
  [ -f "$file" ] || continue
  [[ "$file" == *".py" ]] || [[ "$file" == *".xml" ]] || [[ "$file" == *".js" ]] || continue

  if grep -Eq 'odoo\.com|apps\.odoo\.com' "$file" 2>/dev/null; then
    echo -e "  ${YELLOW}WARN: $file references odoo.com${NC}"
    odoo_com_violations=$((odoo_com_violations + 1))
  fi
done

if [ "$odoo_com_violations" -gt 0 ]; then
  echo -e "${YELLOW}  Found $odoo_com_violations odoo.com references${NC}"
  warnings=$((warnings + odoo_com_violations))
else
  echo -e "${GREEN}  PASS: No odoo.com references found${NC}"
fi

echo ""

# =============================================================================
# POLICY 4: Forbidden File Modifications
# =============================================================================
echo "== P4: Forbidden File Modifications =="

FORBIDDEN_PATHS=(
  ".git/"
  "node_modules/"
  ".env"
  "credentials.json"
  "serviceAccountKey.json"
)

forbidden_violations=0
if [ "$DIFF_ONLY" = true ]; then
  changed_files=$(git diff --name-only HEAD~1 2>/dev/null || echo "")

  for forbidden in "${FORBIDDEN_PATHS[@]}"; do
    if echo "$changed_files" | grep -q "$forbidden" 2>/dev/null; then
      echo -e "  ${RED}VIOLATION: Forbidden path modified: $forbidden${NC}"
      forbidden_violations=$((forbidden_violations + 1))
    fi
  done
fi

if [ "$forbidden_violations" -gt 0 ]; then
  echo -e "${RED}  Found $forbidden_violations forbidden modifications${NC}"
  errors=$((errors + forbidden_violations))
else
  echo -e "${GREEN}  PASS: No forbidden modifications${NC}"
fi

echo ""

# =============================================================================
# POLICY 5: Python Syntax Check
# =============================================================================
echo "== P5: Python Syntax Check =="

py_errors=0
for file in $(echo "$FILES" | grep '\.py$' || true); do
  [ -f "$file" ] || continue

  if ! python3 -m py_compile "$file" 2>/dev/null; then
    echo -e "  ${RED}VIOLATION: $file has Python syntax error${NC}"
    py_errors=$((py_errors + 1))
  fi
done

if [ "$py_errors" -gt 0 ]; then
  echo -e "${RED}  Found $py_errors Python syntax errors${NC}"
  errors=$((errors + py_errors))
else
  echo -e "${GREEN}  PASS: All Python files have valid syntax${NC}"
fi

echo ""

# =============================================================================
# POLICY 6: JSON/YAML Syntax Check
# =============================================================================
echo "== P6: JSON/YAML Syntax Check =="

config_errors=0

# Check JSON files
for file in $(echo "$FILES" | grep '\.json$' || true); do
  [ -f "$file" ] || continue

  if ! python3 -c "import json; json.load(open('$file'))" 2>/dev/null; then
    echo -e "  ${RED}VIOLATION: $file has invalid JSON${NC}"
    config_errors=$((config_errors + 1))
  fi
done

# Check YAML files
for file in $(echo "$FILES" | grep -E '\.ya?ml$' || true); do
  [ -f "$file" ] || continue

  if ! python3 -c "import yaml; yaml.safe_load(open('$file'))" 2>/dev/null; then
    echo -e "  ${RED}VIOLATION: $file has invalid YAML${NC}"
    config_errors=$((config_errors + 1))
  fi
done

if [ "$config_errors" -gt 0 ]; then
  echo -e "${RED}  Found $config_errors config syntax errors${NC}"
  errors=$((errors + config_errors))
else
  echo -e "${GREEN}  PASS: All config files have valid syntax${NC}"
fi

echo ""

# =============================================================================
# POLICY 7: No Debug Statements in Production Code
# =============================================================================
echo "== P7: No Debug Statements =="

DEBUG_PATTERNS=(
  'console\.log\('
  'print\('
  'debugger;'
  'pdb\.set_trace'
  'breakpoint\(\)'
  'import pdb'
)

debug_violations=0
for file in $FILES; do
  [ -f "$file" ] || continue
  # Skip test files
  [[ "$file" == *"test"* ]] && continue
  [[ "$file" == *"spec"* ]] && continue

  for pattern in "${DEBUG_PATTERNS[@]}"; do
    if grep -Eq "$pattern" "$file" 2>/dev/null; then
      matches=$(grep -Ec "$pattern" "$file" 2>/dev/null || echo "0")
      echo -e "  ${YELLOW}WARN: $file has debug statements ($matches matches)${NC}"
      debug_violations=$((debug_violations + matches))
    fi
  done
done

if [ "$debug_violations" -gt 0 ]; then
  echo -e "${YELLOW}  Found $debug_violations debug statements${NC}"
  warnings=$((warnings + debug_violations))
else
  echo -e "${GREEN}  PASS: No debug statements found${NC}"
fi

echo ""

# =============================================================================
# Summary
# =============================================================================
echo "== Policy Check Summary =="
echo "Errors: $errors"
echo "Warnings: $warnings"

if [ "$AUTO_FIX" = true ]; then
  echo "Fixes applied: $fixes"
fi

# Exit with appropriate code
if [ "$errors" -gt 0 ]; then
  echo ""
  echo -e "${RED}FAIL: Policy violations found${NC}"
  exit 1
fi

echo ""
echo -e "${GREEN}PASS: All policy checks passed${NC}"
exit 0
