#!/bin/bash

# IPAI Finance PPM Dashboard Deployment Script
# This script deploys the ECharts dashboard module to the live Odoo instance

echo "=== IPAI Finance PPM Dashboard Deployment ==="
echo ""

# Check if we're in the right directory
if [ ! -f "odoo-bin" ]; then
    echo "❌ Error: Must run from odoo-ce root directory"
    exit 1
fi

echo "✅ Found odoo-ce repository"

# Check if module exists
if [ ! -d "addons/ipai_finance_ppm_dashboard" ]; then
    echo "❌ Error: Module not found at addons/ipai_finance_ppm_dashboard"
    exit 1
fi

echo "✅ Module structure verified"

# Deploy to server
echo ""
echo "🚀 Deploying to live server..."
echo ""

# SSH to server and deploy
ssh root@erp.insightpulseai.net << 'EOF'
cd /opt/odoo-ce
git pull origin feature/add-expense-equipment-prd
./scripts/deploy-odoo-modules.sh ipai_finance_ppm_dashboard
sudo systemctl restart odoo
EOF

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📋 Next steps:"
echo "1. Navigate to: https://erp.insightpulseai.net"
echo "2. Login with admin credentials"
echo "3. Go to Apps menu"
echo "4. Click 'Update Apps List' (⟳ icon top-right)"
echo "5. Search for 'IPAI Finance PPM Dashboard'"
echo "6. Click 'Install' button"
echo ""
echo "🎯 After installation:"
echo "- New menu 'Finance PPM Dashboard' should appear in top navigation"
echo "- Click to see Gantt chart + BIR calendar heatmap"
echo "- Both charts powered by ECharts with demo data"
echo ""
echo "📊 Features:"
echo "- November 2025 Month-End Close Gantt chart"
echo "- BIR Filing Calendar 2026 heatmap"
echo "- Real-time interactive charts"
echo "- Odoo-native integration (no external app needed)"
