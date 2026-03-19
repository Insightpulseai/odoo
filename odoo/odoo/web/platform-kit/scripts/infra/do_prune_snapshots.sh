#!/usr/bin/env bash
# =============================================================================
# DO_PRUNE_SNAPSHOTS.SH - DigitalOcean Snapshot Retention Policy
# =============================================================================
# Enforces snapshot retention policy:
# - KEEP: Snapshots with "gold" names (baseline, production-complete, post-migration)
# - DELETE: All other snapshots older than retention period
# =============================================================================

set -euo pipefail

# Configuration
RETENTION_DAYS="${RETENTION_DAYS:-60}"
DRY_RUN="${DRY_RUN:-false}"
FORCE="${FORCE:-false}"

# Gold snapshot patterns (these are NEVER deleted)
GOLD_PATTERNS=(
    "baseline"
    "production-complete"
    "post-migration"
    "gold"
    "critical"
    "release"
)

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_debug() { echo -e "${BLUE}[DEBUG]${NC} $1"; }
log_gold() { echo -e "${CYAN}[GOLD]${NC} $1"; }

usage() {
    cat <<EOF
Usage: $0 [OPTIONS]

DigitalOcean snapshot retention policy enforcement.

Gold snapshots (NEVER deleted):
  Names containing: ${GOLD_PATTERNS[*]}

All other snapshots older than retention period will be deleted.

Options:
  --dry-run              Show what would be deleted without making changes
  --retention-days N     Delete non-gold snapshots older than N days (default: 60)
  --force                Skip confirmation prompt
  --list-gold            Only list gold snapshots, then exit
  --list-deletable       Only list deletable snapshots, then exit
  -h, --help             Show this help message

Environment Variables:
  DRY_RUN                Set to 'true' for dry-run mode
  RETENTION_DAYS         Number of days to retain non-gold snapshots
  FORCE                  Set to 'true' to skip confirmation

Examples:
  $0                              # Preview what would be deleted
  $0 --dry-run                    # Same as above
  $0 --retention-days 30 --force  # Delete snapshots older than 30 days
  $0 --list-gold                  # Show protected gold snapshots

Prerequisites:
  - doctl CLI installed and authenticated
  - Appropriate DigitalOcean API permissions

EOF
    exit 0
}

# Check for doctl
check_doctl() {
    if ! command -v doctl &>/dev/null; then
        log_error "doctl CLI not found. Please install: https://docs.digitalocean.com/reference/doctl/how-to/install/"
        exit 1
    fi

    if ! doctl account get &>/dev/null; then
        log_error "doctl not authenticated. Run: doctl auth init"
        exit 1
    fi

    log_info "doctl authenticated successfully"
}

# Check if snapshot name matches gold patterns
is_gold_snapshot() {
    local name="$1"
    local name_lower
    name_lower=$(echo "$name" | tr '[:upper:]' '[:lower:]')

    for pattern in "${GOLD_PATTERNS[@]}"; do
        if [[ "$name_lower" == *"$pattern"* ]]; then
            return 0  # true - is gold
        fi
    done
    return 1  # false - not gold
}

# Calculate age in days from ISO date
get_age_days() {
    local created_at="$1"
    local created_ts
    local now_ts
    local age_seconds

    # Parse ISO date to timestamp
    created_ts=$(date -j -f "%Y-%m-%dT%H:%M:%SZ" "$created_at" "+%s" 2>/dev/null || \
                 date -d "$created_at" "+%s" 2>/dev/null)
    now_ts=$(date "+%s")
    age_seconds=$((now_ts - created_ts))
    echo $((age_seconds / 86400))
}

# Parse arguments
LIST_GOLD=false
LIST_DELETABLE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run) DRY_RUN=true; shift ;;
        --retention-days) RETENTION_DAYS="$2"; shift 2 ;;
        --force) FORCE=true; shift ;;
        --list-gold) LIST_GOLD=true; shift ;;
        --list-deletable) LIST_DELETABLE=true; shift ;;
        -h|--help) usage ;;
        *) log_error "Unknown option: $1"; usage ;;
    esac
done

# =============================================================================
# Main Script
# =============================================================================

log_info "=== DigitalOcean Snapshot Retention Policy ==="
log_info "Retention: ${RETENTION_DAYS} days"
log_info "Gold patterns: ${GOLD_PATTERNS[*]}"
log_info "Dry Run: ${DRY_RUN}"
echo ""

check_doctl

# Get all user snapshots (droplet snapshots)
log_info "Fetching snapshot list..."
SNAPSHOT_LIST=$(doctl compute image list-user --format ID,Name,CreatedAt,SizeGigaBytes,Regions --no-header 2>/dev/null)

if [[ -z "$SNAPSHOT_LIST" ]]; then
    log_info "No user snapshots found"
    exit 0
fi

# Track snapshots
declare -a GOLD_SNAPSHOTS=()
declare -a GOLD_NAMES=()
declare -a DELETABLE_IDS=()
declare -a DELETABLE_NAMES=()
declare -a DELETABLE_AGES=()
declare -a DELETABLE_SIZES=()

total_deletable_size=0

# Process each snapshot
while IFS=$'\t' read -r snap_id snap_name created_at size_gb regions; do
    [[ -z "$snap_id" ]] && continue

    # Calculate age
    age_days=$(get_age_days "$created_at" 2>/dev/null || echo "0")

    # Check if gold
    if is_gold_snapshot "$snap_name"; then
        GOLD_SNAPSHOTS+=("$snap_id")
        GOLD_NAMES+=("$snap_name (${age_days}d old, ${size_gb}GB)")
    elif [[ "$age_days" -gt "$RETENTION_DAYS" ]]; then
        DELETABLE_IDS+=("$snap_id")
        DELETABLE_NAMES+=("$snap_name")
        DELETABLE_AGES+=("$age_days")
        DELETABLE_SIZES+=("$size_gb")
        total_deletable_size=$((total_deletable_size + ${size_gb%.*}))
    fi
done <<< "$SNAPSHOT_LIST"

# List gold snapshots
if [[ "$LIST_GOLD" == "true" || ${#GOLD_SNAPSHOTS[@]} -gt 0 ]]; then
    echo ""
    log_gold "=== Gold Snapshots (Protected) ==="
    if [[ ${#GOLD_SNAPSHOTS[@]} -eq 0 ]]; then
        echo "  (none found)"
    else
        for name in "${GOLD_NAMES[@]}"; do
            echo "  🔒 $name"
        done
    fi
    echo ""

    if [[ "$LIST_GOLD" == "true" ]]; then
        log_info "Total gold snapshots: ${#GOLD_SNAPSHOTS[@]}"
        exit 0
    fi
fi

# List deletable snapshots
if [[ "$LIST_DELETABLE" == "true" || ${#DELETABLE_IDS[@]} -gt 0 ]]; then
    echo ""
    log_warn "=== Deletable Snapshots (>${RETENTION_DAYS} days old) ==="
    if [[ ${#DELETABLE_IDS[@]} -eq 0 ]]; then
        echo "  (none found)"
    else
        for i in "${!DELETABLE_IDS[@]}"; do
            echo "  🗑️  ${DELETABLE_NAMES[$i]} (${DELETABLE_AGES[$i]}d old, ${DELETABLE_SIZES[$i]}GB)"
        done
    fi
    echo ""

    if [[ "$LIST_DELETABLE" == "true" ]]; then
        log_info "Total deletable: ${#DELETABLE_IDS[@]} snapshots (~${total_deletable_size}GB)"
        exit 0
    fi
fi

# Exit if nothing to delete
if [[ ${#DELETABLE_IDS[@]} -eq 0 ]]; then
    log_info "No snapshots to delete"
    log_info "Gold snapshots preserved: ${#GOLD_SNAPSHOTS[@]}"
    exit 0
fi

# Summary
echo ""
log_info "=== Summary ==="
log_info "Gold (preserved): ${#GOLD_SNAPSHOTS[@]} snapshots"
log_warn "Deletable: ${#DELETABLE_IDS[@]} snapshots (~${total_deletable_size}GB)"
echo ""

# Dry run mode
if [[ "$DRY_RUN" == "true" ]]; then
    log_warn "[DRY-RUN] Would delete ${#DELETABLE_IDS[@]} snapshot(s) (~${total_deletable_size}GB)"
    log_info "Run without --dry-run to apply changes"
    exit 0
fi

# Confirmation
if [[ "$FORCE" != "true" ]]; then
    echo -n "Delete ${#DELETABLE_IDS[@]} snapshot(s)? This will free ~${total_deletable_size}GB. [y/N] "
    read -r confirm
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        log_info "Aborted"
        exit 0
    fi
fi

# Delete snapshots
log_info "=== Deleting Snapshots ==="
deleted_count=0
deleted_size=0
failed_count=0

for i in "${!DELETABLE_IDS[@]}"; do
    snap_id="${DELETABLE_IDS[$i]}"
    snap_name="${DELETABLE_NAMES[$i]}"
    snap_size="${DELETABLE_SIZES[$i]}"

    log_info "Deleting: $snap_name..."

    if doctl compute image delete "$snap_id" --force 2>/dev/null; then
        log_info "  ✓ Deleted $snap_name"
        ((deleted_count++))
        deleted_size=$((deleted_size + ${snap_size%.*}))
    else
        log_error "  ✗ Failed to delete $snap_name"
        ((failed_count++))
    fi
done

echo ""
log_info "=== Final Summary ==="
log_info "Deleted: $deleted_count snapshot(s) (~${deleted_size}GB freed)"
log_info "Gold preserved: ${#GOLD_SNAPSHOTS[@]} snapshot(s)"
if [[ $failed_count -gt 0 ]]; then
    log_warn "Failed: $failed_count snapshot(s)"
fi

# Final count
remaining=$(doctl compute image list-user --no-header 2>/dev/null | wc -l | tr -d ' ')
log_info "Total remaining snapshots: $remaining"
