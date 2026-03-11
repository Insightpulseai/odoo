#!/usr/bin/env bash
# apply_custom_properties.sh - Apply org-level custom properties schema
# Usage: ./scripts/github/apply_custom_properties.sh [schema_file]
set -euo pipefail

: "${ORG_SLUG:?missing ORG_SLUG environment variable}"
schema_file="${1:-ops/github/custom-properties/schema.json}"

if [[ ! -f "$schema_file" ]]; then
  echo "ERROR: Schema file not found: $schema_file"
  exit 1
fi

echo "==> Applying custom properties from: $schema_file"
echo "    Organization: $ORG_SLUG"

# Parse and apply each property definition
props="$(jq -c '.properties[]' "$schema_file")"
success_count=0
fail_count=0

while IFS= read -r prop; do
  name="$(jq -r '.property_name' <<<"$prop")"
  value_type="$(jq -r '.value_type' <<<"$prop")"
  required="$(jq -r '.required // false' <<<"$prop")"
  default_value="$(jq -r '.default_value // null' <<<"$prop")"
  description="$(jq -r '.description // ""' <<<"$prop")"

  echo "    Upserting property: $name (type: $value_type)"

  # Build the API payload based on value type
  api_payload=$(jq -n \
    --arg name "$name" \
    --arg value_type "$value_type" \
    --argjson required "$required" \
    --arg default_value "$default_value" \
    --arg description "$description" \
    '{
      property_name: $name,
      value_type: $value_type,
      required: $required,
      description: $description
    } + (if $default_value != "null" then {default_value: $default_value} else {} end)')

  # Add allowed_values for single_select type
  if [[ "$value_type" == "single_select" ]]; then
    allowed_values="$(jq -c '.allowed_values // []' <<<"$prop")"
    api_payload=$(echo "$api_payload" | jq --argjson av "$allowed_values" '. + {allowed_values: $av}')
  fi

  # Try PATCH first (update), then POST (create) if it fails
  if gh api -X PATCH "orgs/$ORG_SLUG/properties/schema/$name" \
    -H "Accept: application/vnd.github+json" \
    --input - <<<"$api_payload" >/dev/null 2>&1; then
    echo "      ✓ Updated: $name"
    ((success_count++))
  elif gh api -X POST "orgs/$ORG_SLUG/properties/schema" \
    -H "Accept: application/vnd.github+json" \
    --input - <<<"$api_payload" >/dev/null 2>&1; then
    echo "      ✓ Created: $name"
    ((success_count++))
  else
    echo "      ✗ Failed: $name"
    ((fail_count++))
  fi
done <<<"$props"

echo ""
echo "==> Custom properties applied: $success_count succeeded, $fail_count failed"

if [[ $fail_count -gt 0 ]]; then
  echo "WARNING: Some properties failed to apply. Check org permissions."
  exit 1
fi

echo "OK: Custom property schema applied successfully."
