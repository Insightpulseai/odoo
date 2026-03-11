#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Module Drift Gate - CI check that prevents module quality regressions
# ---------------------------------------------------------------------------
# Usage: ./scripts/ci/module_drift_gate.sh [--baseline FILE] [--strict]
#
# This script runs the module audit agent and compares results against
# a baseline to detect regressions. It fails CI if:
#   - Any module goes from PASS to WARN or FAIL
#   - Any module goes from WARN to FAIL
#   - (with --strict) Any new warnings are introduced
#
# Exit codes:
#   0 = No regressions detected
#   1 = Regressions detected
#   2 = Script/config error
# ---------------------------------------------------------------------------

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
AUDIT_SCRIPT="$REPO_ROOT/scripts/module_audit_agent.py"
COMPARE_SCRIPT="$SCRIPT_DIR/compare_audit_baseline.py"
OUTPUT_DIR="$REPO_ROOT/artifacts"
BASELINE_FILE="${OUTPUT_DIR}/module_audit_baseline.json"
CURRENT_FILE="${OUTPUT_DIR}/module_audit_matrix.json"
STRICT_FLAG=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --baseline)
            BASELINE_FILE="$2"
            shift 2
            ;;
        --strict)
            STRICT_FLAG="--strict"
            shift
            ;;
        --help|-h)
            head -20 "$0" | tail -18
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 2
            ;;
    esac
done

echo "=== Module Drift Gate ==="
echo "Baseline: $BASELINE_FILE"
echo "Strict mode: ${STRICT_FLAG:+enabled}"
echo ""

# Ensure output directory exists
mkdir -p "$OUTPUT_DIR"

# Run the audit
echo "Running module audit..."
python "$AUDIT_SCRIPT" --output "$OUTPUT_DIR/" 2>/dev/null

if [[ $? -ne 0 ]]; then
    echo "ERROR: Module audit failed"
    exit 2
fi

echo ""

# Check if baseline exists
if [[ ! -f "$BASELINE_FILE" ]]; then
    echo "No baseline found at $BASELINE_FILE"
    echo "Creating baseline from current audit..."
    cp "$CURRENT_FILE" "$BASELINE_FILE"
    echo "Baseline created. Run again to check for drift."
    exit 0
fi

# Compare baseline vs current
echo "Comparing against baseline..."
echo ""

python "$COMPARE_SCRIPT" \
    --baseline "$BASELINE_FILE" \
    --current "$CURRENT_FILE" \
    $STRICT_FLAG

exit_code=$?

# Update baseline if requested via env var
if [[ "${UPDATE_BASELINE:-false}" == "true" && $exit_code -eq 0 ]]; then
    echo ""
    echo "Updating baseline..."
    cp "$CURRENT_FILE" "$BASELINE_FILE"
    echo "Baseline updated."
fi

exit $exit_code
