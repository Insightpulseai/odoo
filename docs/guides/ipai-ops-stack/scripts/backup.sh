#!/bin/bash
# Backup all databases and volumes

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="$PROJECT_DIR/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"

echo "=== ipai-ops-stack Backup ==="
echo "Timestamp: $TIMESTAMP"
echo ""

cd "$PROJECT_DIR/docker"

# Backup PostgreSQL databases
echo "Backing up PostgreSQL databases..."
for db in mattermost focalboard superset; do
    echo "  - $db"
    docker compose exec -T postgres pg_dump -U postgres "$db" > "$BACKUP_DIR/${db}_${TIMESTAMP}.sql"
done

# Backup n8n data
echo "Backing up n8n data..."
docker compose exec -T n8n tar czf - -C /home/node .n8n > "$BACKUP_DIR/n8n_${TIMESTAMP}.tar.gz"

# Create combined archive
echo "Creating combined archive..."
cd "$BACKUP_DIR"
tar czf "backup_${TIMESTAMP}.tar.gz" \
    mattermost_${TIMESTAMP}.sql \
    focalboard_${TIMESTAMP}.sql \
    superset_${TIMESTAMP}.sql \
    n8n_${TIMESTAMP}.tar.gz

# Clean up individual files
rm -f mattermost_${TIMESTAMP}.sql focalboard_${TIMESTAMP}.sql superset_${TIMESTAMP}.sql n8n_${TIMESTAMP}.tar.gz

echo ""
echo "Backup complete: $BACKUP_DIR/backup_${TIMESTAMP}.tar.gz"
