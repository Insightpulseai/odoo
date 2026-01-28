#!/usr/bin/env bash
# sync-env.sh - Synchronize local and Codespaces development environments
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SANDBOX_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "🔄 Syncing development environment..."
echo ""

# 1. Ensure we're on main branch
echo "1️⃣ Checking Git branch..."
cd "$REPO_ROOT"
CURRENT_BRANCH=$(git branch --show-current)
if [[ "$CURRENT_BRANCH" != "main" ]]; then
    echo "⚠️  Warning: Not on main branch (currently on: $CURRENT_BRANCH)"
    read -p "Switch to main? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git checkout main
    else
        echo "❌ Aborting - must be on main branch for sync"
        exit 1
    fi
fi

# 2. Pull latest changes
echo ""
echo "2️⃣ Pulling latest changes from origin/main..."
git pull origin main || {
    echo "❌ Failed to pull from origin/main"
    exit 1
}

# 3. Check for unpushed commits
echo ""
echo "3️⃣ Checking for unpushed commits..."
UNPUSHED=$(git log origin/main..HEAD --oneline | wc -l | tr -d ' ')
if [[ "$UNPUSHED" -gt 0 ]]; then
    echo "⚠️  You have $UNPUSHED unpushed commit(s):"
    git log origin/main..HEAD --oneline
    echo ""
    read -p "Push these commits to origin/main? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git push origin main || {
            echo "❌ Failed to push to origin/main"
            exit 1
        }
    else
        echo "⚠️  Continuing with unpushed commits (local and Codespaces will diverge)"
    fi
fi

# 4. Verify devcontainer config exists
echo ""
echo "4️⃣ Verifying devcontainer configuration..."
if [[ ! -f "$REPO_ROOT/.devcontainer/devcontainer.json" ]]; then
    echo "❌ Missing .devcontainer/devcontainer.json"
    exit 1
fi
if [[ ! -f "$REPO_ROOT/.devcontainer/docker-compose.yml" ]]; then
    echo "❌ Missing .devcontainer/docker-compose.yml"
    exit 1
fi
echo "✅ Devcontainer config present"

# 5. Check Docker availability
echo ""
echo "5️⃣ Checking Docker availability..."
if ! docker info &>/dev/null; then
    echo "⚠️  Docker not running locally"
    echo "   Skipping container sync (Codespaces will handle this)"
else
    echo "✅ Docker running locally"

    # 6. Sync containers (optional - only if Docker is available)
    echo ""
    echo "6️⃣ Syncing containers..."
    read -p "Start devcontainer services locally? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cd "$REPO_ROOT"
        docker compose -f .devcontainer/docker-compose.yml up -d
        echo "✅ Devcontainer services started"
    else
        echo "⏭️  Skipping container start"
    fi
fi

# 7. Verify repo health
echo ""
echo "7️⃣ Running repo health checks..."
if [[ -f "$SANDBOX_ROOT/scripts/verify.sh" ]]; then
    "$SANDBOX_ROOT/scripts/verify.sh" || {
        echo "⚠️  Health checks failed - review output above"
        exit 1
    }
else
    echo "⚠️  verify.sh not found, skipping health checks"
fi

# 8. Display current state
echo ""
echo "✅ Environment sync complete!"
echo ""
echo "Current state:"
echo "  Branch: $(git branch --show-current)"
echo "  HEAD: $(git rev-parse --short HEAD)"
echo "  Origin: $(git rev-parse --short origin/main)"
echo ""
echo "Next steps:"
echo "  - Local dev: ./scripts/dev/up.sh"
echo "  - Codespaces: gh codespace create --repo jgtolentino/odoo-ce --branch main"
echo ""
