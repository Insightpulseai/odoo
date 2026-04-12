#!/usr/bin/env bash
# vscode-ipai-control-tower/scripts/install.sh
# Validates the extension output, packages it, and installs into VS Code.
# Run from the vscode-ipai-control-tower/ directory.

set -euo pipefail
EXT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$EXT_DIR"

echo "=== IPAI Control Tower — build + install ==="

# 1. Validate compiled output exists
if [ ! -f "out/extension.js" ]; then
  echo "ERROR: out/extension.js not found. Run: npm run compile"
  exit 1
fi
echo "✓ out/extension.js present ($(du -sh out/extension.js | cut -f1))"

# 2. Check package.json present
if [ ! -f "package.json" ]; then
  echo "ERROR: package.json missing"
  exit 1
fi
echo "✓ package.json present"

# 3. Install deps if needed
if [ ! -d "node_modules/@vscode/vsce" ]; then
  echo "Installing devDependencies..."
  npm install
fi

# 4. Package
echo "Packaging..."
npx @vscode/vsce package --no-dependencies --out ipai-control-tower.vsix
ls -lh ipai-control-tower.vsix

# 5. Install
echo "Installing into VS Code..."
code --install-extension ipai-control-tower.vsix --force
echo ""
echo "✓ Done. Reload VS Code (Cmd+Shift+P → 'Reload Window') to activate."
echo ""
echo "Test the chat participant:"
echo "  Open chat panel (Cmd+Shift+I) → @ipai /ssot-doctrine"
