#!/usr/bin/env bash
set -euo pipefail

VENDOR_DIR="${1:-templates/vendor}"

fail(){ echo "❌ $*" >&2; exit 1; }

[[ -d "$VENDOR_DIR" ]] || fail "missing vendor dir: $VENDOR_DIR"

# Every vendored template must have a .PINNED_SHA file
missing=0
for d in "$VENDOR_DIR"/*; do
  [[ -d "$d" ]] || continue
  base="$(basename "$d")"
  pin="$VENDOR_DIR/${base}.PINNED_SHA"
  if [[ ! -f "$pin" ]]; then
    echo "❌ missing pin file: $pin" >&2
    missing=1
  else
    sha="$(tr -d '\n\r ' < "$pin")"
    if [[ ! "$sha" =~ ^[0-9a-f]{40}$ ]]; then
      echo "❌ invalid sha in: $pin => '$sha'" >&2
      missing=1
    fi
  fi
done

[[ "$missing" -eq 0 ]] || fail "template pin guard failed"
echo "✅ template pin guard OK"
