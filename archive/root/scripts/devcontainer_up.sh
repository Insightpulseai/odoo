#!/usr/bin/env bash
set -euo pipefail

# CLI-only devcontainer launcher (no VS Code required)
# Requires: Docker running on host + node/npm available on host

if ! command -v devcontainer >/dev/null 2>&1; then
  echo "[devcontainer_up] @devcontainers/cli not found, installing..."
  npm i -g @devcontainers/cli
fi

echo "[devcontainer_up] Starting devcontainer..."
devcontainer up --workspace-folder .

echo ""
echo "✅ DevContainer is running"
echo ""
echo "📍 Execute commands inside container:"
echo "   devcontainer exec --workspace-folder . -- bash -lc 'python --version'"
echo ""
echo "📍 Start Odoo:"
echo "   devcontainer exec --workspace-folder . -- bash -lc 'cd sandbox/dev && docker compose up -d'"
echo ""
