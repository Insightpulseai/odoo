#!/usr/bin/env bash
set -euo pipefail

# Finance PPM Golden Snapshot Restore Script
# Purpose: Restore production database to canonical Finance PPM state
# WARNING: This will overwrite the current production database!

BACKUP_FILE=${1:-}
DB_CONTAINER=${DB_CONTAINER:-odoo-db-1}
DB_NAME=${DB_NAME:-odoo}
DB_USER=${DB_USER:-odoo}

if [ -z "$BACKUP_FILE" ]; then
    echo "❌ Usage: $0 <backup_file>"
    echo ""
    echo "Available golden snapshots:"
    ssh root@159.223.75.148 "ls -lh /root/backups/odoo_finance_ppm_golden_*.sql"
    echo ""
    echo "Example:"
    echo "  $0 /root/backups/odoo_finance_ppm_golden_20251227_022029.sql"
    exit 1
fi

echo "⚠️  WARNING: This will restore the production database to golden snapshot!"
echo ""
echo "   Backup file: $BACKUP_FILE"
echo "   Target database: $DB_NAME"
echo "   Container: $DB_CONTAINER"
echo ""
read -p "Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "❌ Restore cancelled"
    exit 1
fi

echo ""
echo "🔄 Restoring database from golden snapshot..."

ssh root@159.223.75.148 "docker exec -i $DB_CONTAINER psql -U $DB_USER -d postgres -c 'DROP DATABASE IF EXISTS $DB_NAME;'"
ssh root@159.223.75.148 "docker exec -i $DB_CONTAINER psql -U $DB_USER -d postgres -c 'CREATE DATABASE $DB_NAME;'"
ssh root@159.223.75.148 "docker exec -i $DB_CONTAINER psql -U $DB_USER -d $DB_NAME" < "$BACKUP_FILE"

echo ""
echo "✅ Database restored from golden snapshot"
echo ""
echo "🔍 Running health check..."
./scripts/finance_ppm_health_check.sh $DB_NAME

exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo ""
    echo "✅ Restore successful! Health check passed: 8/12/144/36/36"
else
    echo ""
    echo "❌ Health check failed after restore"
    exit 1
fi
