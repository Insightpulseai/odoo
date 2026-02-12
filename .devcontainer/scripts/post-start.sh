#!/usr/bin/env bash
set -euo pipefail

echo "[post-start] Odoo 19 Development - Post-Start"

# Verify workspace mount
if [ ! -d "/workspaces/odoo/addons" ]; then
    echo "⚠️  Warning: /workspaces/odoo/addons not found"
fi

# Verify Docker socket access
if docker version >/dev/null 2>&1; then
    echo "✅ Docker socket accessible"
else
    echo "❌ Docker socket not accessible"
    exit 1
fi

# Verify PostgreSQL connectivity via Docker Compose
if docker compose -f /workspaces/odoo/sandbox/dev/compose.yml exec -T db pg_isready -U odoo >/dev/null 2>&1; then
    echo "✅ PostgreSQL connection verified"
else
    echo "⚠️  PostgreSQL connection failed (container may not be running)"
fi

# Load local environment if exists
if [ -f /workspaces/odoo/.env.local ]; then
    set -a
    source /workspaces/odoo/.env.local
    set +a
    echo "✅ Loaded .env.local"
fi

echo ""
echo "=== DevContainer Status ==="
echo "Odoo URL:   http://localhost:8069"
echo "Database:   odoo_dev@db:5432"
echo "Python:     $(python3 --version)"
echo "Docker:     $(docker --version | cut -d' ' -f3 | cut -d',' -f1)"
echo "Workspace:  /workspaces/odoo"
echo ""
echo "📍 Quick Start:"
echo "   cd sandbox/dev && docker compose up -d"
echo "   docker compose exec odoo odoo -d odoo_dev -u all"
echo "   ./scripts/repo_health.sh"
echo ""
