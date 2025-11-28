#!/bin/bash

# Direct deployment script for IPAI Finance PPM Dashboard
# This copies the module directly to the server

echo "=== Direct Deployment: IPAI Finance PPM Dashboard ==="
echo ""

# Check if module exists locally
if [ ! -d "addons/ipai_finance_ppm_dashboard" ]; then
    echo "❌ Error: Module not found locally"
    exit 1
fi

echo "✅ Module found locally"

# Create module directory on server
echo "📁 Creating module directory on server..."
ssh root@erp.insightpulseai.net "mkdir -p /opt/odoo-ce/addons/ipai_finance_ppm_dashboard"

# Copy module files
echo "📤 Copying module files..."
scp -r addons/ipai_finance_ppm_dashboard/* root@erp.insightpulseai.net:/opt/odoo-ce/addons/ipai_finance_ppm_dashboard/

# Restart Odoo container
echo "🔄 Restarting Odoo container..."
ssh root@erp.insightpulseai.net "cd /opt/odoo-ce && docker compose restart odoo"

echo ""
echo "✅ Direct deployment complete!"
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
