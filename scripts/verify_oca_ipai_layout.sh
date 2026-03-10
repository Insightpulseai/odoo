#!/usr/bin/env bash
set -euo pipefail

# Verify OCA and IPAI addon layout against config/addons.manifest.yaml
# Replaces legacy JSON manifest consumption with YAML via python3.

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

echo "Using manifest: $MANIFEST"

echo
echo "== Checking root directories =="
for rel in "addons/oca" "addons/ipai"; do
  if [ -d "$ROOT/$rel" ]; then
    echo "  OK: $rel exists"
  else
    echo "  MISSING: $rel"
  fi
done

echo
echo "== Checking OCA repositories placement =="
python3 -c "
import yaml, sys
with open('$MANIFEST') as f:
    m = yaml.safe_load(f)
for r in m.get('oca_repositories', []):
    repo = r['repo']
    path = f'addons/oca/{repo}'
    print(f'{repo}|{path}')
" | while IFS='|' read -r name path; do
  if [ -d "$ROOT/$path" ]; then
    echo "  OK: $name -> $path"
  else
    echo "  MISSING: $name at $path"
  fi
done

echo
echo "== Must-have modules (from manifest) =="
python3 -c "
import yaml
with open('$MANIFEST') as f:
    m = yaml.safe_load(f)
for r in m.get('oca_repositories', []):
    mods = r.get('must_have')
    if mods:
        print(f\"{r['repo']}: {', '.join(mods)}\")
"

echo
echo "Manifest + filesystem check complete (module install state is up to Odoo)."
