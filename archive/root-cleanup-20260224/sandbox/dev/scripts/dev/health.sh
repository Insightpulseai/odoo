#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════════════
# Check Odoo Dev Sandbox Health
# ═══════════════════════════════════════════════════════════════════════════════
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

echo "🔍 Checking Odoo dev sandbox health..."
echo ""

# Check containers
echo "📦 Containers:"
docker compose ps
echo ""

# Check database
echo "🗄️  Database:"
if docker compose exec -T db pg_isready -U odoo &>/dev/null; then
  echo "   ✅ PostgreSQL is ready"
else
  echo "   ❌ PostgreSQL is NOT ready"
fi
echo ""

# Check Odoo HTTP
echo "🌐 Odoo HTTP:"
if curl -sf http://localhost:8069/web/health &>/dev/null; then
  echo "   ✅ Odoo is responding (http://localhost:8069)"
else
  echo "   ❌ Odoo is NOT responding"
  echo "   💡 Check logs: docker compose logs odoo"
fi
echo ""

# Show recent logs
echo "📋 Recent Odoo logs (last 10 lines):"
docker compose logs --tail=10 odoo
