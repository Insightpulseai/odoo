#!/usr/bin/env bash
set -euo pipefail

# Backup DNS Configuration
# Purpose: Export current DNS records for disaster recovery
# Usage: ./scripts/dns/backup-dns-config.sh

DOMAIN="insightpulseai.com"
BACKUP_DIR="${BACKUP_DIR:-docs/evidence/dns-backups}"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

echo "════════════════════════════════════════════════════════════════"
echo "DNS Configuration Backup"
echo "════════════════════════════════════════════════════════════════"
echo

# Check prerequisites
if ! command -v doctl &> /dev/null; then
    echo "❌ ERROR: doctl CLI not found"
    exit 1
fi

if ! doctl account get &> /dev/null; then
    echo "❌ ERROR: doctl not authenticated"
    exit 1
fi

# Create backup directory
mkdir -p "$BACKUP_DIR"

BACKUP_FILE="$BACKUP_DIR/dns-backup-${TIMESTAMP}.json"
LATEST_LINK="$BACKUP_DIR/dns-backup-latest.json"

echo "Backup file: $BACKUP_FILE"
echo

# Export DNS records in JSON format
echo "Exporting DNS records..."
doctl compute domain records list "$DOMAIN" --output json > "$BACKUP_FILE"

# Also export in human-readable format
echo "Creating human-readable format..."
doctl compute domain records list "$DOMAIN" \
    --format ID,Type,Name,Data,Priority,TTL > "${BACKUP_FILE%.json}.txt"

# Create symlink to latest
ln -sf "$(basename "$BACKUP_FILE")" "$LATEST_LINK"
ln -sf "$(basename "${BACKUP_FILE%.json}.txt")" "${LATEST_LINK%.json}.txt"

echo "✅ Backup complete"
echo

# Show summary
RECORD_COUNT=$(jq '. | length' "$BACKUP_FILE")
echo "Records backed up: $RECORD_COUNT"
echo

echo "Files created:"
echo "  - JSON: $BACKUP_FILE"
echo "  - TXT:  ${BACKUP_FILE%.json}.txt"
echo "  - Link: $LATEST_LINK"
echo

echo "═══════════════════════════════════════════════════════════════"
echo "Record Summary:"
echo "═══════════════════════════════════════════════════════════════"

jq -r '.[] | "\(.type)\t\(.name)\t\(.data)"' "$BACKUP_FILE" | column -t

echo
echo "═══════════════════════════════════════════════════════════════"
echo "To restore from backup:"
echo "═══════════════════════════════════════════════════════════════"
echo
echo "1. Review backup file: cat $BACKUP_FILE"
echo
echo "2. Restore individual record:"
echo "   jq -r '.[] | select(.name == \"erp\")' $BACKUP_FILE"
echo "   doctl compute domain records create $DOMAIN \\"
echo "     --record-type A \\"
echo "     --record-name erp \\"
echo "     --record-data 178.128.112.214"
echo
echo "3. Full restore (use with caution):"
echo "   ./scripts/dns/restore-dns-from-backup.sh $BACKUP_FILE"
echo
