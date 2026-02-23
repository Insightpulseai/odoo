#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════════════
# Reset Odoo Dev Database (DESTRUCTIVE)
# ═══════════════════════════════════════════════════════════════════════════════
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

echo "⚠️  WARNING: This will DELETE all data in odoo_dev database!"
echo ""
read -p "Type 'yes' to confirm: " -r
echo

if [[ ! $REPLY =~ ^yes$ ]]; then
  echo "❌ Aborted"
  exit 1
fi

echo "🗑️  Dropping odoo_dev database..."

# Drop and recreate database
docker compose exec db psql -U odoo -d postgres <<-EOSQL
  DROP DATABASE IF EXISTS odoo_dev;
  CREATE DATABASE odoo_dev OWNER odoo;
EOSQL

echo ""
echo "✅ Database reset complete"
echo ""
echo "🔄 Restart Odoo to initialize:"
echo "   docker compose restart odoo"
echo ""
echo "🌐 Then access:"
echo "   http://localhost:8069"
