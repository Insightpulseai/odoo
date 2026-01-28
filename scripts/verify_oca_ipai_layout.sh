#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MANIFEST="$ROOT/config/addons_manifest.oca_ipai.json"

if ! command -v jq >/dev/null 2>&1; then
  echo "ERROR: jq is required to verify manifest." >&2
  exit 1
fi

echo "✅ Using manifest: $MANIFEST"
oca_root="$(jq -r '.roots.oca_root' "$MANIFEST")"
ipai_root="$(jq -r '.roots.ipai_root' "$MANIFEST")"

echo "== Checking root directories =="
for rel in "$oca_root" "$ipai_root"; do
  if [ -d "$ROOT/$rel" ]; then
    echo "  ✅ $rel exists"
  else
    echo "  ❌ MISSING: $rel"
  fi
done

echo
echo "== Checking OCA repositories placement =="
jq -c '.oca_repositories[]' "$MANIFEST" | while read -r repo; do
  name="$(echo "$repo" | jq -r '.name')"
  path="$(echo "$repo" | jq -r '.path')"
  if [ -d "$ROOT/$path" ]; then
    echo "  ✅ $name → $path"
  else
    echo "  ❌ $name missing at $path"
  fi
done

echo
echo "== Priority modules snapshot (from manifest only) =="
jq -r '.oca_must_have_modules | to_entries[] | "\(.key): \(.value | join(", "))"' "$MANIFEST"

echo
echo "✔ Manifest + filesystem check complete (module install state is up to Odoo)."
