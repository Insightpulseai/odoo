#!/usr/bin/env bash
set -euo pipefail

# Clone missing OCA repositories listed in config/addons.manifest.yaml.
# Replaces legacy JSON manifest consumption with YAML via python3.
#
# NOTE: For production use, prefer gitaggregate:
#   gitaggregate -c oca-aggregate.yml
# This script is a lightweight fallback for quick dev setup.

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MANIFEST="$ROOT/config/addons.manifest.yaml"

if [ ! -f "$MANIFEST" ]; then
  echo "ERROR: Manifest not found: $MANIFEST" >&2
  exit 1
fi

if ! python3 -c "import yaml" 2>/dev/null; then
  echo "ERROR: PyYAML required. Install: pip install pyyaml" >&2
  exit 1
fi

echo "Checking for missing OCA repositories..."
echo

MISSING_COUNT=0
CLONED_COUNT=0

python3 -c "
import yaml
with open('$MANIFEST') as f:
    m = yaml.safe_load(f)
for r in m.get('oca_repositories', []):
    print(f\"{r['repo']}|{r['url']}|{r['ref']}\")
" | while IFS='|' read -r name url ref; do
  path="addons/oca/$name"

  if [ -d "$ROOT/$path" ]; then
    echo "OK: $name already exists at $path"
  else
    echo "Cloning $name from $url (ref: $ref)..."
    mkdir -p "$(dirname "$ROOT/$path")"
    if git clone --depth 1 --single-branch --branch "$ref" "$url" "$ROOT/$path"; then
      echo "   Cloned successfully to $path"
      CLONED_COUNT=$((CLONED_COUNT + 1))
    else
      echo "   Failed to clone (branch $ref may not exist)"
      MISSING_COUNT=$((MISSING_COUNT + 1))
    fi
    echo
  fi
done

echo
echo "Done. Run ./scripts/verify_oca_ipai_layout.sh to verify."
echo "For full production hydration, use: gitaggregate -c oca-aggregate.yml"
