#!/usr/bin/env bash
# Devcontainer initializeCommand — validates Docker context before build.
# Codespaces: exit 0 early (Docker is managed by GitHub).
# Local: ensure the 'colima' (default) context is active.
set -euo pipefail

# Codespaces provides Docker natively — nothing to check
if [ "${CODESPACES:-}" = "true" ]; then
  exit 0
fi

ctx=$(docker context show 2>/dev/null || true)

if [ "$ctx" = "colima" ] || [ "$ctx" = "default" ]; then
  echo "[preflight] Docker context: $ctx — OK"
  exit 0
fi

echo "[preflight] ERROR: Expected docker context 'colima' or 'default', got: '${ctx:-<none>}'"
echo ""
echo "  Fix: run 'docker context use colima' or start Colima default profile:"
echo "    colima start"
echo "    docker context use colima"
exit 1
