#!/usr/bin/env bash
# check-sync.sh - Verify local ↔ Codespaces sync status
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SANDBOX_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║         LOCAL ↔ CODESPACES SYNC STATUS                           ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

cd "$REPO_ROOT"

# Git State
echo "✅ Git State:"
CURRENT_BRANCH=$(git branch --show-current)
HEAD_SHA=$(git rev-parse --short HEAD)
ORIGIN_SHA=$(git rev-parse --short origin/main)
UNCOMMITTED=$(git status --porcelain | wc -l | tr -d ' ')

echo "   Branch: $CURRENT_BRANCH"
echo "   HEAD: $HEAD_SHA"
echo "   Origin: $ORIGIN_SHA"

if [[ "$HEAD_SHA" == "$ORIGIN_SHA" ]]; then
    echo "   Status: ✓ Synced with origin/main"
else
    echo "   Status: ⚠ Diverged from origin/main"
fi

if [[ "$UNCOMMITTED" -eq 0 ]]; then
    echo "   Working tree: ✓ Clean"
else
    echo "   Working tree: ⚠ $UNCOMMITTED uncommitted changes"
fi
echo ""

# Sync Scripts
echo "✅ Sync Scripts:"
SYNC_ENV=$([ -f "$SANDBOX_ROOT/scripts/dev/sync-env.sh" ] && echo "✓" || echo "✗")
START_DEV=$([ -f "$SANDBOX_ROOT/scripts/dev/start-dev.sh" ] && echo "✓" || echo "✗")
echo "   sync-env.sh: $SYNC_ENV"
echo "   start-dev.sh: $START_DEV"
echo ""

# Documentation
echo "✅ Documentation:"
SYNC_GUIDE=$([ -f "$SANDBOX_ROOT/SYNC_GUIDE.md" ] && echo "✓" || echo "✗")
DEV_SANDBOX=$([ -f "$SANDBOX_ROOT/docs/runbooks/DEV_SANDBOX.md" ] && echo "✓" || echo "✗")
echo "   SYNC_GUIDE.md: $SYNC_GUIDE"
echo "   DEV_SANDBOX.md: $DEV_SANDBOX"
echo ""

# Devcontainer Config
echo "✅ Devcontainer Config:"
DEVCONTAINER_JSON=$([ -f "$REPO_ROOT/.devcontainer/devcontainer.json" ] && echo "✓" || echo "✗")
DOCKER_COMPOSE=$([ -f "$REPO_ROOT/.devcontainer/docker-compose.yml" ] && echo "✓" || echo "✗")
echo "   devcontainer.json: $DEVCONTAINER_JSON"
echo "   docker-compose.yml: $DOCKER_COMPOSE"
echo ""

# Overall Status
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║ OVERALL STATUS                                                   ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

if [[ "$HEAD_SHA" == "$ORIGIN_SHA" ]] && \
   [[ "$UNCOMMITTED" -eq 0 ]] && \
   [[ "$SYNC_ENV" == "✓" ]] && \
   [[ "$START_DEV" == "✓" ]] && \
   [[ "$DEVCONTAINER_JSON" == "✓" ]] && \
   [[ "$DOCKER_COMPOSE" == "✓" ]]; then
    echo "✅ All checks passed - environments are synchronized"
    echo ""
    echo "Ready to:"
    echo "  - Work locally: ./scripts/dev/start-dev.sh"
    echo "  - Work in Codespaces: gh codespace create --repo jgtolentino/odoo-ce --branch main"
else
    echo "⚠️  Some checks failed - run ./scripts/dev/sync-env.sh to synchronize"
fi
echo ""

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║ USAGE COMMANDS                                                   ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""
echo "Daily Start (Local):"
echo "  cd ~/Documents/GitHub/odoo-ce/sandbox/dev"
echo "  ./scripts/dev/sync-env.sh"
echo "  ./scripts/dev/start-dev.sh"
echo ""
echo "Daily Start (Codespaces):"
echo "  gh codespace create --repo jgtolentino/odoo-ce --branch main"
echo "  cd /workspaces/odoo-ce/sandbox/dev"
echo "  ./scripts/dev/sync-env.sh"
echo "  ./scripts/dev/start-dev.sh"
echo ""
echo "Quick Verification:"
echo "  git status"
echo "  ./scripts/verify.sh"
echo "  curl -I http://localhost:8069/web/login"
echo ""
