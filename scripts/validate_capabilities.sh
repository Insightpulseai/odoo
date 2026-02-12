#!/usr/bin/env bash
set -euo pipefail

MANIFEST="agents/capabilities/manifest.json"

# Ensure jq available (CI environment)
if ! command -v jq >/dev/null 2>&1; then
  echo "❌ jq not available. This script must run in CI with jq installed."
  exit 2
fi

# Ensure rg (ripgrep) available
if ! command -v rg >/dev/null 2>&1; then
  echo "❌ ripgrep (rg) not available. Install with: apt-get install ripgrep"
  exit 2
fi

echo "==> Validating capability evidence against manifest"
echo ""

# Use a temp file to track failures across subshell boundary
TMPFILE=$(mktemp)
trap "rm -f $TMPFILE" EXIT

total=0

# Validate each capability
while IFS= read -r cap; do
  id=$(echo "$cap" | jq -r '.id')
  claim=$(echo "$cap" | jq -r '.claim')
  total=$((total + 1))

  echo "[$total] Validating: $id"
  echo "    Claim: $claim"

  cap_failed=0

  # Validate required paths exist
  paths=$(echo "$cap" | jq -r '.evidence.paths_must_exist[]?' 2>/dev/null || true)
  if [ -n "${paths:-}" ]; then
    while IFS= read -r p; do
      [ -z "$p" ] && continue
      if [ ! -e "$p" ]; then
        echo "    ❌ Missing path: $p"
        cap_failed=1
      else
        echo "    ✅ Path exists: $p"
      fi
    done <<<"$paths"
  fi

  # Validate grep patterns match somewhere in repo
  greps=$(echo "$cap" | jq -r '.evidence.grep_must_match[]?' 2>/dev/null || true)
  if [ -n "${greps:-}" ]; then
    while IFS= read -r g; do
      [ -z "$g" ] && continue
      if ! rg -q -S "$g" . 2>/dev/null; then
        echo "    ❌ Missing grep pattern: $g"
        cap_failed=1
      else
        echo "    ✅ Grep pattern found: $g"
      fi
    done <<<"$greps"
  fi

  if [ "$cap_failed" -eq 1 ]; then
    echo "FAIL" >> "$TMPFILE"
  fi

  echo ""
done < <(jq -c '.capabilities[]' "$MANIFEST")

if [ -s "$TMPFILE" ]; then
  echo ""
  echo "❌ Capability evidence validation FAILED"
  echo "   Some claimed capabilities lack code evidence in the repository."
  echo "   Either implement the capability or remove the claim from manifest.json"
  exit 1
fi

echo "✅ All capability evidence validated successfully"
echo "   Total capabilities checked: $total"
