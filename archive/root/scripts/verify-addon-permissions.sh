#!/bin/bash
###############################################################################
# verify-addon-permissions.sh - Verify Odoo addon permissions on server
#
# Usage:
#   ./scripts/verify-addon-permissions.sh
#
# Purpose:
#   - Check all addons in /opt/odoo-ce/repo/addons/ have correct permissions
#   - Ensure ownership is set to UID 100:GID 101 (odoo container user)
#   - Fix any permission issues automatically
#
# Exit codes:
#   0 - All permissions correct or fixed successfully
#   1 - SSH connection failed
#   2 - Permission fixes failed
###############################################################################

set -euo pipefail

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REMOTE_HOST="178.128.112.214"
REMOTE_USER="root"
ADDON_DIR="/opt/odoo-ce/repo/addons"

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

main() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  Odoo Addon Permission Verification"
    echo "  Target: ${REMOTE_USER}@${REMOTE_HOST}"
    echo "  Addon Directory: ${ADDON_DIR}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    # Check SSH connection
    log_info "Checking SSH connection..."
    if ! ssh -o ConnectTimeout=5 "${REMOTE_USER}@${REMOTE_HOST}" "echo 'SSH OK'" &>/dev/null; then
        log_error "Cannot connect to ${REMOTE_USER}@${REMOTE_HOST}"
        exit 1
    fi
    log_success "SSH connection verified"
    echo ""

    # Find addons with incorrect permissions
    log_info "Scanning for permission issues..."

    # Get list of addons with incorrect ownership
    # Scans: ipai/ namespace + all standalone ipai_* modules (31 total)
    incorrect_addons=$(ssh "${REMOTE_USER}@${REMOTE_HOST}" "
        cd ${ADDON_DIR} && \
        find ipai ipai_* -maxdepth 0 -type d 2>/dev/null | while read dir; do
            owner=\$(stat -c '%u:%g' \"\$dir\" 2>/dev/null)
            if [ \"\$owner\" != \"100:101\" ]; then
                echo \"\$dir (\$owner)\"
            fi
        done
    ")

    if [ -z "$incorrect_addons" ]; then
        log_success "All addon permissions are correct (100:101)"
        echo ""
        return 0
    fi

    # Display issues found
    log_warning "Found addons with incorrect permissions:"
    echo "$incorrect_addons" | while read line; do
        echo "   ⚠️  $line"
    done
    echo ""

    # Fix permissions
    log_info "Fixing permissions..."
    # Fix all ipai/ namespace + all standalone ipai_* modules
    ssh "${REMOTE_USER}@${REMOTE_HOST}" "
        cd ${ADDON_DIR} && \
        chown -R 100:101 ipai ipai_* && \
        chmod -R 755 ipai ipai_*
    " || {
        log_error "Failed to fix permissions"
        exit 2
    }

    log_success "All addon permissions fixed"
    echo ""

    # Verify fix
    log_info "Verifying fix..."
    # Verify all ipai/ namespace + all standalone ipai_* modules
    remaining_issues=$(ssh "${REMOTE_USER}@${REMOTE_HOST}" "
        cd ${ADDON_DIR} && \
        find ipai ipai_* -maxdepth 0 -type d 2>/dev/null | while read dir; do
            owner=\$(stat -c '%u:%g' \"\$dir\" 2>/dev/null)
            if [ \"\$owner\" != \"100:101\" ]; then
                echo \"\$dir\"
            fi
        done
    ")

    if [ -z "$remaining_issues" ]; then
        log_success "Verification passed - all permissions correct"
    else
        log_error "Verification failed - some permissions still incorrect:"
        echo "$remaining_issues"
        exit 2
    fi

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log_success "Permission verification complete"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
}

main "$@"
