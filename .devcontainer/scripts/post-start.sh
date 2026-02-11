#!/bin/bash
set -e

echo "Odoo 19 Development - Post-Start"

# Verify workspace mount
if [ ! -d "/workspace/addons" ]; then
    echo "Warning: /workspace/addons not found"
fi

# Verify PostgreSQL connectivity
if pg_isready -h postgres -U odoo -d odoo; then
    echo "PostgreSQL connection verified"
else
    echo "PostgreSQL connection failed"
    exit 1
fi

# Load local environment if exists
if [ -f /workspace/.env.local ]; then
    set -a
    source /workspace/.env.local
    set +a
    echo "Loaded .env.local"
fi

echo ""
echo "Odoo URL:   http://localhost:8069"
echo "Database:   odoo@postgres:5432"
echo "Python:     $(python3 --version)"
echo "Workspace:  /workspace"
echo ""
echo "Quick Start:"
echo "  python odoo-bin -d odoo_dev --addons-path=addons"
echo "  ./scripts/repo_health.sh"
echo ""
