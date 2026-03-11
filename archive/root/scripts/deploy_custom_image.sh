#!/bin/bash
# Final Production Deployment Script for Custom Odoo Image
# DigitalOcean VPS Deployment - Exit Code 0 Success Criteria

set -e  # Exit immediately on any command failure

# Define Variables
ODOO_DB_NAME="odoo"
ODOO_MODULES="ipai_finance_ppm,ipai_equipment,ipai_expense,ipai_finance_monthly_closing,ipai_ocr_expense,ipai_ce_cleaner"
COMPOSE_FILE="docker-compose.yml"
IMAGE_TAG="ghcr.io/jgtolentino/odoo-ce:latest"

echo "🚀 Starting Custom Odoo Image Deployment"
echo "=========================================="

# 1. Navigate to project directory
echo "📁 Step 1: Navigating to project directory"
cd ~/odoo-prod || { echo "❌ Failed to navigate to odoo-prod directory"; exit 1; }
echo "✅ Current directory: $(pwd)"

# 2. Authenticate and Pull the new custom image (GHCR)
echo "🐳 Step 2: Pulling latest custom Odoo image"
echo "📦 Image: $IMAGE_TAG"
docker compose -f $COMPOSE_FILE pull odoo || { echo "❌ Failed to pull Odoo image"; exit 1; }
echo "✅ Custom image pulled successfully"

# 3. Restart/Swap the Container (Atomic Deployment)
echo "🔄 Step 3: Performing atomic container swap"
docker compose -f $COMPOSE_FILE up -d --force-recreate odoo || { echo "❌ Failed to restart Odoo container"; exit 1; }
echo "✅ Container swapped successfully"

# 4. Wait for Odoo to become healthy
echo "⏳ Step 4: Waiting for Odoo health check"
max_attempts=30
attempt=1
while [ $attempt -le $max_attempts ]; do
    if docker compose -f $COMPOSE_FILE ps odoo | grep -q "healthy"; then
        echo "✅ Odoo container is healthy"
        break
    fi
    echo "⏰ Waiting for Odoo health... ($attempt/$max_attempts)"
    sleep 10
    attempt=$((attempt + 1))
done

if [ $attempt -gt $max_attempts ]; then
    echo "❌ Odoo container failed to become healthy"
    exit 1
fi

# 5. Apply Database Migrations (Schema Update)
echo "🗃️ Step 5: Applying database migrations"
echo "📊 Modules: $ODOO_MODULES"
docker compose -f $COMPOSE_FILE exec odoo odoo-bin -c /etc/odoo.conf -d $ODOO_DB_NAME \
    -u $ODOO_MODULES --stop-after-init || { echo "❌ Database migration failed"; exit 1; }
echo "✅ Database migrations applied successfully"

# 6. Final Health Check Validation
echo "🏥 Step 6: Performing final health check"
curl -f http://localhost:8069/web/health || { echo "❌ Health check failed"; exit 1; }
echo "✅ Health check passed - HTTP 200 response"

# 7. Verify deployment success
echo "✅ Step 7: Verifying deployment completion"
echo "📋 Deployment Summary:"
echo "   - Custom Image: $IMAGE_TAG"
echo "   - Database: $ODOO_DB_NAME"
echo "   - Modules Updated: $ODOO_MODULES"
echo "   - Health Status: ✅ Healthy"

echo ""
echo "🎉 DEPLOYMENT SUCCESSFUL!"
echo "=========================="
echo "All commands completed with exit code 0"
echo "Custom Odoo image is now running in production"
echo "WBS/PPM schema updates have been applied"

# Exit with success code (DigitalOcean standard)
exit 0
