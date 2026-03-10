#!/usr/bin/env bash
set -euo pipefail

# Prevent accidental commits of sandbox artifacts
tracked="$(git ls-files 'sandbox/**/.artifacts/**' || true)"
if [ -n "$tracked" ]; then
  echo "❌ FAIL: sandbox artifacts are tracked in git:"
  echo "$tracked"
  echo ""
  echo "Action: remove from index and keep sandbox/**/.artifacts/ in .gitignore."
  exit 1
fi

echo "✅ OK: no sandbox/.artifacts tracked"
