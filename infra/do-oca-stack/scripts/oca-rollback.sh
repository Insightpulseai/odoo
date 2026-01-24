#!/usr/bin/env bash
# Rollback script for OCA stack deployment
# Restores to a previous git commit or backup
#
# Usage:
#   ./oca-rollback.sh git <commit-sha>      # Rollback code to specific commit
#   ./oca-rollback.sh backup <backup-dir>   # Restore database from backup
#   ./oca-rollback.sh list                  # List available rollback points
#
# Examples:
#   ./oca-rollback.sh list
#   ./oca-rollback.sh git abc123
#   ./oca-rollback.sh backup backups/20260124-120000

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[$(date +%H:%M:%S)]${NC} $*"; }
warn() { echo -e "${YELLOW}[$(date +%H:%M:%S)] WARN:${NC} $*"; }
error() { echo -e "${RED}[$(date +%H:%M:%S)] ERROR:${NC} $*" >&2; }

usage() {
  cat <<EOF
Usage: $0 <command> [args]

Commands:
  list                    List available rollback points
  git <commit-sha>        Rollback code to specific git commit
  backup <backup-dir>     Restore database from backup directory

Examples:
  $0 list
  $0 git abc1234
  $0 backup backups/20260124-120000
EOF
  exit 1
}

# -----------------------------------------
# List available rollback points
# -----------------------------------------
cmd_list() {
  echo -e "${YELLOW}=== Git History (last 10 commits) ===${NC}"
  git log --oneline -n 10

  echo ""
  echo -e "${YELLOW}=== Local Backups ===${NC}"
  if [[ -d backups ]]; then
    ls -1t backups/ 2>/dev/null | head -10 || echo "(no backups found)"
  else
    echo "(backups directory not found)"
  fi

  echo ""
  echo -e "${YELLOW}=== Current State ===${NC}"
  echo "HEAD: $(git rev-parse --short HEAD)"
  echo "Branch: $(git branch --show-current)"
  docker compose ps --format "table {{.Name}}\t{{.Status}}" 2>/dev/null || true
}

# -----------------------------------------
# Git rollback
# -----------------------------------------
cmd_git() {
  local commit="${1:-}"

  if [[ -z "$commit" ]]; then
    error "No commit SHA provided"
    usage
  fi

  # Verify commit exists
  if ! git cat-file -t "$commit" &>/dev/null; then
    error "Invalid commit: $commit"
    exit 1
  fi

  log "Rolling back to commit: $commit"

  # Create backup of current state
  BACKUP_SHA=$(git rev-parse --short HEAD)
  log "Current HEAD: $BACKUP_SHA (save this to undo rollback)"

  # Pre-rollback backup
  log "Creating pre-rollback database backup..."
  BACKUP_DIR="backups/pre-rollback-$(date +%Y%m%d-%H%M%S)"
  mkdir -p "$BACKUP_DIR"
  docker compose exec -T db pg_dump -U odoo -Fc odoo > "$BACKUP_DIR/odoo.dump" || warn "Database backup failed"

  # Checkout commit
  log "Checking out $commit..."
  git checkout "$commit"

  # Sync OCA repos if lock file changed
  if [[ -f oca.lock ]]; then
    log "Syncing OCA repos to match lock file..."
    make fetch || warn "OCA fetch had warnings"
  fi

  # Restart services
  log "Restarting services..."
  docker compose pull --quiet
  docker compose up -d

  # Wait for health
  log "Waiting for services to be healthy..."
  sleep 10

  # Verify
  log "Running verification..."
  ./scripts/oca-verify.sh || warn "Some verification checks failed"

  echo ""
  echo -e "${GREEN}=== ROLLBACK COMPLETE ===${NC}"
  echo "Rolled back to: $commit"
  echo "Pre-rollback backup: $BACKUP_DIR"
  echo "To undo: ./oca-rollback.sh git $BACKUP_SHA"
}

# -----------------------------------------
# Backup restore
# -----------------------------------------
cmd_backup() {
  local backup_dir="${1:-}"

  if [[ -z "$backup_dir" ]]; then
    error "No backup directory provided"
    usage
  fi

  if [[ ! -d "$backup_dir" ]]; then
    error "Backup directory not found: $backup_dir"
    exit 1
  fi

  local dump_file="$backup_dir/odoo.dump"
  local sql_file="$backup_dir/odoo.sql"
  local sql_gz_file="$backup_dir/odoo.sql.gz"

  # Find the backup file
  if [[ -f "$dump_file" ]]; then
    RESTORE_FILE="$dump_file"
    RESTORE_CMD="pg_restore -U odoo -d odoo --clean --if-exists"
  elif [[ -f "$sql_file" ]]; then
    RESTORE_FILE="$sql_file"
    RESTORE_CMD="psql -U odoo -d odoo"
  elif [[ -f "$sql_gz_file" ]]; then
    RESTORE_FILE="$sql_gz_file"
    RESTORE_CMD="zcat | psql -U odoo -d odoo"
  else
    error "No valid backup file found in $backup_dir (expected odoo.dump, odoo.sql, or odoo.sql.gz)"
    exit 1
  fi

  log "Restoring from: $RESTORE_FILE"

  # Create pre-restore backup
  log "Creating pre-restore backup..."
  PRE_RESTORE_DIR="backups/pre-restore-$(date +%Y%m%d-%H%M%S)"
  mkdir -p "$PRE_RESTORE_DIR"
  docker compose exec -T db pg_dump -U odoo -Fc odoo > "$PRE_RESTORE_DIR/odoo.dump" || warn "Pre-restore backup failed"

  # Stop Odoo to prevent writes during restore
  log "Stopping Odoo..."
  docker compose stop odoo

  # Restore database
  log "Restoring database..."
  if [[ "$RESTORE_FILE" == *.dump ]]; then
    docker compose exec -T db pg_restore -U odoo -d odoo --clean --if-exists < "$RESTORE_FILE"
  elif [[ "$RESTORE_FILE" == *.sql.gz ]]; then
    zcat "$RESTORE_FILE" | docker compose exec -T db psql -U odoo -d odoo
  else
    docker compose exec -T db psql -U odoo -d odoo < "$RESTORE_FILE"
  fi

  # Restore filestore if present
  if [[ -f "$backup_dir/filestore.tar.gz" ]]; then
    log "Restoring filestore..."
    docker run --rm \
      -v odoo-filestore:/data \
      -v "$(pwd)/$backup_dir":/backup \
      alpine sh -c "rm -rf /data/* && tar xzf /backup/filestore.tar.gz -C /data"
  fi

  # Restart services
  log "Starting services..."
  docker compose up -d

  # Wait for health
  log "Waiting for services..."
  sleep 15

  # Verify
  log "Running verification..."
  ./scripts/oca-verify.sh || warn "Some verification checks failed"

  echo ""
  echo -e "${GREEN}=== RESTORE COMPLETE ===${NC}"
  echo "Restored from: $backup_dir"
  echo "Pre-restore backup: $PRE_RESTORE_DIR"
}

# -----------------------------------------
# Main
# -----------------------------------------
COMMAND="${1:-}"

case "$COMMAND" in
  list)
    cmd_list
    ;;
  git)
    cmd_git "${2:-}"
    ;;
  backup)
    cmd_backup "${2:-}"
    ;;
  *)
    usage
    ;;
esac
