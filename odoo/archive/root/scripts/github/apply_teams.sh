#!/usr/bin/env bash
# apply_teams.sh - Create/update GitHub teams from configuration
# Usage: ./scripts/github/apply_teams.sh [teams_file]
set -euo pipefail

: "${ORG_SLUG:?missing ORG_SLUG environment variable}"
teams_file="${1:-ops/github/teams/teams.json}"

if [[ ! -f "$teams_file" ]]; then
  echo "ERROR: Teams file not found: $teams_file"
  exit 1
fi

echo "==> Applying teams from: $teams_file"
echo "    Organization: $ORG_SLUG"

success_count=0
fail_count=0

# Process each team definition
jq -c '.teams[]' "$teams_file" | while read -r team; do
  name="$(jq -r '.name' <<<"$team")"
  privacy="$(jq -r '.privacy // "closed"' <<<"$team")"
  description="$(jq -r '.description // ""' <<<"$team")"

  # Convert name to slug (lowercase, spaces to hyphens)
  slug="$(echo "$name" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')"

  echo "    Upserting team: $name (slug: $slug)"

  # Check if team exists
  if gh api "orgs/$ORG_SLUG/teams/$slug" >/dev/null 2>&1; then
    # Update existing team
    if gh api -X PATCH "orgs/$ORG_SLUG/teams/$slug" \
      -f name="$name" \
      -f privacy="$privacy" \
      -f description="$description" >/dev/null 2>&1; then
      echo "      ✓ Updated: $name"
    else
      echo "      ✗ Failed to update: $name"
    fi
  else
    # Create new team
    if gh api -X POST "orgs/$ORG_SLUG/teams" \
      -f name="$name" \
      -f privacy="$privacy" \
      -f description="$description" >/dev/null 2>&1; then
      echo "      ✓ Created: $name"
    else
      echo "      ✗ Failed to create: $name"
    fi
  fi
done

echo ""
echo "OK: Teams configuration applied."

# Apply team-repo mappings if defined
if jq -e '.team_repo_mappings' "$teams_file" >/dev/null 2>&1; then
  echo ""
  echo "==> Applying team-repo mappings"

  jq -c '.team_repo_mappings[]' "$teams_file" | while read -r mapping; do
    team="$(jq -r '.team' <<<"$mapping")"
    permission="$(jq -r '.permission // "push"' <<<"$mapping")"
    team_slug="$(echo "$team" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')"

    jq -r '.repos[]' <<<"$mapping" | while read -r repo; do
      echo "    Mapping $team -> $repo ($permission)"
      if gh api -X PUT "orgs/$ORG_SLUG/teams/$team_slug/repos/$ORG_SLUG/$repo" \
        -f permission="$permission" >/dev/null 2>&1; then
        echo "      ✓ Mapped"
      else
        echo "      ✗ Failed (repo may not exist or insufficient permissions)"
      fi
    done
  done

  echo ""
  echo "OK: Team-repo mappings applied."
fi
