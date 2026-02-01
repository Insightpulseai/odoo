#!/usr/bin/env bash
set -e

# -----------------------------------------------------------------------------
# Production Backup Script (Template)
# -----------------------------------------------------------------------------
# Purpose: Create a read-only dump of the production database for staging refresh.
# Usage:   Run this from a machine with SSH access to Prod (or on Prod itself).
# -----------------------------------------------------------------------------

PROD_HOST="${PROD_HOST:-erp.insightpulseai.com}"
PROD_DB="${PROD_DB:-odoo}"
PROD_USER="${PROD_USER:-odoo}"
BACKUP_DIR="${BACKUP_DIR:-./backups}"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"
FILENAME="$BACKUP_DIR/prod_dump_$DATE.sql"

echo "Creating backup of '$PROD_DB' from '$PROD_HOST'..."
# Note: Adjust pg_dump command based on your access method (SSH tunnel, direct, or docker exec)

# Example (SSH Tunnel/Remote):
# ssh user@$PROD_HOST "pg_dump -U $PROD_USER -d $PROD_DB --format=c --no-owner --no-acl" > "$FILENAME"

# Example (Docker Exec on Prod Server):
# docker exec -t odoo-db pg_dump -U $PROD_USER -d $PROD_DB --format=c --no-owner --no-acl > "$FILENAME"

echo "Backup saved to: $FILENAME"
echo "To restore to staging: Copy this file to dev machine and run restore."
