#!/usr/bin/env bash
set -euo pipefail

echo "=== Release Gate Check ==="
bash scripts/sync_current_state.sh >/dev/null

if ! git diff --quiet; then
  echo "❌ ERROR: Drift detected. Release blocked."
  echo "The following files are out of sync:"
  git status --porcelain
  echo ""
  echo "Run './scripts/sync_current_state.sh' and commit changes before releasing."
  exit 1
fi

echo "✅ OK: Repository is in sync. Safe to tag/release."
