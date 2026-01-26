#!/usr/bin/env bash
# validate_governance.sh - Validate GitHub governance configuration files
# Usage: ./scripts/github/validate_governance.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "==> Validating GitHub governance configuration"
echo "    Repo root: $REPO_ROOT"

errors=0

# Validate custom properties schema
echo ""
echo "--- Custom Properties Schema ---"
schema_file="$REPO_ROOT/ops/github/custom-properties/schema.json"
if [[ -f "$schema_file" ]]; then
  if jq empty "$schema_file" 2>/dev/null; then
    prop_count="$(jq '.properties | length' "$schema_file")"
    echo "✓ Valid JSON: $schema_file ($prop_count properties)"

    # Validate required fields
    jq -e '.properties[] | select(.property_name and .value_type and .required != null)' "$schema_file" >/dev/null 2>&1 || {
      echo "✗ Missing required fields in properties"
      ((errors++))
    }
  else
    echo "✗ Invalid JSON: $schema_file"
    ((errors++))
  fi
else
  echo "✗ Missing: $schema_file"
  ((errors++))
fi

# Validate rulesets
echo ""
echo "--- Repository Rulesets ---"
ruleset_file="$REPO_ROOT/ops/github/rulesets/org-repo-ruleset.json"
if [[ -f "$ruleset_file" ]]; then
  if jq empty "$ruleset_file" 2>/dev/null; then
    ruleset_name="$(jq -r '.name' "$ruleset_file")"
    rule_count="$(jq '.rules | length' "$ruleset_file")"
    echo "✓ Valid JSON: $ruleset_file (name: $ruleset_name, $rule_count rules)"

    # Validate required fields
    jq -e '.name and .target and .enforcement and .rules' "$ruleset_file" >/dev/null 2>&1 || {
      echo "✗ Missing required ruleset fields"
      ((errors++))
    }
  else
    echo "✗ Invalid JSON: $ruleset_file"
    ((errors++))
  fi
else
  echo "✗ Missing: $ruleset_file"
  ((errors++))
fi

# Validate teams configuration
echo ""
echo "--- Teams Configuration ---"
teams_file="$REPO_ROOT/ops/github/teams/teams.json"
if [[ -f "$teams_file" ]]; then
  if jq empty "$teams_file" 2>/dev/null; then
    team_count="$(jq '.teams | length' "$teams_file")"
    echo "✓ Valid JSON: $teams_file ($team_count teams)"

    # Validate required fields
    jq -e '.teams[] | select(.name and .privacy)' "$teams_file" >/dev/null 2>&1 || {
      echo "✗ Missing required team fields"
      ((errors++))
    }
  else
    echo "✗ Invalid JSON: $teams_file"
    ((errors++))
  fi
else
  echo "✗ Missing: $teams_file"
  ((errors++))
fi

# Summary
echo ""
echo "==> Validation complete"
if [[ $errors -eq 0 ]]; then
  echo "✓ All governance configuration files are valid"
  exit 0
else
  echo "✗ Found $errors error(s)"
  exit 1
fi
