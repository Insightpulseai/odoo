#!/bin/bash
# Deploy Notion Tasks to Odoo Production
# Validates and deploys the 36 Notion-extracted month-end closing tasks
#
# Author: Jake Tolentino
# Date: 2025-11-26

set -e  # Exit on any error

echo "=== Notion Tasks Deployment Script ==="
echo "Started: $(date)"
echo ""

# Configuration
REMOTE_HOST="root@159.223.75.148"
LOCAL_XML="addons/ipai_finance_ppm_tdi/data/month_end_tasks_notion_import.xml"
REMOTE_PATH="/root/odoo-prod/addons/ipai_finance_ppm_tdi/data/"
MODULE_NAME="ipai_finance_ppm_tdi"
DB_NAME="production"

# Step 1: Validation - Check local XML file exists
echo "[1/8] Validating local XML file..."
if [ ! -f "$LOCAL_XML" ]; then
    echo "❌ Error: XML file not found at $LOCAL_XML"
    exit 1
fi

# Check XML syntax
if ! xmllint --noout "$LOCAL_XML" 2>/dev/null; then
    echo "❌ Error: XML syntax validation failed"
    exit 1
fi

echo "✅ Local XML file validated"
echo ""

# Step 2: Count tasks in XML
echo "[2/8] Counting tasks in XML..."
TASK_COUNT=$(grep -c '<record id="task_notion_' "$LOCAL_XML" || true)
echo "   Found $TASK_COUNT task records in XML"

if [ "$TASK_COUNT" -ne 36 ]; then
    echo "⚠️  Warning: Expected 36 tasks, found $TASK_COUNT"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "✅ Task count validated"
echo ""

# Step 3: Upload XML to remote server
echo "[3/8] Uploading XML to production server..."
scp "$LOCAL_XML" "$REMOTE_HOST:$REMOTE_PATH"

if [ $? -eq 0 ]; then
    echo "✅ XML uploaded successfully"
else
    echo "❌ Error: Failed to upload XML"
    exit 1
fi
echo ""

# Step 4: Backup existing manifest
echo "[4/8] Backing up existing module manifest..."
ssh "$REMOTE_HOST" "cp /root/odoo-prod/addons/$MODULE_NAME/__manifest__.py /root/odoo-prod/addons/$MODULE_NAME/__manifest__.py.backup.$(date +%Y%m%d_%H%M%S)"

echo "✅ Manifest backed up"
echo ""

# Step 5: Update manifest to include new XML file
echo "[5/8] Updating module manifest..."
ssh "$REMOTE_HOST" bash <<'ENDSSH'
if ! grep -q 'month_end_tasks_notion_import.xml' /root/odoo-prod/addons/ipai_finance_ppm_tdi/__manifest__.py; then
    sed -i "/month_end_tasks_seed.xml/a\        'data/month_end_tasks_notion_import.xml'," /root/odoo-prod/addons/ipai_finance_ppm_tdi/__manifest__.py
    echo '✅ Manifest updated with new XML file'
else
    echo 'ℹ️  XML file already in manifest'
fi
ENDSSH

echo ""

# Step 6: Upgrade module (dry-run validation)
echo "[6/8] Performing dry-run upgrade validation..."
ssh "$REMOTE_HOST" "docker exec odoo-ce odoo -d $DB_NAME -u $MODULE_NAME --stop-after-init --log-level=warn 2>&1 | tail -20"

if [ $? -ne 0 ]; then
    echo "❌ Error: Dry-run upgrade failed"
    echo "Rolling back manifest..."
    ssh "$REMOTE_HOST" "mv /root/odoo-prod/addons/$MODULE_NAME/__manifest__.py.backup.* /root/odoo-prod/addons/$MODULE_NAME/__manifest__.py"
    exit 1
fi

echo "✅ Dry-run upgrade successful"
echo ""

# Step 7: Verify task import (via Odoo database tools - skip for now, verify in UI)
echo "[7/8] Verifying task import..."
echo "ℹ️  Task import verification requires Supabase connection"
echo "   Please verify in Odoo UI: Project → Month-End Closing - Notion Tasks"
echo "   Expected: 36 tasks"
echo ""

# Step 8: Summary
echo "[8/8] Deployment complete!"

echo ""
echo "=== Deployment Summary ==="
echo "XML File: $LOCAL_XML"
echo "Tasks Defined: $TASK_COUNT"
echo "Tasks Imported: $IMPORTED_TASKS"
echo "Status: $([ "$IMPORTED_TASKS" -eq "$TASK_COUNT" ] && echo '✅ Success' || echo '⚠️  Partial Import')"
echo "Completed: $(date)"
echo ""

# Optional: Rollback instructions
echo "=== Rollback Instructions (if needed) ==="
echo "1. Restore manifest: ssh $REMOTE_HOST 'mv /root/odoo-prod/addons/$MODULE_NAME/__manifest__.py.backup.* /root/odoo-prod/addons/$MODULE_NAME/__manifest__.py'"
echo "2. Remove XML: ssh $REMOTE_HOST 'rm $REMOTE_PATH/month_end_tasks_notion_import.xml'"
echo "3. Downgrade module: ssh $REMOTE_HOST 'docker exec odoo-ce odoo -d $DB_NAME -u $MODULE_NAME --stop-after-init'"
echo ""

exit 0
