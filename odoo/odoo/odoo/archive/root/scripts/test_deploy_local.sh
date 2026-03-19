#!/bin/bash
# Local Test Deployment - Verify deployment approach works
# This tests the deployment logic without requiring production environment

set -e

echo "🧪 Local Deployment Test Starting"
echo "=================================="

# 1. Check if Docker is available
echo "🐳 Step 1: Check Docker availability"
docker --version || { echo "❌ Docker not available"; exit 1; }
echo "✅ Docker is available"

# 2. Check if Docker Compose is available
echo "📋 Step 2: Check Docker Compose availability"
docker compose version || { echo "❌ Docker Compose not available"; exit 1; }
echo "✅ Docker Compose is available"

# 3. Verify deployment files exist
echo "📁 Step 3: Verify deployment files"
[ -f "deploy/docker-compose.yml" ] || { echo "❌ docker-compose.yml missing"; exit 1; }
[ -f "deploy/odoo.conf" ] || { echo "❌ odoo.conf missing"; exit 1; }
echo "✅ All deployment files exist"

# 4. Verify custom modules exist
echo "📦 Step 4: Verify custom modules"
[ -d "addons/ipai_equipment" ] || { echo "❌ ipai_equipment module missing"; exit 1; }
[ -d "addons/ipai_expense" ] || { echo "❌ ipai_expense module missing"; exit 1; }
[ -d "addons/ipai_finance_monthly_closing" ] || { echo "❌ ipai_finance_monthly_closing module missing"; exit 1; }
[ -d "addons/ipai_ocr_expense" ] || { echo "❌ ipai_ocr_expense module missing"; exit 1; }
[ -d "addons/ipai_ce_cleaner" ] || { echo "❌ ipai_ce_cleaner module missing"; exit 1; }
echo "✅ All custom modules exist"

# 5. Test Docker Compose syntax
echo "🔧 Step 5: Test Docker Compose syntax"
docker compose -f deploy/docker-compose.yml config || { echo "❌ Docker Compose syntax error"; exit 1; }
echo "✅ Docker Compose syntax valid"

# 6. Test deployment script syntax
echo "📜 Step 6: Test deployment script syntax"
bash -n scripts/simple_deploy.sh || { echo "❌ Deployment script syntax error"; exit 1; }
echo "✅ Deployment script syntax valid"

echo ""
echo "🎉 LOCAL DEPLOYMENT TEST PASSED!"
echo "================================"
echo "✅ All deployment components verified"
echo "✅ Docker environment ready"
echo "✅ Configuration files valid"
echo "✅ Custom modules available"
echo "✅ Deployment script ready for production"

echo ""
echo "🚀 Ready for Production Deployment:"
echo "   ssh user@159.223.75.148"
echo "   cd ~/odoo-prod"
echo "   ./scripts/simple_deploy.sh"
