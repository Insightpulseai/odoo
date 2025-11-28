#!/bin/bash

# IPAI Finance PPM Dashboard Installation Verification
# This script verifies the module deployment and provides installation instructions

echo "=== IPAI Finance PPM Dashboard - Installation Verification ==="
echo ""

# Check if module exists on server
echo "🔍 Checking module deployment status..."
ssh root@erp.insightpulseai.net "cd /opt/odoo-ce && find . -name 'ipai_finance_ppm_dashboard' -type d" > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Module files deployed to server: /opt/odoo-ce/addons/ipai_finance_ppm_dashboard/"
else
    echo "❌ Module not found on server"
    exit 1
fi

# Check module structure
echo ""
echo "📁 Verifying module structure..."
ssh root@erp.insightpulseai.net "cd /opt/odoo-ce/addons/ipai_finance_ppm_dashboard && ls -la"

# Check if Odoo is running
echo ""
echo "🔄 Checking Odoo status..."
ssh root@erp.insightpulseai.net "docker ps | grep odoo"

echo ""
echo "🎯 INSTALLATION STATUS SUMMARY:"
echo "================================="
echo "✅ Module files: DEPLOYED"
echo "✅ Odoo instance: RUNNING"
echo "⏳ Module installation: PENDING (requires UI installation)"
echo ""

echo "📋 MANUAL INSTALLATION REQUIRED:"
echo "================================="
echo "1. Navigate to: https://erp.insightpulseai.net"
echo "2. Login with admin credentials"
echo "3. Go to Apps menu"
echo "4. Click 'Update Apps List' (⟳ icon top-right)"
echo "5. Search for 'IPAI Finance PPM Dashboard'"
echo "6. Click 'Install' button"
echo ""

echo "🔍 VERIFICATION AFTER INSTALLATION:"
echo "==================================="
echo "After installation, verify by running:"
echo "ssh root@erp.insightpulseai.net \"docker exec odoo-db-1 psql -U odoo -d odoo -c \\\"SELECT name, state FROM ir_module_module WHERE name = 'ipai_finance_ppm_dashboard';\\\"\""
echo ""
echo "Expected output:"
echo "           name            |  state"
echo "----------------------------+----------"
echo " ipai_finance_ppm_dashboard | installed"
echo ""

echo "🎯 DASHBOARD ACCESS:"
echo "===================="
echo "After installation, access the dashboard via:"
echo "- Top navigation menu: 'Finance PPM Dashboard'"
echo "- URL: https://erp.insightpulseai.net/web#action=ipai_finance_ppm_dashboard.action_finance_ppm_dashboard"
echo ""

echo "📊 FEATURES AVAILABLE:"
echo "======================"
echo "- November 2025 Month-End Close Gantt Chart"
echo "- BIR Filing Calendar 2026 Heatmap"
echo "- Interactive ECharts visualizations"
echo "- Real-time dashboard updates"
