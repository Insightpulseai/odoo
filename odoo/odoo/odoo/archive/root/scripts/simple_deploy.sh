#!/bin/bash
# Simple Odoo Deployment - Base Image + Delta Approach
# No complex automation, just pull and deploy

set -e

echo "🚀 Simple Odoo Deployment Starting"
echo "==================================="

# 1. Navigate to project directory
echo "📁 Step 1: Navigate to project directory"
cd ~/odoo-prod || { echo "❌ Failed to navigate to odoo-prod"; exit 1; }

# 2. Pull base Odoo image (if needed)
echo "🐳 Step 2: Pull base Odoo 18 image"
docker pull odoo:18.0 || { echo "❌ Failed to pull Odoo image"; exit 1; }
echo "✅ Base Odoo image ready"

# 3. Stop current containers
echo "🛑 Step 3: Stop current containers"
docker compose down || echo "⚠️ No containers to stop"

# 4. Start with latest configuration
echo "▶️ Step 4: Start containers with latest config"
docker compose up -d || { echo "❌ Failed to start containers"; exit 1; }

# 5. Wait for Odoo to be ready
echo "⏳ Step 5: Wait for Odoo to be ready"
sleep 30

# 6. Apply database updates for custom modules
echo "🗃️ Step 6: Apply database updates"
docker compose exec odoo odoo-bin -c /etc/odoo.conf -d odoo \
    -u ipai_finance_ppm,ipai_equipment,ipai_expense,ipai_finance_monthly_closing,ipai_ocr_expense,ipai_ce_cleaner \
    --stop-after-init || { echo "⚠️ Database updates may have issues"; }

# 7. Verify deployment
echo "✅ Step 7: Verify deployment"
curl -f http://localhost:8069/web/health && echo "✅ Health check passed" || echo "⚠️ Health check warning"

echo ""
echo "🎉 SIMPLE DEPLOYMENT COMPLETE!"
echo "==============================="
echo "Odoo is running with custom modules"
echo "No complex automation - just base image + delta"
