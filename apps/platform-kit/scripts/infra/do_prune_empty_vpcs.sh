#!/usr/bin/env bash
# =============================================================================
# DO_PRUNE_EMPTY_VPCS.SH - DigitalOcean Empty VPC Cleanup
# =============================================================================
# Deletes empty VPCs matching specified patterns (default: pr-* prefix).
# Only removes VPCs with 0 attached resources (droplets, databases, etc.).
# =============================================================================

set -euo pipefail

# Configuration
VPC_PATTERN="${VPC_PATTERN:-^pr-}"
DRY_RUN="${DRY_RUN:-false}"
FORCE="${FORCE:-false}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_debug() { echo -e "${BLUE}[DEBUG]${NC} $1"; }

usage() {
    cat <<EOF
Usage: $0 [OPTIONS]

DigitalOcean empty VPC cleanup script.
Deletes VPCs matching a pattern that have no attached resources.

Options:
  --dry-run           Show what would be deleted without making changes
  --pattern REGEX     VPC name pattern to match (default: ^pr-)
  --force             Skip confirmation prompt
  --all-empty         Delete ALL empty VPCs (ignores pattern, requires --force)
  -h, --help          Show this help message

Environment Variables:
  DRY_RUN             Set to 'true' for dry-run mode
  VPC_PATTERN         Regex pattern for VPC names to target
  FORCE               Set to 'true' to skip confirmation

Examples:
  $0                           # Preview pr-* VPCs for deletion
  $0 --dry-run                 # Dry run (default behavior)
  $0 --force                   # Delete pr-* VPCs without confirmation
  $0 --pattern "^test-"        # Target test-* VPCs
  $0 --all-empty --force       # Delete ALL empty VPCs

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

    # Verify authentication
    if ! doctl account get &>/dev/null; then
        log_error "doctl not authenticated. Run: doctl auth init"
        exit 1
    fi

    log_info "doctl authenticated successfully"
}

# Get VPC member count (droplets, databases, k8s, etc.)
get_vpc_member_count() {
    local vpc_id="$1"

    # List VPC members and count them
    local count
    count=$(doctl vpcs members list "$vpc_id" --format ID --no-header 2>/dev/null | wc -l | tr -d ' ')

    echo "$count"
}

# Parse arguments
ALL_EMPTY=false
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run) DRY_RUN=true; shift ;;
        --pattern) VPC_PATTERN="$2"; shift 2 ;;
        --force) FORCE=true; shift ;;
        --all-empty) ALL_EMPTY=true; shift ;;
        -h|--help) usage ;;
        *) log_error "Unknown option: $1"; usage ;;
    esac
done

# Validation
if [[ "$ALL_EMPTY" == "true" && "$FORCE" != "true" ]]; then
    log_error "--all-empty requires --force flag for safety"
    exit 1
fi

# =============================================================================
# Main Script
# =============================================================================

log_info "=== DigitalOcean VPC Cleanup ==="
log_info "Pattern: ${VPC_PATTERN}"
log_info "Dry Run: ${DRY_RUN}"
log_info "Force: ${FORCE}"
echo ""

# Check doctl availability
check_doctl

# Get all VPCs
log_info "Fetching VPC list..."
VPC_LIST=$(doctl vpcs list --format ID,Name,Region,URN --no-header 2>/dev/null)

if [[ -z "$VPC_LIST" ]]; then
    log_info "No VPCs found in account"
    exit 0
fi

# Track VPCs to delete
declare -a VPCS_TO_DELETE=()
declare -a VPC_NAMES_TO_DELETE=()

# Process each VPC
log_info "Analyzing VPCs..."
echo ""

while IFS=$'\t' read -r vpc_id vpc_name vpc_region vpc_urn; do
    # Skip empty lines
    [[ -z "$vpc_id" ]] && continue

    # Check if name matches pattern (or all-empty mode)
    if [[ "$ALL_EMPTY" != "true" ]]; then
        if ! echo "$vpc_name" | grep -qE "$VPC_PATTERN"; then
            log_debug "Skipping $vpc_name (doesn't match pattern)"
            continue
        fi
    fi

    # Get member count
    member_count=$(get_vpc_member_count "$vpc_id")

    if [[ "$member_count" -eq 0 ]]; then
        log_info "Empty VPC found: $vpc_name ($vpc_region) - $member_count members"
        VPCS_TO_DELETE+=("$vpc_id")
        VPC_NAMES_TO_DELETE+=("$vpc_name")
    else
        log_debug "VPC $vpc_name has $member_count members, skipping"
    fi
done <<< "$VPC_LIST"

echo ""

# Summary
if [[ ${#VPCS_TO_DELETE[@]} -eq 0 ]]; then
    log_info "No empty VPCs matching pattern found"
    exit 0
fi

log_info "=== VPCs to Delete ==="
for i in "${!VPCS_TO_DELETE[@]}"; do
    echo "  - ${VPC_NAMES_TO_DELETE[$i]} (${VPCS_TO_DELETE[$i]})"
done
echo ""
log_info "Total: ${#VPCS_TO_DELETE[@]} VPC(s)"
echo ""

# Dry run mode
if [[ "$DRY_RUN" == "true" ]]; then
    log_warn "[DRY-RUN] Would delete ${#VPCS_TO_DELETE[@]} VPC(s)"
    log_info "Run without --dry-run to apply changes"
    exit 0
fi

# Confirmation (unless --force)
if [[ "$FORCE" != "true" ]]; then
    echo -n "Delete these ${#VPCS_TO_DELETE[@]} VPC(s)? [y/N] "
    read -r confirm
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        log_info "Aborted"
        exit 0
    fi
fi

# Delete VPCs
log_info "=== Deleting VPCs ==="
deleted_count=0
failed_count=0

for i in "${!VPCS_TO_DELETE[@]}"; do
    vpc_id="${VPCS_TO_DELETE[$i]}"
    vpc_name="${VPC_NAMES_TO_DELETE[$i]}"

    log_info "Deleting: $vpc_name..."

    if doctl vpcs delete "$vpc_id" --force 2>/dev/null; then
        log_info "  ✓ Deleted $vpc_name"
        ((deleted_count++))
    else
        log_error "  ✗ Failed to delete $vpc_name"
        ((failed_count++))
    fi
done

echo ""
log_info "=== Summary ==="
log_info "Deleted: $deleted_count VPC(s)"
if [[ $failed_count -gt 0 ]]; then
    log_warn "Failed: $failed_count VPC(s)"
fi

# Verify remaining VPCs matching pattern
remaining=$(doctl vpcs list --format Name --no-header 2>/dev/null | grep -cE "$VPC_PATTERN" || echo "0")
log_info "Remaining VPCs matching '$VPC_PATTERN': $remaining"
