#!/usr/bin/env bash
# =============================================================================
# DO_RESOURCE_CHECK.SH - DigitalOcean Resource Monitoring
# =============================================================================
# Checks resource utilization across DigitalOcean infrastructure.
# Provides alerts for disk, CPU, RAM, and cost concerns.
# =============================================================================

set -euo pipefail

# Configuration
DISK_WARN_THRESHOLD="${DISK_WARN_THRESHOLD:-70}"
DISK_CRIT_THRESHOLD="${DISK_CRIT_THRESHOLD:-85}"
OUTPUT_FORMAT="${OUTPUT_FORMAT:-text}"  # text, json, markdown

# Known droplets (from CLAUDE.md)
KNOWN_DROPLETS=(
    "odoo-erp-prod:159.223.75.148"
    "ocr-service-droplet:188.166.237.231"
    "plane-ce-prod:167.99.104.239"
)

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_crit() { echo -e "${RED}[CRITICAL]${NC} $1"; }
log_ok() { echo -e "${GREEN}[OK]${NC} $1"; }

usage() {
    cat <<EOF
Usage: $0 [OPTIONS]

DigitalOcean resource monitoring and alerting.

Options:
  --format FORMAT     Output format: text, json, markdown (default: text)
  --disk-warn N       Disk warning threshold % (default: 70)
  --disk-crit N       Disk critical threshold % (default: 85)
  --check-remote      SSH to droplets for live metrics (requires SSH access)
  --summary           Show summary only (no details)
  -h, --help          Show this help message

Environment Variables:
  DISK_WARN_THRESHOLD   Warning threshold for disk usage
  DISK_CRIT_THRESHOLD   Critical threshold for disk usage
  OUTPUT_FORMAT         Output format (text, json, markdown)

Examples:
  $0                    # Full resource report
  $0 --summary          # Quick summary
  $0 --check-remote     # Live metrics from droplets
  $0 --format markdown  # Markdown output for docs

Prerequisites:
  - doctl CLI installed and authenticated
  - SSH access for --check-remote option

EOF
    exit 0
}

# Check for doctl
check_doctl() {
    if ! command -v doctl &>/dev/null; then
        log_error "doctl CLI not found"
        exit 1
    fi
    if ! doctl account get &>/dev/null; then
        log_error "doctl not authenticated"
        exit 1
    fi
}

# Get droplet info from doctl
get_droplets() {
    doctl compute droplet list --format ID,Name,PublicIPv4,Region,Size,Disk,Memory,VCPUs,Status --no-header 2>/dev/null
}

# Get VPC count
get_vpc_count() {
    doctl vpcs list --no-header 2>/dev/null | wc -l | tr -d ' '
}

# Get snapshot count and size
get_snapshot_info() {
    local count size
    count=$(doctl compute image list-user --no-header 2>/dev/null | wc -l | tr -d ' ')
    size=$(doctl compute image list-user --format SizeGigaBytes --no-header 2>/dev/null | awk '{sum+=$1} END {print sum}' || echo "0")
    echo "$count:$size"
}

# Get App Platform apps
get_app_count() {
    doctl apps list --no-header 2>/dev/null | wc -l | tr -d ' '
}

# Get managed databases
get_db_count() {
    doctl databases list --no-header 2>/dev/null | wc -l | tr -d ' '
}

# Check remote disk usage via SSH
check_remote_disk() {
    local ip="$1"
    local name="$2"

    # Try SSH with timeout
    local disk_info
    disk_info=$(ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no "root@$ip" \
        "df -h / | tail -n 1 | awk '{print \$5}'" 2>/dev/null || echo "N/A")

    echo "$disk_info"
}

# Check remote Docker usage via SSH
check_remote_docker() {
    local ip="$1"

    local docker_info
    docker_info=$(ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no "root@$ip" \
        "docker system df --format '{{.Type}}: {{.Size}}' 2>/dev/null" 2>/dev/null || echo "N/A")

    echo "$docker_info"
}

# Parse arguments
CHECK_REMOTE=false
SUMMARY_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --format) OUTPUT_FORMAT="$2"; shift 2 ;;
        --disk-warn) DISK_WARN_THRESHOLD="$2"; shift 2 ;;
        --disk-crit) DISK_CRIT_THRESHOLD="$2"; shift 2 ;;
        --check-remote) CHECK_REMOTE=true; shift ;;
        --summary) SUMMARY_ONLY=true; shift ;;
        -h|--help) usage ;;
        *) log_error "Unknown option: $1"; usage ;;
    esac
done

# =============================================================================
# Main Script
# =============================================================================

echo ""
log_info "=== DigitalOcean Resource Report ==="
log_info "Generated: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo ""

check_doctl

# Collect metrics
DROPLETS=$(get_droplets)
VPC_COUNT=$(get_vpc_count)
SNAPSHOT_INFO=$(get_snapshot_info)
SNAPSHOT_COUNT=$(echo "$SNAPSHOT_INFO" | cut -d: -f1)
SNAPSHOT_SIZE=$(echo "$SNAPSHOT_INFO" | cut -d: -f2)
APP_COUNT=$(get_app_count)
DB_COUNT=$(get_db_count)

# Count PR VPCs
PR_VPC_COUNT=$(doctl vpcs list --format Name --no-header 2>/dev/null | grep -cE "^pr-" || echo "0")

# =============================================================================
# Output: Summary
# =============================================================================

if [[ "$OUTPUT_FORMAT" == "markdown" ]]; then
    echo "## Resource Summary"
    echo ""
    echo "| Resource | Count | Notes |"
    echo "|----------|-------|-------|"
    echo "| Droplets | $(echo "$DROPLETS" | wc -l | tr -d ' ') | Compute instances |"
    echo "| VPCs | $VPC_COUNT | $PR_VPC_COUNT pr-* VPCs |"
    echo "| Snapshots | $SNAPSHOT_COUNT | ~${SNAPSHOT_SIZE}GB total |"
    echo "| Apps | $APP_COUNT | App Platform |"
    echo "| Databases | $DB_COUNT | Managed DBs |"
    echo ""
else
    log_info "=== Resource Summary ==="
    echo "  Droplets:    $(echo "$DROPLETS" | wc -l | tr -d ' ')"
    echo "  VPCs:        $VPC_COUNT (pr-* VPCs: $PR_VPC_COUNT)"
    echo "  Snapshots:   $SNAPSHOT_COUNT (~${SNAPSHOT_SIZE}GB)"
    echo "  Apps:        $APP_COUNT"
    echo "  Databases:   $DB_COUNT"
    echo ""
fi

# =============================================================================
# Alerts & Warnings
# =============================================================================

ALERT_COUNT=0

# Check for VPC sprawl
if [[ "$PR_VPC_COUNT" -gt 5 ]]; then
    log_warn "VPC sprawl detected: $PR_VPC_COUNT pr-* VPCs"
    log_info "  → Run: ./scripts/infra/do_prune_empty_vpcs.sh"
    ((ALERT_COUNT++))
fi

# Check snapshot count
if [[ "$SNAPSHOT_COUNT" -gt 20 ]]; then
    log_warn "High snapshot count: $SNAPSHOT_COUNT snapshots (~${SNAPSHOT_SIZE}GB)"
    log_info "  → Run: ./scripts/infra/do_prune_snapshots.sh --dry-run"
    ((ALERT_COUNT++))
fi

if [[ "$SUMMARY_ONLY" == "true" ]]; then
    echo ""
    if [[ $ALERT_COUNT -gt 0 ]]; then
        log_warn "Total alerts: $ALERT_COUNT"
    else
        log_ok "No alerts"
    fi
    exit 0
fi

# =============================================================================
# Output: Droplet Details
# =============================================================================

echo ""
if [[ "$OUTPUT_FORMAT" == "markdown" ]]; then
    echo "## Droplet Details"
    echo ""
    echo "| Name | IP | Region | Size | Disk | RAM | Status |"
    echo "|------|----|----- --|------|------|-----|--------|"
fi

log_info "=== Droplet Details ==="
while IFS=$'\t' read -r id name ip region size disk memory vcpus status; do
    [[ -z "$id" ]] && continue

    if [[ "$OUTPUT_FORMAT" == "markdown" ]]; then
        echo "| $name | $ip | $region | $size | ${disk}GB | ${memory}MB | $status |"
    else
        echo "  📦 $name"
        echo "     IP: $ip | Region: $region"
        echo "     Size: $size | Disk: ${disk}GB | RAM: ${memory}MB | vCPUs: $vcpus"
        echo "     Status: $status"
        echo ""
    fi
done <<< "$DROPLETS"

# =============================================================================
# Remote Checks (if enabled)
# =============================================================================

if [[ "$CHECK_REMOTE" == "true" ]]; then
    echo ""
    log_info "=== Remote Disk Checks ==="

    for entry in "${KNOWN_DROPLETS[@]}"; do
        name="${entry%%:*}"
        ip="${entry##*:}"

        echo -n "  Checking $name ($ip)... "

        disk_pct=$(check_remote_disk "$ip" "$name")

        if [[ "$disk_pct" == "N/A" ]]; then
            log_warn "SSH failed"
        else
            # Parse percentage
            pct_num="${disk_pct%\%}"
            if [[ "$pct_num" -ge "$DISK_CRIT_THRESHOLD" ]]; then
                log_crit "Disk: $disk_pct (CRITICAL)"
                log_info "    → Run: ssh root@$ip 'bash -s' < ./scripts/infra/do_disk_cleanup.sh"
                ((ALERT_COUNT++))
            elif [[ "$pct_num" -ge "$DISK_WARN_THRESHOLD" ]]; then
                log_warn "Disk: $disk_pct (WARNING)"
                ((ALERT_COUNT++))
            else
                log_ok "Disk: $disk_pct"
            fi
        fi

        # Check Docker if available
        if [[ "$CHECK_REMOTE" == "true" ]]; then
            docker_info=$(check_remote_docker "$ip")
            if [[ "$docker_info" != "N/A" && -n "$docker_info" ]]; then
                echo "    Docker:"
                echo "$docker_info" | while read -r line; do
                    echo "      $line"
                done
            fi
        fi
    done
fi

# =============================================================================
# Final Summary
# =============================================================================

echo ""
log_info "=== Health Summary ==="
if [[ $ALERT_COUNT -gt 0 ]]; then
    log_warn "Alerts: $ALERT_COUNT issue(s) detected"
    echo ""
    log_info "Recommended actions:"
    echo "  1. VPC cleanup:      ./scripts/infra/do_prune_empty_vpcs.sh --dry-run"
    echo "  2. Snapshot cleanup: ./scripts/infra/do_prune_snapshots.sh --dry-run"
    echo "  3. Disk cleanup:     ./scripts/infra/do_disk_cleanup.sh --dry-run"
else
    log_ok "All resources within normal parameters"
fi

echo ""
log_info "Report complete"
