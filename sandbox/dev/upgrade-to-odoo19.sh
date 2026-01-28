#!/bin/bash
# Upgrade from Odoo 18 to Odoo 19 EE parity image

cd ~/Documents/GitHub/odoo-ce/sandbox/dev

echo "🛑 Stopping old containers..."
docker compose down

echo "🗑️  Removing old Odoo 18 image..."
docker rmi odoo:18.0 2>/dev/null || echo "   (no old image to remove)"

echo "📥 Pulling Odoo 19.0 EE parity image..."
docker compose pull

echo "🚀 Starting Odoo 19.0 EE parity..."
docker compose up -d

echo "⏳ Waiting for services..."
sleep 15

echo "✅ Checking status..."
docker compose ps

echo ""
echo "🌐 Access Odoo 19.0 at: http://localhost:9069/web/login"
echo "   Clear browser cache: Command + Shift + R"
