#!/bin/bash
#
# Finance PPM Schema Fix Script
# ===============================
# Fixes missing database columns in project.task table
# caused by module update not being applied
#
# Error: psycopg2.errors.UndefinedColumn: column project_task.finance_code does not exist
#

set -euo pipefail

echo "========================================="
echo "Finance PPM Schema Fix"
echo "========================================="
echo ""

# Check if running on Odoo server
if [ ! -f "/etc/odoo/odoo.conf" ]; then
    echo "⚠️  WARNING: Not on Odoo server"
    echo ""
    echo "This script must run on: odoo-erp-prod (159.223.75.148)"
    echo ""
    echo "Run the following commands on the Odoo server:"
    echo ""
    echo "1. Stop Odoo service:"
    echo "   sudo systemctl stop odoo"
    echo ""
    echo "2. Upgrade module:"
    echo "   sudo -u odoo odoo -c /etc/odoo/odoo.conf -d production -u ipai_finance_ppm --stop-after-init"
    echo ""
    echo "3. Start Odoo service:"
    echo "   sudo systemctl start odoo"
    echo ""
    echo "4. Verify schema:"
    echo "   sudo -u postgres psql production -c \"\\d project_task\" | grep finance_code"
    echo ""
    exit 1
fi

echo "Running on Odoo server - proceeding with upgrade..."
echo ""

# Stop Odoo
echo "[1/5] Stopping Odoo service..."
sudo systemctl stop odoo
echo "✓ Odoo stopped"
echo ""

# Backup database
echo "[2/5] Creating database backup..."
BACKUP_FILE="/var/backups/odoo/production_$(date +%Y%m%d_%H%M%S).sql"
sudo -u postgres pg_dump production > "$BACKUP_FILE"
echo "✓ Backup created: $BACKUP_FILE"
echo ""

# Upgrade module
echo "[3/5] Upgrading ipai_finance_ppm module..."
sudo -u odoo odoo -c /etc/odoo/odoo.conf -d production -u ipai_finance_ppm --stop-after-init
if [ $? -eq 0 ]; then
    echo "✓ Module upgraded successfully"
else
    echo "✗ Module upgrade failed"
    echo ""
    echo "Rolling back - starting Odoo with old schema..."
    sudo systemctl start odoo
    exit 1
fi
echo ""

# Verify schema
echo "[4/5] Verifying database schema..."
COLUMNS=$(sudo -u postgres psql production -c "SELECT column_name FROM information_schema.columns WHERE table_name = 'project_task' AND column_name LIKE 'finance%' OR column_name LIKE 'x_%';" -t)

if echo "$COLUMNS" | grep -q "finance_code"; then
    echo "✓ finance_code column exists"
else
    echo "✗ finance_code column missing - upgrade may have failed"
fi

if echo "$COLUMNS" | grep -q "x_external_key"; then
    echo "✓ x_external_key column exists"
else
    echo "✗ x_external_key column missing"
fi

echo ""
echo "All finance-related columns:"
echo "$COLUMNS"
echo ""

# Start Odoo
echo "[5/5] Starting Odoo service..."
sudo systemctl start odoo
echo "✓ Odoo started"
echo ""

# Wait for Odoo to be ready
echo "Waiting for Odoo to be ready..."
sleep 10

# Test connection
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8069 | grep -q "200\|303"; then
    echo "✓ Odoo is responding"
else
    echo "⚠️  Odoo may not be fully started yet - check logs:"
    echo "   sudo journalctl -u odoo -f"
fi

echo ""
echo "========================================="
echo "Schema Fix Complete!"
echo "========================================="
echo ""
echo "Verification steps:"
echo "1. Check Odoo logs for errors:"
echo "   sudo journalctl -u odoo -n 50"
echo ""
echo "2. Test Finance PPM dashboard:"
echo "   https://erp.insightpulseai.net/ipai/finance/ppm"
echo ""
echo "3. Verify project tasks load without errors"
echo ""
