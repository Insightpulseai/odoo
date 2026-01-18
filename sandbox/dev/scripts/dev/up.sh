#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════════════
# Start Odoo Dev Sandbox
# ═══════════════════════════════════════════════════════════════════════════════
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

echo "📦 Starting Odoo dev sandbox..."

# Check for .env file
if [ ! -f .env ]; then
  echo "⚠️  No .env file found. Using defaults from .env.example"
  echo "   Run: cp .env.example .env"
fi

# Start services
docker compose up -d

echo ""
echo "✅ Services starting..."
echo ""
echo "🔍 Checking health..."
sleep 5

docker compose ps

echo ""
echo "📋 Logs (Ctrl+C to exit):"
echo "   docker compose logs -f"
echo ""
echo "🌐 Access Odoo:"
echo "   http://localhost:8069"
echo ""
echo "🛑 Stop:"
echo "   docker compose down"
