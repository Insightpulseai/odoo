#!/bin/bash
# Restore from backup

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <backup_file.tar.gz>"
    exit 1
fi

BACKUP_FILE="$1"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
TEMP_DIR=$(mktemp -d)

if [ ! -f "$BACKUP_FILE" ]; then
    echo "Error: Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo "=== ipai-ops-stack Restore ==="
echo "Backup file: $BACKUP_FILE"
echo ""

# Extract backup
echo "Extracting backup..."
tar xzf "$BACKUP_FILE" -C "$TEMP_DIR"

cd "$PROJECT_DIR/docker"

# Restore PostgreSQL databases
echo "Restoring PostgreSQL databases..."
for db in mattermost focalboard superset; do
    if [ -f "$TEMP_DIR/${db}_*.sql" ]; then
        echo "  - $db"
        docker compose exec -T postgres psql -U postgres "$db" < "$TEMP_DIR/${db}_"*.sql
    fi
done

# Restore n8n data
if ls "$TEMP_DIR"/n8n_*.tar.gz 1> /dev/null 2>&1; then
    echo "Restoring n8n data..."
    docker compose exec -T n8n tar xzf - -C /home/node < "$TEMP_DIR"/n8n_*.tar.gz
fi

# Clean up
rm -rf "$TEMP_DIR"

echo ""
echo "Restore complete. You may need to restart services:"
echo "  ./scripts/down.sh && ./scripts/up.sh"
