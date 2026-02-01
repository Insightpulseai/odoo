#!/usr/bin/env bash
set -euo pipefail

: "${FIGMA_ACCESS_TOKEN:?Missing FIGMA_ACCESS_TOKEN}"
: "${FIGMA_FILE_KEY:?Missing FIGMA_FILE_KEY}"

OUT_DIR="${OUT_DIR:-artifacts/figma}"
CACHE_DIR="${CACHE_DIR:-.cache}"
mkdir -p "$OUT_DIR" "$CACHE_DIR"

ts="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
meta_json="${OUT_DIR}/figma_file_meta.json"
state_file="${CACHE_DIR}/figma_${FIGMA_FILE_KEY}_version.txt"

echo "Polling Figma file: ${FIGMA_FILE_KEY}..."

curl -sS \
  -H "X-Figma-Token: ${FIGMA_ACCESS_TOKEN}" \
  "https://api.figma.com/v1/files/${FIGMA_FILE_KEY}" \
  > "$meta_json"

# Check for API errors
if grep -q '"err"' "$meta_json" 2>/dev/null; then
  echo "ERROR: Figma API returned an error:"
  cat "$meta_json"
  exit 1
fi

name="$(python3 -c "
import json
d=json.load(open('$meta_json'))
print(d.get('name',''))
")"

version="$(python3 -c "
import json
d=json.load(open('$meta_json'))
print(d.get('version',''))
")"

last_modified="$(python3 -c "
import json
d=json.load(open('$meta_json'))
print(d.get('lastModified',''))
")"

prev="(none)"
changed="true"

if [[ -f "$state_file" ]]; then
  prev="$(cat "$state_file" || true)"
  if [[ "$prev" == "$version" ]]; then
    changed="false"
  fi
fi

echo "$version" > "$state_file"

# Generate poll_result.json using Python to handle special chars safely
python3 - "$ts" "$FIGMA_FILE_KEY" "$name" "$prev" "$version" "$last_modified" "$changed" > "${OUT_DIR}/poll_result.json" <<'PYEOF'
import json
import sys

ts, file_key, name, prev, version, last_modified, changed = sys.argv[1:8]
result = {
    "timestamp": ts,
    "file_key": file_key,
    "name": name,
    "prev_version": prev,
    "current_version": version,
    "last_modified": last_modified,
    "changed": changed == "true"
}
print(json.dumps(result, indent=2))
PYEOF

# Output for GitHub Actions
if [[ -n "${GITHUB_OUTPUT:-}" ]]; then
  echo "FIGMA_FILE_NAME=$name" >> "$GITHUB_OUTPUT"
  echo "FIGMA_PREV_VERSION=$prev" >> "$GITHUB_OUTPUT"
  echo "FIGMA_VERSION=$version" >> "$GITHUB_OUTPUT"
  echo "FIGMA_LAST_MODIFIED=$last_modified" >> "$GITHUB_OUTPUT"
  echo "FIGMA_CHANGED=$changed" >> "$GITHUB_OUTPUT"
fi

echo ""
echo "=== Figma Poll Result ==="
echo "File:         $name"
echo "Prev version: $prev"
echo "Curr version: $version"
echo "Last modified: $last_modified"
echo "Changed:      $changed"
echo "========================="
