#!/usr/bin/env bash
# check_parity_boundaries.sh — warn on ipai_* modules without justification
set -euo pipefail

# Established integration-bridge modules (no justification file required)
ALLOWLIST=(
    "ipai_enterprise_bridge"
    "ipai_slack_connector"
    "ipai_auth_oidc"
    "ipai_ai_tools"
    "ipai_mcp_bridge"
    "ipai_rest_controllers"
    "ipai_finance_ppm"
    "ipai_bir_compliance"
    "ipai_bir_alphalist"
    "ipai_bir_itad"
    "ipai_bir_qap"
)

BASELINE_FILE="scripts/ci/parity_boundaries.baseline.txt"
FAIL_ON_NEW="${FAIL_ON_NEW:-1}"
WARNINGS=0
WARNINGS_LIST=()

warn() {
    echo "WARN: $1"
    WARNINGS=$((WARNINGS + 1))
    WARNINGS_LIST+=("WARN: $1")
}

for module_dir in addons/ipai/*/; do
    module=$(basename "$module_dir")
    allowed=0
    for a in "${ALLOWLIST[@]}"; do
        [[ "$module" == "$a" ]] && allowed=1 && break
    done
    [[ "$allowed" == "1" ]] && continue

    if [[ ! -f "$module_dir/PARITY_CONNECTOR_JUSTIFICATION.md" ]]; then
        warn "$module — no PARITY_CONNECTOR_JUSTIFICATION.md"
        echo "      If EE-parity: move to addons/oca/*"
        echo "      If connector/glue: add justification file"
    fi
done

# Baseline comparison for warnings
if [ "$WARNINGS" -gt 0 ]; then
    if [ -f "$BASELINE_FILE" ] && [ "$FAIL_ON_NEW" = "1" ]; then
        # Check for new warnings
        NEW_WARNINGS=()
        for w in "${WARNINGS_LIST[@]}"; do
            if ! grep -Fxq "$w" "$BASELINE_FILE" 2>/dev/null; then
                NEW_WARNINGS+=("$w")
            fi
        done

        if [ "${#NEW_WARNINGS[@]}" -gt 0 ]; then
            echo ""
            echo "❌ FAIL: New parity boundary warnings detected:"
            printf '%s\n' "${NEW_WARNINGS[@]}"
            echo ""
            echo "To update baseline (if intentional):"
            echo "  bash scripts/ci/check_parity_boundaries.sh 2>&1 | grep '^WARN:' | sort > scripts/ci/parity_boundaries.baseline.txt"
            exit 1
        fi
    fi
    echo ""
    echo "✅ PASS (with $WARNINGS baseline warnings, no new violations)"
    exit 0
else
    echo "✅ PASS — all parity boundaries respected."
    exit 0
fi
