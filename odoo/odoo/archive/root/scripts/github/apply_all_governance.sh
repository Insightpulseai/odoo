#!/usr/bin/env bash
# apply_all_governance.sh - Apply all GitHub governance configurations
# Usage: ./scripts/github/apply_all_governance.sh
# Environment: ORG_SLUG (required), DEFAULT_BRANCH (optional, default: main)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

: "${ORG_SLUG:?missing ORG_SLUG environment variable}"
DEFAULT_BRANCH="${DEFAULT_BRANCH:-main}"

echo "=============================================="
echo "GitHub Governance - Full Apply"
echo "=============================================="
echo "Organization: $ORG_SLUG"
echo "Default Branch: $DEFAULT_BRANCH"
echo "=============================================="
echo ""

# Step 1: Validate configurations
echo "STEP 1: Validating governance configuration..."
"$SCRIPT_DIR/validate_governance.sh" || {
  echo "ERROR: Validation failed, aborting apply"
  exit 1
}
echo ""

# Step 2: Apply custom properties
echo "STEP 2: Applying custom properties..."
"$SCRIPT_DIR/apply_custom_properties.sh" || {
  echo "WARNING: Custom properties apply failed (may require org admin permissions)"
}
echo ""

# Step 3: Apply rulesets
echo "STEP 3: Applying organization rulesets..."
"$SCRIPT_DIR/apply_org_ruleset.sh" || {
  echo "WARNING: Ruleset apply failed (may require org admin permissions)"
}
echo ""

# Step 4: Apply teams
echo "STEP 4: Applying teams configuration..."
"$SCRIPT_DIR/apply_teams.sh" || {
  echo "WARNING: Teams apply failed (may require org admin permissions)"
}
echo ""

echo "=============================================="
echo "Governance Apply Complete"
echo "=============================================="
echo ""
echo "To verify, run:"
echo "  gh api orgs/$ORG_SLUG/properties/schema | jq '.[].property_name'"
echo "  gh api orgs/$ORG_SLUG/rulesets | jq '.[].name'"
echo "  gh api orgs/$ORG_SLUG/teams | jq '.[].slug'"
