#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════════════
# Stop Odoo Dev Sandbox
# ═══════════════════════════════════════════════════════════════════════════════
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

echo "🛑 Stopping Odoo dev sandbox..."

docker compose down

echo ""
echo "✅ Services stopped"
echo ""
echo "💡 Data preserved in volumes:"
echo "   - odoo-dev-db-data"
echo "   - odoo-dev-filestore"
echo ""
echo "🗑️  To remove volumes:"
echo "   docker compose down -v"
