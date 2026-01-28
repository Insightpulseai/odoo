#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MANIFEST="$ROOT/config/addons_manifest.oca_ipai.json"

if ! command -v jq >/dev/null 2>&1; then
  echo "ERROR: jq is required." >&2
  exit 1
fi

echo "🔍 Checking for missing OCA repositories..."
echo

MISSING_COUNT=0
CLONED_COUNT=0

jq -c '.oca_repositories[]' "$MANIFEST" | while read -r repo; do
  name="$(echo "$repo" | jq -r '.name')"
  url="$(echo "$repo" | jq -r '.url')"
  path="$(echo "$repo" | jq -r '.path')"

  if [ -d "$ROOT/$path" ]; then
    echo "✅ $name already exists at $path"
  else
    echo "📦 Cloning $name from $url..."
    mkdir -p "$(dirname "$ROOT/$path")"
    if git clone --depth 1 --single-branch --branch 18.0 "$url" "$ROOT/$path"; then
      echo "   ✅ Cloned successfully to $path"
      CLONED_COUNT=$((CLONED_COUNT + 1))
    else
      echo "   ⚠️  Failed to clone (branch 18.0 may not exist)"
      MISSING_COUNT=$((MISSING_COUNT + 1))
    fi
    echo
  fi
done

echo
echo "📊 Summary:"
echo "   Cloned: $CLONED_COUNT repositories"
if [ "$MISSING_COUNT" -gt 0 ]; then
  echo "   Failed: $MISSING_COUNT repositories (may need manual intervention)"
fi
echo
echo "✔ Done. Run ./scripts/verify_oca_ipai_layout.sh to verify."
