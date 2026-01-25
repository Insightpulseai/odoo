#!/usr/bin/env bash
# Design Sync: Export Figma Variables + Publish Code Connect mappings
# Requires: FIGMA_ACCESS_TOKEN, FIGMA_FILE_KEY
set -euo pipefail

: "${FIGMA_ACCESS_TOKEN:?Missing FIGMA_ACCESS_TOKEN}"
: "${FIGMA_FILE_KEY:?Missing FIGMA_FILE_KEY}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$REPO_ROOT"

echo "==> (1) Exporting Figma Variables -> figma/tokens/"
node scripts/figma-export-variables.mjs

echo "==> (2) Publishing Code Connect mappings (expects figma/connect + figma.config.json present)"
# Install if not present. CLI is @figma/code-connect; docs show npm global install.
# In CI, prefer local devDependency and npx.
if [ -f package.json ]; then
  npm -s ls @figma/code-connect >/dev/null 2>&1 || npm -s i -D @figma/code-connect@latest
  npx -s figma connect publish --token="$FIGMA_ACCESS_TOKEN"
else
  npm -s i -g @figma/code-connect@latest
  npx -s figma connect publish --token="$FIGMA_ACCESS_TOKEN"
fi

echo "OK: design sync complete"
