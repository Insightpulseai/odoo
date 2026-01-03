#!/usr/bin/env bash
set -euo pipefail
OWNER_REPO="${1:-jgtolentino/odoo-ce}"

if ! command -v jq &> /dev/null; then
    echo "Error: jq is required but not installed."
    exit 1
fi

jq -c '.[]' ops/github/labels.json | while read -r row; do
  name=$(echo "$row" | jq -r .name)
  color=$(echo "$row" | jq -r .color)
  desc=$(echo "$row" | jq -r .description)
  
  echo "Applying label: $name"
  # Using || true to avoid failure if label exists (gh label create fails if exists)
  # Ideally we check existence or use edit if exists, but create --force isn't a flag in standard gh cli for labels usually?
  # Actually 'gh label create' has no --force to overwrite. 'gh label edit' allows editing.
  # We try create, if fails, try edit.
  
  if gh label list --repo "$OWNER_REPO" | grep -q "$name"; then
      gh label edit "$name" --repo "$OWNER_REPO" --color "$color" --description "$desc" >/dev/null
  else
      gh label create "$name" --repo "$OWNER_REPO" --color "$color" --description "$desc" >/dev/null
  fi
done
echo "Labels synced."
