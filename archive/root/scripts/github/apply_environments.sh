#!/usr/bin/env bash
# apply_environments.sh — Create/update GitHub environments from declarative config
# Source: ops/github/environments/environments.json
# Requires: GH_TOKEN with repo admin permissions
set -euo pipefail

REPO="${REPO:-Insightpulseai/odoo}"
CONFIG="ops/github/environments/environments.json"

if [[ ! -f "$CONFIG" ]]; then
  echo "ERROR: $CONFIG not found" >&2
  exit 1
fi

if [[ -z "${GH_TOKEN:-}" ]]; then
  echo "ERROR: GH_TOKEN not set. Set it with repo admin permissions." >&2
  exit 1
fi

API="https://api.github.com"
AUTH_HEADER="Authorization: Bearer ${GH_TOKEN}"
ACCEPT="Accept: application/vnd.github+json"
API_VERSION="X-GitHub-Api-Version: 2022-11-28"

env_count=$(jq '.environments | length' "$CONFIG")
echo "==> Applying $env_count environments to $REPO"
echo ""

success=0
failed=0

for i in $(seq 0 $((env_count - 1))); do
  env_name=$(jq -r ".environments[$i].name" "$CONFIG")
  env_desc=$(jq -r ".environments[$i].description // empty" "$CONFIG")
  wait_timer=$(jq -r ".environments[$i].protection_rules.wait_timer // 0" "$CONFIG")
  has_branch_policy=$(jq -r ".environments[$i].protection_rules.deployment_branch_policy // null" "$CONFIG")

  echo "--- [$((i + 1))/$env_count] $env_name ---"

  # Build the PUT body
  body="{}"

  # Wait timer (only for non-zero values)
  if [[ "$wait_timer" -gt 0 ]]; then
    body=$(echo "$body" | jq --argjson wt "$wait_timer" '. + {wait_timer: $wt}')
  fi

  # Deployment branch policy
  if [[ "$has_branch_policy" != "null" ]]; then
    protected=$(jq -r ".environments[$i].protection_rules.deployment_branch_policy.protected_branches // false" "$CONFIG")
    body=$(echo "$body" | jq --argjson pb "$protected" '. + {deployment_branch_policy: {protected_branches: $pb, custom_branch_policies: false}}')

    # If custom branch policies exist and protected_branches is false
    custom_count=$(jq ".environments[$i].protection_rules.deployment_branch_policy.custom_branch_policies | length" "$CONFIG")
    if [[ "$protected" == "false" && "$custom_count" -gt 0 ]]; then
      body=$(echo "$body" | jq '. + {deployment_branch_policy: {protected_branches: false, custom_branch_policies: true}}')
    fi
  fi

  # URL-encode environment name (spaces and special chars)
  encoded_name=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$env_name', safe=''))")

  # Create or update the environment
  status_code=$(curl -s -o /dev/null -w "%{http_code}" \
    -X PUT \
    -H "$AUTH_HEADER" \
    -H "$ACCEPT" \
    -H "$API_VERSION" \
    -H "Content-Type: application/json" \
    -d "$body" \
    "$API/repos/$REPO/environments/$encoded_name")

  if [[ "$status_code" =~ ^2 ]]; then
    echo "  Created/updated (HTTP $status_code)"
    success=$((success + 1))

    # Apply custom branch policies if needed
    if [[ "$has_branch_policy" != "null" && "$protected" == "false" && "$custom_count" -gt 0 ]]; then
      echo "  Applying $custom_count custom branch policies..."
      for j in $(seq 0 $((custom_count - 1))); do
        branch_name=$(jq -r ".environments[$i].protection_rules.deployment_branch_policy.custom_branch_policies[$j].name" "$CONFIG")
        # Determine type: tag pattern (v*) vs branch name
        if [[ "$branch_name" == *"*"* ]]; then
          bp_type="tag"
        else
          bp_type="branch"
        fi
        bp_status=$(curl -s -o /dev/null -w "%{http_code}" \
          -X POST \
          -H "$AUTH_HEADER" \
          -H "$ACCEPT" \
          -H "$API_VERSION" \
          -H "Content-Type: application/json" \
          -d "{\"type\":\"$bp_type\",\"name\":\"$branch_name\"}" \
          "$API/repos/$REPO/environments/$encoded_name/deployment-branch-policies")
        if [[ "$bp_status" =~ ^2 ]]; then
          echo "    + $bp_type policy: $branch_name (HTTP $bp_status)"
        else
          echo "    ! $bp_type policy: $branch_name failed (HTTP $bp_status)"
        fi
      done
    fi
  else
    echo "  FAILED (HTTP $status_code)"
    failed=$((failed + 1))
  fi

  # Report required secrets
  secret_count=$(jq ".environments[$i].secrets_required | length" "$CONFIG")
  if [[ "$secret_count" -gt 0 ]]; then
    echo "  Required secrets ($secret_count):"
    for s in $(jq -r ".environments[$i].secrets_required[]" "$CONFIG"); do
      echo "    - $s"
    done
  fi

  echo ""
done

echo "==> Done: $success succeeded, $failed failed (of $env_count total)"

if [[ "$failed" -gt 0 ]]; then
  exit 1
fi
