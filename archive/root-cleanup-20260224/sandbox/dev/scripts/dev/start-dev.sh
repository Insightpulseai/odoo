#!/usr/bin/env bash
# start-dev.sh - Unified dev environment starter (local + Codespaces)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SANDBOX_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "🚀 Starting development environment..."
echo ""

# Detect environment
if [[ -n "${CODESPACES:-}" ]]; then
    ENV_TYPE="codespaces"
    echo "📦 Environment: GitHub Codespaces"
else
    ENV_TYPE="local"
    echo "💻 Environment: Local"
fi
echo ""

# 1. Start devcontainer services
echo "1️⃣ Starting devcontainer services..."
cd "$REPO_ROOT"

if [[ ! -f .devcontainer/docker-compose.yml ]]; then
    echo "❌ .devcontainer/docker-compose.yml not found"
    exit 1
fi

docker compose -f .devcontainer/docker-compose.yml up -d || {
    echo "❌ Failed to start devcontainer services"
    exit 1
}
echo "✅ Devcontainer services started"

# 2. Wait for PostgreSQL
echo ""
echo "2️⃣ Waiting for PostgreSQL..."
MAX_WAIT=30
WAIT_COUNT=0
until docker compose -f .devcontainer/docker-compose.yml exec -T postgres pg_isready -U odoo &>/dev/null; do
    if [[ $WAIT_COUNT -ge $MAX_WAIT ]]; then
        echo "❌ PostgreSQL failed to start within ${MAX_WAIT}s"
        exit 1
    fi
    echo -n "."
    sleep 1
    ((WAIT_COUNT++))
done
echo ""
echo "✅ PostgreSQL ready"

# 3. Run health checks
echo ""
echo "3️⃣ Running health checks..."
if [[ -f "$SANDBOX_ROOT/scripts/dev/health.sh" ]]; then
    "$SANDBOX_ROOT/scripts/dev/health.sh" || {
        echo "⚠️  Health checks failed - review output above"
    }
else
    echo "⚠️  health.sh not found, skipping"
fi

# 4. Display access information
echo ""
echo "✅ Development environment ready!"
echo ""
echo "Access URLs:"

if [[ "$ENV_TYPE" == "codespaces" ]]; then
    CODESPACE_NAME="${CODESPACE_NAME:-unknown}"
    echo "  Odoo: https://$CODESPACE_NAME-8069.preview.app.github.dev"
    echo "  PostgreSQL: localhost:5432 (inside codespace)"
else
    echo "  Odoo: http://localhost:8069"
    echo "  PostgreSQL: localhost:5432"
fi

echo ""
echo "Database credentials:"
echo "  User: odoo"
echo "  Password: odoo"
echo "  Database: odoo_dev"
echo ""
echo "Next steps:"
echo "  - View logs: ./scripts/dev/logs.sh"
echo "  - Stop services: ./scripts/dev/down.sh"
echo "  - Reset database: ./scripts/dev/reset-db.sh"
echo ""
