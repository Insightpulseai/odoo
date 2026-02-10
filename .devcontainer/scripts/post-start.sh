#!/bin/bash
set -e

echo "🚀 Odoo 19 Development - Post-Start"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Verify workspace mount
if [ ! -d "/workspace/addons" ]; then
    echo "⚠️  Warning: /workspace/addons not found"
fi

# Verify PostgreSQL connectivity
if pg_isready -h postgres -U odoo -d postgres; then
    echo "✅ PostgreSQL connection verified"
else
    echo "❌ PostgreSQL connection failed"
    exit 1
fi

# Display environment info
echo ""
echo "🎯 Development Environment Ready"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Odoo URL: http://localhost:8069"
echo "Database: postgres@postgres:5432"
echo "User: odoo / odoo"
echo "Python: $(python3 --version)"
echo "Workspace: /workspace"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "💡 Quick Start:"
echo "  python odoo-bin -d odoo --addons-path=addons"
echo "  ./scripts/odoo_dev.sh        # If wrapper exists"
echo "  ./scripts/repo_health.sh     # Run health checks"
echo ""

# Load local environment if exists
if [ -f .env.local ]; then
    set -a
    source .env.local
    set +a
    echo "✅ Loaded .env.local"
fi
