#!/usr/bin/env bash
# =============================================================================
# Continue Configuration Validation Script
# Validates .continue/ directory follows Continue.dev best practices.
#
# Usage:
#   ./scripts/validate-continue-config.sh
#
# Exit codes:
#   0 - All checks passed
#   1 - Configuration errors found
# =============================================================================
set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

errors=0
warnings=0

echo "== Continue Configuration Validation =="
echo ""

# =============================================================================
# Check .continue directory exists
# =============================================================================
echo "== Directory Structure =="

if [ ! -d ".continue" ]; then
  echo -e "${RED}ERROR: Missing .continue/ directory${NC}"
  errors=$((errors + 1))
else
  echo -e "${GREEN}OK: .continue/ directory exists${NC}"
fi

# =============================================================================
# Check config.json
# =============================================================================
echo ""
echo "== config.json =="

CONFIG_FILE=".continue/config.json"

if [ ! -f "$CONFIG_FILE" ]; then
  echo -e "${RED}ERROR: Missing $CONFIG_FILE${NC}"
  errors=$((errors + 1))
else
  # Validate JSON syntax
  if ! python3 -c "import json; json.load(open('$CONFIG_FILE'))" 2>/dev/null; then
    echo -e "${RED}ERROR: $CONFIG_FILE has invalid JSON syntax${NC}"
    errors=$((errors + 1))
  else
    echo -e "${GREEN}OK: $CONFIG_FILE is valid JSON${NC}"

    # Check for $schema reference
    if grep -q '"\$schema"' "$CONFIG_FILE" 2>/dev/null; then
      echo -e "${GREEN}OK: $CONFIG_FILE has \$schema reference${NC}"
    else
      echo -e "${YELLOW}WARN: $CONFIG_FILE missing \$schema reference${NC}"
      warnings=$((warnings + 1))
    fi

    # Check for rules array
    if grep -q '"rules"' "$CONFIG_FILE" 2>/dev/null; then
      rule_count=$(python3 -c "import json; print(len(json.load(open('$CONFIG_FILE')).get('rules', [])))" 2>/dev/null || echo "0")
      echo -e "${GREEN}OK: $CONFIG_FILE has $rule_count rules defined${NC}"
    else
      echo -e "${YELLOW}WARN: $CONFIG_FILE has no rules defined${NC}"
      warnings=$((warnings + 1))
    fi

    # Check for contextProviders
    if grep -q '"contextProviders"' "$CONFIG_FILE" 2>/dev/null; then
      echo -e "${GREEN}OK: $CONFIG_FILE has contextProviders${NC}"
    else
      echo -e "${YELLOW}WARN: $CONFIG_FILE missing contextProviders${NC}"
      warnings=$((warnings + 1))
    fi

    # Check for slashCommands
    if grep -q '"slashCommands"' "$CONFIG_FILE" 2>/dev/null; then
      cmd_count=$(python3 -c "import json; print(len(json.load(open('$CONFIG_FILE')).get('slashCommands', [])))" 2>/dev/null || echo "0")
      echo -e "${GREEN}OK: $CONFIG_FILE has $cmd_count slashCommands${NC}"
    else
      echo -e "${YELLOW}WARN: $CONFIG_FILE has no slashCommands${NC}"
      warnings=$((warnings + 1))
    fi
  fi
fi

# =============================================================================
# Check rules directory
# =============================================================================
echo ""
echo "== Rules Directory =="

RULES_DIR=".continue/rules"

if [ ! -d "$RULES_DIR" ]; then
  echo -e "${YELLOW}WARN: Missing $RULES_DIR directory${NC}"
  warnings=$((warnings + 1))
else
  echo -e "${GREEN}OK: $RULES_DIR directory exists${NC}"

  # Count rule files
  yaml_count=$(find "$RULES_DIR" -type f \( -name "*.yaml" -o -name "*.yml" \) 2>/dev/null | wc -l | tr -d ' ')
  md_count=$(find "$RULES_DIR" -type f -name "*.md" 2>/dev/null | wc -l | tr -d ' ')

  echo -e "  YAML rules: $yaml_count"
  echo -e "  Markdown rules: $md_count"

  # Validate YAML rule files
  for rule_file in $(find "$RULES_DIR" -type f \( -name "*.yaml" -o -name "*.yml" \) 2>/dev/null); do
    if python3 -c "import yaml; yaml.safe_load(open('$rule_file'))" 2>/dev/null; then
      echo -e "  ${GREEN}OK: $(basename "$rule_file") is valid YAML${NC}"
    else
      echo -e "  ${RED}ERROR: $(basename "$rule_file") has invalid YAML${NC}"
      errors=$((errors + 1))
    fi
  done

  # Check for required rule files
  REQUIRED_RULES=("agentic.md" "spec-kit.yaml")
  for rule in "${REQUIRED_RULES[@]}"; do
    if [ -f "$RULES_DIR/$rule" ]; then
      echo -e "  ${GREEN}OK: $rule exists${NC}"
    else
      echo -e "  ${YELLOW}WARN: Missing recommended rule: $rule${NC}"
      warnings=$((warnings + 1))
    fi
  done
fi

# =============================================================================
# Check prompts directory
# =============================================================================
echo ""
echo "== Prompts Directory =="

PROMPTS_DIR=".continue/prompts"

if [ ! -d "$PROMPTS_DIR" ]; then
  echo -e "${YELLOW}WARN: Missing $PROMPTS_DIR directory${NC}"
  warnings=$((warnings + 1))
else
  echo -e "${GREEN}OK: $PROMPTS_DIR directory exists${NC}"

  # Check for required prompts
  REQUIRED_PROMPTS=("plan.md" "implement.md" "verify.md" "ship.md")
  for prompt in "${REQUIRED_PROMPTS[@]}"; do
    if [ -f "$PROMPTS_DIR/$prompt" ]; then
      echo -e "  ${GREEN}OK: $prompt exists${NC}"
    else
      echo -e "  ${YELLOW}WARN: Missing prompt: $prompt${NC}"
      warnings=$((warnings + 1))
    fi
  done
fi

# =============================================================================
# Check .continuerc.json (optional, for headless)
# =============================================================================
echo ""
echo "== Headless Configuration =="

if [ -f ".continuerc.json" ]; then
  if python3 -c "import json; json.load(open('.continuerc.json'))" 2>/dev/null; then
    echo -e "${GREEN}OK: .continuerc.json is valid${NC}"
  else
    echo -e "${RED}ERROR: .continuerc.json has invalid JSON${NC}"
    errors=$((errors + 1))
  fi
else
  echo -e "${YELLOW}INFO: No .continuerc.json (headless config)${NC}"
fi

# =============================================================================
# Summary
# =============================================================================
echo ""
echo "== Validation Summary =="
echo "Errors: $errors"
echo "Warnings: $warnings"

if [ "$errors" -gt 0 ]; then
  echo ""
  echo -e "${RED}FAIL: Continue configuration errors found${NC}"
  exit 1
fi

echo ""
echo -e "${GREEN}PASS: Continue configuration is valid${NC}"
exit 0
