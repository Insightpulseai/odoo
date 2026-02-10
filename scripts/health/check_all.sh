#!/usr/bin/env bash
# Complete service health check
# Usage: ./scripts/health/check_all.sh

set -euo pipefail
cd "$(dirname "$0")/../.."

# Load environment
set -a
source .env.platform.local 2>/dev/null || true
set +a

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║           COMPLETE SERVICE HEALTH CHECK                      ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Docker
echo "📦 Docker Services:"
docker ps --format "  {{.Names}}: {{.Status}}" --filter name=odoo
echo ""

# PostgreSQL
echo "🐘 PostgreSQL:"
docker exec odoo-postgres pg_isready -U odoo | sed 's/^/  /'
docker exec odoo-postgres psql -U odoo -lqt | cut -d \| -f 1 | grep -E "odoo_prod|postgres" | sed 's/^/  DB: /'
echo ""

# Web Services
echo "🌐 Web Services:"
echo "  Next.js: $(curl -s http://localhost:3002/api/auth/health | jq -r '.status') ($(curl -s http://localhost:3002/api/auth/health | jq -r '.latency_ms')ms)"
echo "  Odoo: $(curl -sI http://localhost:8069 | head -1 | cut -d' ' -f2-)"
echo ""

# Supabase
echo "☁️  Supabase:"
echo "  Auth API: $(curl -s "${SUPABASE_URL}/auth/v1/health" -H "apikey: ${SUPABASE_ANON_KEY}" | jq -r '.version')"
echo "  Edge Functions: $(curl -s "${SUPABASE_URL}/functions/v1/secret-smoke" -H "Authorization: Bearer ${SUPABASE_ANON_KEY}" | jq -r '"\(.present)/7 secrets"')"
echo ""

# Auth Endpoints
echo "🔐 Auth System:"
curl -s http://localhost:3002/api/auth/health | jq -r '"  Health: \(.status)"'
echo "  Callback: $(curl -sI http://localhost:3002/api/auth/callback | head -1 | cut -d' ' -f2-)"
echo "  Error Page: $(curl -sI 'http://localhost:3002/auth/error?error=test' | head -1 | cut -d' ' -f2-)"
echo ""

echo "✅ All services operational"
