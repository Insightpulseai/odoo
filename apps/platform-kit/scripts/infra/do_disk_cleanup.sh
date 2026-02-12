#!/usr/bin/env bash
# =============================================================================
# DO_DISK_CLEANUP.SH - DigitalOcean Droplet Disk Cleanup
# =============================================================================
# Reclaims disk space via Docker prune, journal vacuum, and log truncation.
# Safe to run repeatedly - only removes unused/orphaned resources.
# =============================================================================

set -euo pipefail

# Configuration
JOURNAL_VACUUM_DAYS="${JOURNAL_VACUUM_DAYS:-7}"
LOG_SIZE_THRESHOLD="${LOG_SIZE_THRESHOLD:-100M}"
DRY_RUN="${DRY_RUN:-false}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

usage() {
    cat <<EOF
Usage: $0 [OPTIONS]

DigitalOcean droplet disk cleanup script.

Options:
  --dry-run           Show what would be done without making changes
  --journal-days N    Keep journal logs for N days (default: 7)
  --log-threshold S   Truncate logs larger than S (default: 100M)
  -h, --help          Show this help message

Environment Variables:
  DRY_RUN             Set to 'true' for dry-run mode
  JOURNAL_VACUUM_DAYS Number of days to keep journal logs
  LOG_SIZE_THRESHOLD  Size threshold for log truncation

Examples:
  $0                           # Run cleanup
  $0 --dry-run                 # Preview changes
  $0 --journal-days 14         # Keep 14 days of journal logs

Remote execution:
  ssh root@<DROPLET_IP> 'bash -s' < $0
EOF
    exit 0
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run) DRY_RUN=true; shift ;;
        --journal-days) JOURNAL_VACUUM_DAYS="$2"; shift 2 ;;
        --log-threshold) LOG_SIZE_THRESHOLD="$2"; shift 2 ;;
        -h|--help) usage ;;
        *) log_error "Unknown option: $1"; usage ;;
    esac
done

# =============================================================================
# Pre-cleanup: Show current disk usage
# =============================================================================
log_info "=== Current Disk Usage ==="
df -h / | tail -n 1

if command -v docker &>/dev/null; then
    log_info "=== Docker Disk Usage ==="
    docker system df 2>/dev/null || log_warn "Docker not running or no access"
fi

# =============================================================================
# Docker Cleanup
# =============================================================================
if command -v docker &>/dev/null; then
    log_info "=== Docker Cleanup ==="

    if [[ "$DRY_RUN" == "true" ]]; then
        log_warn "[DRY-RUN] Would prune Docker images, containers, and volumes"
        docker system df
    else
        log_info "Pruning unused Docker images..."
        docker image prune -af 2>/dev/null || log_warn "Image prune failed or nothing to prune"

        log_info "Pruning Docker builder cache..."
        docker builder prune -af 2>/dev/null || log_warn "Builder prune failed or nothing to prune"

        log_info "Pruning stopped containers..."
        docker container prune -f 2>/dev/null || log_warn "Container prune failed or nothing to prune"

        log_info "Pruning unused volumes..."
        docker volume prune -f 2>/dev/null || log_warn "Volume prune failed or nothing to prune"

        log_info "Docker cleanup complete"
        docker system df
    fi
else
    log_warn "Docker not installed, skipping Docker cleanup"
fi

# =============================================================================
# Journal Log Cleanup
# =============================================================================
if command -v journalctl &>/dev/null; then
    log_info "=== Journal Log Cleanup ==="

    if [[ "$DRY_RUN" == "true" ]]; then
        log_warn "[DRY-RUN] Would vacuum journal logs older than ${JOURNAL_VACUUM_DAYS} days"
        journalctl --disk-usage 2>/dev/null || true
    else
        log_info "Current journal disk usage:"
        journalctl --disk-usage 2>/dev/null || true

        log_info "Vacuuming journal logs older than ${JOURNAL_VACUUM_DAYS} days..."
        journalctl --vacuum-time="${JOURNAL_VACUUM_DAYS}d" 2>/dev/null || log_warn "Journal vacuum failed"

        log_info "Journal disk usage after cleanup:"
        journalctl --disk-usage 2>/dev/null || true
    fi
else
    log_warn "journalctl not available, skipping journal cleanup"
fi

# =============================================================================
# Large Log File Truncation
# =============================================================================
log_info "=== Large Log File Cleanup ==="

# Find large log files
LARGE_LOGS=$(find /var/log -type f -name "*.log" -size "+${LOG_SIZE_THRESHOLD}" 2>/dev/null || true)

if [[ -n "$LARGE_LOGS" ]]; then
    log_info "Found large log files (>${LOG_SIZE_THRESHOLD}):"
    echo "$LARGE_LOGS" | while read -r logfile; do
        size=$(du -h "$logfile" 2>/dev/null | cut -f1)
        echo "  $logfile ($size)"
    done

    if [[ "$DRY_RUN" == "true" ]]; then
        log_warn "[DRY-RUN] Would truncate the above log files"
    else
        log_info "Truncating large log files..."
        echo "$LARGE_LOGS" | while read -r logfile; do
            truncate -s 0 "$logfile" 2>/dev/null && log_info "Truncated: $logfile" || log_warn "Failed to truncate: $logfile"
        done
    fi
else
    log_info "No log files larger than ${LOG_SIZE_THRESHOLD} found"
fi

# =============================================================================
# APT Cache Cleanup (Debian/Ubuntu)
# =============================================================================
if command -v apt-get &>/dev/null; then
    log_info "=== APT Cache Cleanup ==="

    if [[ "$DRY_RUN" == "true" ]]; then
        log_warn "[DRY-RUN] Would clean apt cache"
        du -sh /var/cache/apt/archives/ 2>/dev/null || true
    else
        log_info "Cleaning apt cache..."
        apt-get clean 2>/dev/null || log_warn "apt-get clean failed"
        apt-get autoremove -y 2>/dev/null || log_warn "apt-get autoremove failed"
    fi
fi

# =============================================================================
# Temp Files Cleanup
# =============================================================================
log_info "=== Temp Files Cleanup ==="

if [[ "$DRY_RUN" == "true" ]]; then
    log_warn "[DRY-RUN] Would clean /tmp files older than 7 days"
    find /tmp -type f -mtime +7 2>/dev/null | wc -l | xargs -I{} echo "  {} files would be removed"
else
    log_info "Cleaning old temp files..."
    find /tmp -type f -mtime +7 -delete 2>/dev/null || log_warn "Temp cleanup failed or nothing to clean"
fi

# =============================================================================
# Post-cleanup: Show final disk usage
# =============================================================================
log_info "=== Final Disk Usage ==="
df -h / | tail -n 1

log_info "=== Cleanup Complete ==="
if [[ "$DRY_RUN" == "true" ]]; then
    log_warn "This was a dry run. No changes were made."
    log_info "Run without --dry-run to apply changes."
fi
