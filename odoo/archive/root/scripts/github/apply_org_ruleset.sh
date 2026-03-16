#!/usr/bin/env bash
# apply_org_ruleset.sh - Apply organization-level repository rulesets
# Usage: ./scripts/github/apply_org_ruleset.sh [ruleset_file]
set -euo pipefail

: "${ORG_SLUG:?missing ORG_SLUG environment variable}"
DEFAULT_BRANCH="${DEFAULT_BRANCH:-main}"

ruleset_file="${1:-ops/github/rulesets/org-repo-ruleset.json}"

if [[ ! -f "$ruleset_file" ]]; then
  echo "ERROR: Ruleset file not found: $ruleset_file"
  exit 1
fi

echo "==> Applying org ruleset from: $ruleset_file"
echo "    Organization: $ORG_SLUG"
echo "    Default branch: $DEFAULT_BRANCH"

# Substitute ~DEFAULT_BRANCH placeholder
payload="$(cat "$ruleset_file" | sed "s/~DEFAULT_BRANCH/${DEFAULT_BRANCH}/g")"

# Extract ruleset name for idempotency check
ruleset_name="$(echo "$payload" | jq -r '.name')"

# Check if ruleset already exists
echo "    Checking for existing ruleset: $ruleset_name"
existing_id="$(gh api "orgs/$ORG_SLUG/rulesets" \
  -H "Accept: application/vnd.github+json" 2>/dev/null \
  | jq -r ".[] | select(.name==\"$ruleset_name\") | .id" | head -n1 || echo "")"

if [[ -n "${existing_id:-}" && "${existing_id}" != "null" ]]; then
  echo "    Updating existing ruleset (id=$existing_id)"
  if gh api -X PUT "orgs/$ORG_SLUG/rulesets/$existing_id" \
    -H "Accept: application/vnd.github+json" \
    --input - <<<"$payload" >/dev/null 2>&1; then
    echo "    ✓ Ruleset updated: $ruleset_name"
  else
    echo "    ✗ Failed to update ruleset"
    exit 1
  fi
else
  echo "    Creating new ruleset: $ruleset_name"
  if gh api -X POST "orgs/$ORG_SLUG/rulesets" \
    -H "Accept: application/vnd.github+json" \
    --input - <<<"$payload" >/dev/null 2>&1; then
    echo "    ✓ Ruleset created: $ruleset_name"
  else
    echo "    ✗ Failed to create ruleset"
    exit 1
  fi
fi

echo ""
echo "OK: Org ruleset applied successfully."
