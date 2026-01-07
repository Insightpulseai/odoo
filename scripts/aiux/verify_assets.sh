#!/usr/bin/env bash
# AIUX Assets Verification Script
# Verifies Odoo asset bundles are accessible and return HTTP 200
#
# Usage: ./scripts/aiux/verify_assets.sh [OPTIONS]
#
# Options:
#   --odoo-url URL      Odoo base URL (default: http://localhost:8069)
#   --timeout SECS      Request timeout (default: 30)
#   --output FILE       Write results to file (optional)
#   --verbose           Show detailed output
#
# Exit codes:
#   0  All checks passed
#   1  One or more asset endpoints returned non-200
#   2  Login page not accessible

set -euo pipefail

# Default configuration
ODOO_URL="${ODOO_URL:-http://localhost:8069}"
TIMEOUT=30
OUTPUT_FILE=""
VERBOSE=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --odoo-url)
            ODOO_URL="$2"
            shift 2
            ;;
        --timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        --output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Results tracking
declare -a PASSED_CHECKS=()
declare -a FAILED_CHECKS=()

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo ""
    echo -e "${BLUE}==>${NC} $1"
    echo "---------------------------------------------------"
}

log_verbose() {
    if [ "$VERBOSE" = true ]; then
        echo -e "${BLUE}[VERBOSE]${NC} $1"
    fi
}

# Check single endpoint
check_endpoint() {
    local endpoint="$1"
    local description="$2"
    local url="${ODOO_URL}${endpoint}"

    log_verbose "Checking: $url"

    local http_code
    local response_time

    # Make request and capture status code + timing
    local start_time
    start_time=$(date +%s.%N)

    http_code=$(curl -sf -o /dev/null -w "%{http_code}" \
        --connect-timeout "$TIMEOUT" \
        --max-time "$TIMEOUT" \
        "$url" 2>/dev/null || echo "000")

    local end_time
    end_time=$(date +%s.%N)
    response_time=$(echo "$end_time - $start_time" | bc 2>/dev/null || echo "N/A")

    if [ "$http_code" = "200" ]; then
        log_info "PASS: $description ($endpoint) - HTTP $http_code [${response_time}s]"
        PASSED_CHECKS+=("$endpoint")
        return 0
    else
        log_error "FAIL: $description ($endpoint) - HTTP $http_code"
        FAILED_CHECKS+=("$endpoint:$http_code")
        return 1
    fi
}

# Extract hashed asset URL from page
extract_asset_url() {
    local page_url="$1"
    local pattern="$2"

    curl -sf "$page_url" 2>/dev/null | \
        grep -oE "$pattern" | \
        head -1 || echo ""
}

# Main verification
verify_assets() {
    local all_passed=true

    log_step "Verifying Login Page Access"

    if ! check_endpoint "/web/login" "Login page"; then
        log_error "Login page not accessible - aborting"
        return 2
    fi

    log_step "Verifying Static Asset Endpoints"

    # Core asset bundles
    check_endpoint "/web/assets/debug/web.assets_common.js" "Common JS bundle" || all_passed=false
    check_endpoint "/web/assets/debug/web.assets_common.css" "Common CSS bundle" || all_passed=false
    check_endpoint "/web/assets/debug/web.assets_backend.js" "Backend JS bundle" || all_passed=false
    check_endpoint "/web/assets/debug/web.assets_backend.css" "Backend CSS bundle" || all_passed=false

    log_step "Verifying Hashed Asset URLs"

    # Extract actual hashed asset URLs from login page
    local login_html
    login_html=$(curl -sf "${ODOO_URL}/web/login" 2>/dev/null || echo "")

    if [ -n "$login_html" ]; then
        # Find any hashed asset URL
        local hashed_css
        hashed_css=$(echo "$login_html" | grep -oE '/web/assets/[^"]+\.css' | head -1 || echo "")

        if [ -n "$hashed_css" ]; then
            check_endpoint "$hashed_css" "Hashed CSS asset" || all_passed=false
        else
            log_warn "No hashed CSS assets found in login page"
        fi

        local hashed_js
        hashed_js=$(echo "$login_html" | grep -oE '/web/assets/[^"]+\.js' | head -1 || echo "")

        if [ -n "$hashed_js" ]; then
            check_endpoint "$hashed_js" "Hashed JS asset" || all_passed=false
        else
            log_warn "No hashed JS assets found in login page"
        fi
    else
        log_warn "Could not fetch login page for asset URL extraction"
    fi

    log_step "Verifying Web Client Static Files"

    # Static files that should always exist
    check_endpoint "/web/static/src/img/favicon.ico" "Favicon" || true  # Non-fatal
    check_endpoint "/web/static/lib/fontawesome/css/all.css" "FontAwesome CSS" || true  # Non-fatal

    if [ "$all_passed" = true ]; then
        return 0
    else
        return 1
    fi
}

# Generate summary report
generate_report() {
    local report=""

    report+="# AIUX Assets Verification Report\n"
    report+="\n"
    report+="**Generated:** $(date -Iseconds)\n"
    report+="**Odoo URL:** $ODOO_URL\n"
    report+="\n"

    report+="## Summary\n"
    report+="\n"
    report+="| Metric | Value |\n"
    report+="|--------|-------|\n"
    report+="| Passed | ${#PASSED_CHECKS[@]} |\n"
    report+="| Failed | ${#FAILED_CHECKS[@]} |\n"
    report+="| Total  | $((${#PASSED_CHECKS[@]} + ${#FAILED_CHECKS[@]})) |\n"
    report+="\n"

    if [ ${#PASSED_CHECKS[@]} -gt 0 ]; then
        report+="## Passed Checks\n"
        report+="\n"
        for check in "${PASSED_CHECKS[@]}"; do
            report+="- $check\n"
        done
        report+="\n"
    fi

    if [ ${#FAILED_CHECKS[@]} -gt 0 ]; then
        report+="## Failed Checks\n"
        report+="\n"
        for check in "${FAILED_CHECKS[@]}"; do
            report+="- $check\n"
        done
        report+="\n"
    fi

    echo -e "$report"
}

# Print summary to console
print_summary() {
    local status=$1

    echo ""
    echo "==================================================="
    echo "             AIUX ASSETS VERIFICATION              "
    echo "==================================================="
    echo ""
    echo "Odoo URL:     $ODOO_URL"
    echo ""
    echo "Results:"
    echo "  Passed:     ${#PASSED_CHECKS[@]}"
    echo "  Failed:     ${#FAILED_CHECKS[@]}"
    echo ""

    if [ "$status" -eq 0 ]; then
        echo -e "Status:       ${GREEN}PASSED${NC}"
    else
        echo -e "Status:       ${RED}FAILED${NC}"
        echo ""
        echo "Failed endpoints:"
        for check in "${FAILED_CHECKS[@]}"; do
            echo "  - $check"
        done
    fi

    echo "==================================================="
}

# Main execution
main() {
    local exit_code=0

    echo ""
    echo "==================================================="
    echo "          AIUX Assets Verification                 "
    echo "==================================================="
    echo ""
    echo "Configuration:"
    echo "  Odoo URL:   $ODOO_URL"
    echo "  Timeout:    ${TIMEOUT}s"
    echo ""

    if ! verify_assets; then
        exit_code=1
    fi

    # Generate report if output file specified
    if [ -n "$OUTPUT_FILE" ]; then
        log_step "Writing report to $OUTPUT_FILE"
        generate_report > "$OUTPUT_FILE"
        log_info "Report written to $OUTPUT_FILE"
    fi

    print_summary $exit_code

    # Also output machine-readable summary
    if [ "$VERBOSE" = true ]; then
        echo ""
        echo "JSON Summary:"
        echo "{"
        echo "  \"passed\": ${#PASSED_CHECKS[@]},"
        echo "  \"failed\": ${#FAILED_CHECKS[@]},"
        echo "  \"status\": $([ $exit_code -eq 0 ] && echo '\"pass\"' || echo '\"fail\"')"
        echo "}"
    fi

    exit $exit_code
}

main "$@"
