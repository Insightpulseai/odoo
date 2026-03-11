#!/usr/bin/env bash
# =============================================================================
# GitHub Member Status Wrapper
# =============================================================================
# CLI tool for setting standardized GitHub member status using GraphQL API.
# Implements org-wide status taxonomy for coordinated ops signals.
#
# Usage:
#   ./scripts/status/set_status.sh <status> [options]
#
# Statuses:
#   launching   - Shipping to prod/public (prioritize reviews, unblock CI)
#   building    - Heads-down implementation (batch feedback, avoid interrupts)
#   reviewing   - Clearing PR queue (expect quick turnaround)
#   oncall      - Incident/ops focus (only page for urgent issues)
#   planning    - Specs/architecture (comment on PRDs, align scope)
#   clear       - Remove status
#
# Options:
#   -m, --message   Custom message (overrides default)
#   -r, --ref       PR/Issue reference (e.g., odoo-ce#271)
#   -e, --expires   Expiry duration (e.g., 6h, 2d)
#   -h, --help      Show this help
#
# Examples:
#   ./scripts/status/set_status.sh launching
#   ./scripts/status/set_status.sh launching -r "odoo-ce#271"
#   ./scripts/status/set_status.sh building -e 4h
#   ./scripts/status/set_status.sh clear
# =============================================================================
set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# =============================================================================
# Status Taxonomy
# =============================================================================
declare -A STATUS_EMOJI
STATUS_EMOJI=(
    [launching]=":rocket:"
    [building]=":hammer_and_wrench:"
    [reviewing]=":eyes:"
    [oncall]=":rotating_light:"
    [planning]=":memo:"
)

declare -A STATUS_MESSAGE
STATUS_MESSAGE=(
    [launching]="Launching — merge → deploy → validate"
    [building]="Building — heads-down; batch feedback"
    [reviewing]="Reviewing — clearing PR queue"
    [oncall]="Oncall — only ping for urgent issues"
    [planning]="Planning — specs/architecture alignment"
)

# =============================================================================
# Functions
# =============================================================================
show_help() {
    cat << 'EOF'
GitHub Member Status Wrapper

USAGE:
    set_status.sh <status> [options]

STATUSES:
    launching   Shipping to prod/public (prioritize reviews, unblock CI)
    building    Heads-down implementation (batch feedback, avoid interrupts)
    reviewing   Clearing PR queue (expect quick turnaround)
    oncall      Incident/ops focus (only page for urgent issues)
    planning    Specs/architecture (comment on PRDs, align scope)
    clear       Remove status

OPTIONS:
    -m, --message <msg>     Custom message (overrides default)
    -r, --ref <ref>         PR/Issue reference (e.g., odoo-ce#271)
    -e, --expires <dur>     Expiry duration (6h, 2d, etc.)
    -h, --help              Show this help

EXAMPLES:
    # Set launching status
    set_status.sh launching

    # Launching with PR reference
    set_status.sh launching -r "odoo-ce#271"

    # Building for 4 hours
    set_status.sh building -e 4h

    # Custom message
    set_status.sh launching -m "Shipping v2.0 release"

    # Clear status
    set_status.sh clear
EOF
}

parse_duration() {
    local duration="$1"
    local value="${duration%[hdwm]}"
    local unit="${duration: -1}"

    case "$unit" in
        h) echo "$((value))" ;;           # hours
        d) echo "$((value * 24))" ;;       # days -> hours
        w) echo "$((value * 24 * 7))" ;;   # weeks -> hours
        m) echo "$((value * 60))" ;;       # minutes -> minutes (handled separately)
        *) echo "$value" ;;                # assume hours
    esac
}

compute_expiry() {
    local duration="$1"
    local hours
    hours=$(parse_duration "$duration")

    # Cross-platform date handling
    if date --version >/dev/null 2>&1; then
        # GNU date (Linux)
        date -u -d "+${hours} hours" +%Y-%m-%dT%H:%M:%SZ
    else
        # BSD date (macOS)
        date -u -v+"${hours}"H +%Y-%m-%dT%H:%M:%SZ
    fi
}

check_auth() {
    if ! command -v gh &> /dev/null; then
        echo -e "${RED}Error: gh CLI is not installed${NC}"
        echo "Install: https://cli.github.com/"
        exit 1
    fi

    if ! gh auth status &> /dev/null; then
        echo -e "${RED}Error: gh is not authenticated${NC}"
        echo "Run: gh auth login"
        exit 1
    fi
}

set_status() {
    local message="$1"
    local emoji="$2"
    local expires_at="${3:-}"

    local input
    if [[ -n "$expires_at" ]]; then
        input=$(cat << EOF
{
  "message": "${message}",
  "emoji": "${emoji}",
  "expiresAt": "${expires_at}"
}
EOF
)
    else
        input=$(cat << EOF
{
  "message": "${message}",
  "emoji": "${emoji}"
}
EOF
)
    fi

    local result
    result=$(gh api graphql -f query='
mutation($input: ChangeUserStatusInput!) {
  changeUserStatus(input: $input) {
    status { message emoji expiresAt }
  }
}' -f input="$input" 2>&1) || {
        echo -e "${RED}Error setting status:${NC}"
        echo "$result"
        exit 1
    }

    echo "$result"
}

clear_status() {
    local result
    result=$(gh api graphql -f query='
mutation($input: ChangeUserStatusInput!) {
  changeUserStatus(input: $input) {
    status { message emoji expiresAt }
  }
}' -f input='{"message": "", "emoji": ""}' 2>&1) || {
        echo -e "${RED}Error clearing status:${NC}"
        echo "$result"
        exit 1
    }

    echo -e "${GREEN}Status cleared${NC}"
}

get_status() {
    gh api graphql -f query='
query {
  viewer {
    status { message emoji expiresAt }
  }
}' 2>&1
}

# =============================================================================
# Main
# =============================================================================
main() {
    local status=""
    local custom_message=""
    local ref=""
    local expires=""

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -h|--help)
                show_help
                exit 0
                ;;
            -m|--message)
                custom_message="$2"
                shift 2
                ;;
            -r|--ref)
                ref="$2"
                shift 2
                ;;
            -e|--expires)
                expires="$2"
                shift 2
                ;;
            -*)
                echo -e "${RED}Unknown option: $1${NC}"
                show_help
                exit 1
                ;;
            *)
                if [[ -z "$status" ]]; then
                    status="$1"
                else
                    echo -e "${RED}Unexpected argument: $1${NC}"
                    exit 1
                fi
                shift
                ;;
        esac
    done

    # Require status argument
    if [[ -z "$status" ]]; then
        echo -e "${YELLOW}Usage: set_status.sh <status> [options]${NC}"
        echo ""
        echo "Run with --help for full documentation"
        exit 1
    fi

    # Check authentication
    check_auth

    # Handle clear
    if [[ "$status" == "clear" ]]; then
        clear_status
        exit 0
    fi

    # Validate status
    status=$(echo "$status" | tr '[:upper:]' '[:lower:]')
    if [[ -z "${STATUS_EMOJI[$status]:-}" ]]; then
        echo -e "${RED}Unknown status: $status${NC}"
        echo ""
        echo "Valid statuses: launching, building, reviewing, oncall, planning, clear"
        exit 1
    fi

    # Build message
    local message
    if [[ -n "$custom_message" ]]; then
        message="$custom_message"
    else
        message="${STATUS_MESSAGE[$status]}"
    fi

    # Append ref if provided
    if [[ -n "$ref" ]]; then
        message="${message} (${ref})"
    fi

    local emoji="${STATUS_EMOJI[$status]}"

    # Compute expiry
    local expires_at=""
    if [[ -n "$expires" ]]; then
        expires_at=$(compute_expiry "$expires")
    fi

    # Set status
    echo -e "${BLUE}Setting status...${NC}"
    echo ""

    local result
    result=$(set_status "$message" "$emoji" "$expires_at")

    # Display result
    echo -e "${GREEN}Status set successfully${NC}"
    echo ""
    echo "  Emoji:   ${emoji}"
    echo "  Message: ${message}"
    if [[ -n "$expires_at" ]]; then
        echo "  Expires: ${expires_at}"
    fi
    echo ""

    # Verify
    echo -e "${BLUE}Current status:${NC}"
    get_status | jq -r '.data.viewer.status | "  \(.emoji) \(.message)" + if .expiresAt then " (expires: \(.expiresAt))" else "" end'
}

main "$@"
