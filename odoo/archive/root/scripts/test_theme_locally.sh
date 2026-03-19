#!/bin/bash
# Test TBWA theme changes locally
set -e

echo "🧪 Testing TBWA Theme Changes"
echo "=============================="

# Check Docker availability
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not available"
    echo "📝 Manual testing required on production: https://erp.insightpulseai.com"
    exit 1
fi

if ! docker info &> /dev/null; then
    echo "❌ Docker daemon not running"
    echo "📝 Start Docker Desktop and retry"
    exit 1
fi

# Start services
echo "🚀 Starting Odoo development environment..."
docker compose -f docker-compose.dev.yml up -d postgres odoo-core

# Wait for services
echo "⏳ Waiting for Odoo to start (30s)..."
sleep 30

# Health check
echo "🔍 Checking Odoo health..."
if curl -sf http://localhost:8069/web/health > /dev/null; then
    echo "✅ Odoo is running"
else
    echo "❌ Odoo health check failed"
    docker compose -f docker-compose.dev.yml logs odoo-core --tail 50
    exit 1
fi

# Test endpoints
echo ""
echo "📋 Test URLs:"
echo "  - Login page: http://localhost:8069/web/login"
echo "  - Database list: http://localhost:8069/web/database/selector"
echo ""
echo "✅ Visual checks:"
echo "  1. Logo in header should not overlap with menu items"
echo "  2. Footer should display TBWA SMP branding"
echo "  3. Footer should have: Logo, address, legal links, social icons"
echo "  4. Footer should be responsive (test mobile view)"
echo ""
echo "🔧 To update theme:"
echo "  docker compose -f docker-compose.dev.yml exec odoo-core odoo -d odoo_dev -u ipai_web_theme_tbwa --stop-after-init"
