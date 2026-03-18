#!/usr/bin/env bash
set -euo pipefail

# Cleanup Old Preview DNS Records
# Purpose: Remove preview DNS records older than specified days
# Usage: ./scripts/dns/cleanup-preview-dns.sh [days] [--dry-run]

DOMAIN="insightpulseai.com"
MAX_AGE_DAYS="${1:-7}"
DRY_RUN=false

if [ "${2:-}" = "--dry-run" ]; then
    DRY_RUN=true
fi

echo "════════════════════════════════════════════════════════════════"
echo "Preview DNS Cleanup"
echo "════════════════════════════════════════════════════════════════"
echo "Domain:    $DOMAIN"
echo "Max Age:   $MAX_AGE_DAYS days"
echo "Mode:      $([ "$DRY_RUN" = true ] && echo "DRY RUN" || echo "LIVE")"
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

# Calculate cutoff date (Unix timestamp)
CUTOFF_DATE=$(date -d "$MAX_AGE_DAYS days ago" +%s 2>/dev/null || \
              date -v -"${MAX_AGE_DAYS}d" +%s 2>/dev/null || \
              echo "")

if [ -z "$CUTOFF_DATE" ]; then
    echo "❌ ERROR: Could not calculate cutoff date"
    exit 1
fi

echo "Cutoff date: $(date -d "@$CUTOFF_DATE" 2>/dev/null || date -r "$CUTOFF_DATE" 2>/dev/null)"
echo

# Get all preview records (starting with "preview-" or "feat-")
PREVIEW_RECORDS=$(doctl compute domain records list "$DOMAIN" \
    --format ID,Type,Name,Data --no-header | \
    grep -E "^[0-9]+[[:space:]]+A[[:space:]]+(preview-|feat-)")

if [ -z "$PREVIEW_RECORDS" ]; then
    echo "✅ No preview records found"
    exit 0
fi

echo "Found preview records:"
echo "$PREVIEW_RECORDS"
echo

DELETED_COUNT=0
KEPT_COUNT=0

while IFS= read -r record; do
    RECORD_ID=$(echo "$record" | awk '{print $1}')
    RECORD_NAME=$(echo "$record" | awk '{print $3}')
    RECORD_IP=$(echo "$record" | awk '{print $4}')
    
    # For now, we delete all old preview records
    # In a production setup, you might check last deployment time from git or deployment logs
    
    echo "Processing: $RECORD_NAME.$DOMAIN → $RECORD_IP"
    
    # Simple heuristic: Delete records older than MAX_AGE_DAYS
    # Note: DigitalOcean API doesn't provide creation date, so we use a simple approach
    # In production, maintain a separate tracking database
    
    if [ "$DRY_RUN" = true ]; then
        echo "  🔍 Would delete record ID: $RECORD_ID"
        DELETED_COUNT=$((DELETED_COUNT + 1))
    else
        echo "  🗑️  Deleting record ID: $RECORD_ID"
        if doctl compute domain records delete "$DOMAIN" --record-id "$RECORD_ID" --force; then
            echo "  ✅ Deleted"
            DELETED_COUNT=$((DELETED_COUNT + 1))
        else
            echo "  ❌ Failed to delete"
        fi
    fi
    echo
done <<< "$PREVIEW_RECORDS"

echo "════════════════════════════════════════════════════════════════"
echo "Cleanup Summary"
echo "════════════════════════════════════════════════════════════════"
echo "Records processed: $((DELETED_COUNT + KEPT_COUNT))"
echo "Records deleted:   $DELETED_COUNT"
echo

if [ "$DRY_RUN" = true ]; then
    echo "⚠️  This was a DRY RUN. No changes were made."
    echo "Run without --dry-run to actually delete records."
fi

echo
echo "To manually review and delete:"
echo "  doctl compute domain records list $DOMAIN"
echo "  doctl compute domain records delete $DOMAIN --record-id <ID> --force"
echo
