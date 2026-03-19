#!/usr/bin/env bash
# =============================================================================
# Platform Kit Integration Audit Runner
# =============================================================================
# Runs integration health checks defined in the manifest.
#
# Usage:
#   ./scripts/audit/run_integration_audit.sh [OPTIONS]
#
# Options:
#   --integration NAME   Run only the specified integration check
#   --category NAME      Run only checks in the specified category
#   --dry-run           Show what would be run without executing
#   --json              Output results as JSON
#   --fail-fast         Stop on first failure
#   --help              Show this help message
#
# Environment:
#   AUDIT_MANIFEST      Path to manifest (default: config/integrations/integration_manifest.yaml)
#   AUDIT_RESULTS_DIR   Where to store results (default: .audit/results)
#
# Exit codes:
#   0 - All checks passed
#   1 - One or more blocking checks failed
#   2 - Script error
# =============================================================================

set -euo pipefail

# Defaults
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
MANIFEST="${AUDIT_MANIFEST:-$REPO_ROOT/config/integrations/integration_manifest.yaml}"
RESULTS_DIR="${AUDIT_RESULTS_DIR:-$REPO_ROOT/.audit/results}"
TIMESTAMP=$(date -u +"%Y%m%dT%H%M%SZ")

# Options
DRY_RUN=false
JSON_OUTPUT=false
FAIL_FAST=false
INTEGRATION_FILTER=""
CATEGORY_FILTER=""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# =============================================================================
# Helper Functions
# =============================================================================

usage() {
    head -30 "$0" | grep "^#" | sed 's/^# \?//'
    exit 0
}

log() {
    echo -e "${BLUE}[audit]${NC} $*" >&2
}

log_ok() {
    echo -e "${GREEN}[  OK ]${NC} $*"
}

log_fail() {
    echo -e "${RED}[FAIL ]${NC} $*"
}

log_warn() {
    echo -e "${YELLOW}[WARN ]${NC} $*"
}

log_skip() {
    echo -e "${BLUE}[SKIP ]${NC} $*"
}

# =============================================================================
# Parse Arguments
# =============================================================================

while [[ $# -gt 0 ]]; do
    case $1 in
        --integration)
            INTEGRATION_FILTER="$2"
            shift 2
            ;;
        --category)
            CATEGORY_FILTER="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --json)
            JSON_OUTPUT=true
            shift
            ;;
        --fail-fast)
            FAIL_FAST=true
            shift
            ;;
        --help|-h)
            usage
            ;;
        *)
            echo "Unknown option: $1" >&2
            usage
            ;;
    esac
done

# =============================================================================
# Validation
# =============================================================================

if [[ ! -f "$MANIFEST" ]]; then
    echo "Error: Manifest not found: $MANIFEST" >&2
    exit 2
fi

# Create results directory
mkdir -p "$RESULTS_DIR"

# =============================================================================
# Run Checks
# =============================================================================

cd "$REPO_ROOT"

# Track results
TOTAL=0
PASSED=0
FAILED=0
WARNED=0
SKIPPED=0
BLOCKING_FAILED=0

# Results array for JSON output
RESULTS=()

run_check() {
    local name="$1"
    local check_script="$2"
    local blocking="$3"

    ((TOTAL++))

    if [[ ! -f "$check_script" ]]; then
        log_skip "$name (check not found: $check_script)"
        ((SKIPPED++))
        RESULTS+=("{\"integration\": \"$name\", \"status\": \"skip\", \"reason\": \"check not found\"}")
        return 0
    fi

    if [[ "$DRY_RUN" == "true" ]]; then
        log "[dry-run] Would run: python $check_script"
        return 0
    fi

    # Run the check
    local output
    local exit_code=0
    output=$(python "$check_script" 2>&1) || exit_code=$?

    # Parse result status from JSON output
    local status
    status=$(echo "$output" | python -c "import sys,json; print(json.load(sys.stdin).get('status','error'))" 2>/dev/null || echo "error")

    case "$status" in
        ok)
            log_ok "$name"
            ((PASSED++))
            RESULTS+=("$output")
            ;;
        fail)
            log_fail "$name"
            echo "$output" | python -c "import sys,json; d=json.load(sys.stdin); print(f\"  └─ {d.get('code','unknown')}: {d.get('data',{}).get('message','')}\")" 2>/dev/null || echo "  └─ $output"
            ((FAILED++))
            if [[ "$blocking" == "true" ]]; then
                ((BLOCKING_FAILED++))
            fi
            RESULTS+=("$output")
            if [[ "$FAIL_FAST" == "true" && "$blocking" == "true" ]]; then
                return 1
            fi
            ;;
        warn)
            log_warn "$name"
            echo "$output" | python -c "import sys,json; d=json.load(sys.stdin); print(f\"  └─ {d.get('code','unknown')}: {d.get('data',{}).get('message','')}\")" 2>/dev/null || true
            ((WARNED++))
            RESULTS+=("$output")
            ;;
        skip)
            log_skip "$name"
            ((SKIPPED++))
            RESULTS+=("$output")
            ;;
        *)
            log_fail "$name (check error)"
            echo "  └─ $output" | head -5
            ((FAILED++))
            if [[ "$blocking" == "true" ]]; then
                ((BLOCKING_FAILED++))
            fi
            RESULTS+=("{\"integration\": \"$name\", \"status\": \"error\", \"output\": \"$(echo "$output" | head -c 500 | tr '\n' ' ')\"}")
            ;;
    esac

    return 0
}

# =============================================================================
# Main Execution
# =============================================================================

log "Starting integration audit"
log "Manifest: $MANIFEST"
log "Results: $RESULTS_DIR"
echo ""

# Priority 0: Policy checks first
if [[ -z "$INTEGRATION_FILTER" || "$INTEGRATION_FILTER" == "policy" ]]; then
    if [[ -z "$CATEGORY_FILTER" || "$CATEGORY_FILTER" == "policy" ]]; then
        run_check "policy" "scripts/audit/checks/check_domain_policy.py" "true" || {
            if [[ "$FAIL_FAST" == "true" ]]; then
                echo ""
                log_fail "Audit aborted (fail-fast mode)"
                exit 1
            fi
        }
    fi
fi

# Mailgun check
if [[ -z "$INTEGRATION_FILTER" || "$INTEGRATION_FILTER" == "mailgun" ]]; then
    if [[ -z "$CATEGORY_FILTER" || "$CATEGORY_FILTER" == "email" ]]; then
        run_check "mailgun" "scripts/audit/checks/check_mailgun.py" "false"
    fi
fi

# Add more checks here as they are implemented...

# =============================================================================
# Summary
# =============================================================================

echo ""
echo "=============================================="
echo "Integration Audit Summary"
echo "=============================================="
echo "Total:    $TOTAL"
echo "Passed:   $PASSED"
echo "Failed:   $FAILED (blocking: $BLOCKING_FAILED)"
echo "Warned:   $WARNED"
echo "Skipped:  $SKIPPED"
echo "=============================================="

# Save results
RESULT_FILE="$RESULTS_DIR/audit-$TIMESTAMP.json"
{
    echo "{"
    echo "  \"timestamp\": \"$TIMESTAMP\","
    echo "  \"summary\": {"
    echo "    \"total\": $TOTAL,"
    echo "    \"passed\": $PASSED,"
    echo "    \"failed\": $FAILED,"
    echo "    \"blocking_failed\": $BLOCKING_FAILED,"
    echo "    \"warned\": $WARNED,"
    echo "    \"skipped\": $SKIPPED"
    echo "  },"
    echo "  \"results\": ["
    local first=true
    for r in "${RESULTS[@]}"; do
        if [[ "$first" == "true" ]]; then
            first=false
        else
            echo ","
        fi
        echo "    $r"
    done
    echo ""
    echo "  ]"
    echo "}"
} > "$RESULT_FILE"

log "Results saved to: $RESULT_FILE"

# Exit code
if [[ $BLOCKING_FAILED -gt 0 ]]; then
    echo ""
    log_fail "$BLOCKING_FAILED blocking check(s) failed"
    exit 1
fi

if [[ $FAILED -gt 0 ]]; then
    echo ""
    log_warn "$FAILED non-blocking check(s) failed"
    exit 0
fi

echo ""
log_ok "All checks passed"
exit 0
