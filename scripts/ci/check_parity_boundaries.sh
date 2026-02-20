#!/usr/bin/env bash
# check_parity_boundaries.sh — enforce addons structure boundary
# Usage: ./check_parity_boundaries.sh [ci|pre-commit|update-baseline]
set -euo pipefail

# Modes
MODE="${1:-ci}"  # ci, pre-commit, update-baseline

# Baseline file
BASELINE_FILE="scripts/ci/baselines/parity_boundaries_baseline.json"

# Established integration-bridge modules (no justification file required)
# These are grandfathered and should NOT appear in new code
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
    "ipai_ocr_expense"
)

# EE parity keywords (high confidence indicators)
EE_KEYWORDS=(
    "subscription" "subscriptions"
    "forecast" "forecasting"
    "planning" "planner"
    "consolidation" "consolidated"
    "helpdesk" "ticket"
    "knowledge" "wiki"
    "sign" "signature" "esignature"
    "studio" "builder"
    "voip" "phone" "call"
    "documents" "document_management"
    "appointment" "booking" "calendar_appointment"
    "rental" "rentals"
    "social" "social_media"
    "whatsapp"
)

# Enterprise manifest dependencies
EE_MANIFEST_DEPS=(
    "web_enterprise"
    "base_enterprise"
    "web_studio"
    "web_mobile"
)

# Violation tracking
VIOLATIONS=()

# Utility functions
violation() {
    local msg="$1"
    VIOLATIONS+=("$msg")
    echo "❌ VIOLATION: $msg"
}

is_allowlisted() {
    local module="$1"
    for allowed in "${ALLOWLIST[@]}"; do
        [[ "$module" == "$allowed" ]] && return 0
    done
    return 1
}

# Check 1: EE keywords in wrong location (addons/ipai/)
check_keyword_violations() {
    echo "🔍 Checking for EE parity keywords in addons/ipai/..."

    if [[ ! -d "addons/ipai" ]]; then
        echo "   ℹ️  No addons/ipai/ directory found, skipping keyword checks"
        return 0
    fi

    for module_dir in addons/ipai/*/; do
        [[ ! -d "$module_dir" ]] && continue

        module=$(basename "$module_dir")
        is_allowlisted "$module" && continue

        # Check module name for EE keywords
        for keyword in "${EE_KEYWORDS[@]}"; do
            if echo "$module" | grep -qi "$keyword"; then
                violation "$module — module name contains EE keyword '$keyword' (should be in addons/oca/)"
            fi
        done

        # Check manifest file for EE dependencies
        manifest="$module_dir/__manifest__.py"
        if [[ -f "$manifest" ]]; then
            for dep in "${EE_MANIFEST_DEPS[@]}"; do
                if grep -q "'$dep'" "$manifest" 2>/dev/null || grep -q "\"$dep\"" "$manifest" 2>/dev/null; then
                    violation "$module — __manifest__.py depends on '$dep' (Enterprise dependency, should be in addons/oca/)"
                fi
            done
        fi
    done
}

# Check 2: Missing justification files
check_justification_files() {
    echo "🔍 Checking for PARITY_CONNECTOR_JUSTIFICATION.md in addons/ipai/..."

    if [[ ! -d "addons/ipai" ]]; then
        echo "   ℹ️  No addons/ipai/ directory found, skipping justification checks"
        return 0
    fi

    for module_dir in addons/ipai/*/; do
        [[ ! -d "$module_dir" ]] && continue

        module=$(basename "$module_dir")
        is_allowlisted "$module" && continue

        if [[ ! -f "$module_dir/PARITY_CONNECTOR_JUSTIFICATION.md" ]]; then
            violation "$module — missing PARITY_CONNECTOR_JUSTIFICATION.md (required for ipai namespace)"
        fi
    done
}

# Load baseline violations
load_baseline() {
    if [[ ! -f "$BASELINE_FILE" ]]; then
        echo "[]"
        return
    fi

    # Extract violation messages from JSON
    jq -r '.violations[]' "$BASELINE_FILE" 2>/dev/null || echo "[]"
}

# Compare current violations with baseline
compare_with_baseline() {
    if [[ ${#VIOLATIONS[@]} -eq 0 ]]; then
        echo ""
        echo "✅ PASS — all parity boundaries respected (0 violations)"
        return 0
    fi

    # Load baseline
    baseline_violations=$(load_baseline)

    # Find new violations (not in baseline)
    NEW_VIOLATIONS=()
    for violation in "${VIOLATIONS[@]}"; do
        if ! echo "$baseline_violations" | grep -Fxq "$violation" 2>/dev/null; then
            NEW_VIOLATIONS+=("$violation")
        fi
    done

    if [[ ${#NEW_VIOLATIONS[@]} -gt 0 ]]; then
        echo ""
        echo "❌ FAIL: ${#NEW_VIOLATIONS[@]} new parity boundary violation(s) detected:"
        echo ""
        printf '  %s\n' "${NEW_VIOLATIONS[@]}"
        echo ""
        echo "To fix:"
        echo "  1. Move EE parity modules to addons/oca/"
        echo "  2. Add PARITY_CONNECTOR_JUSTIFICATION.md for integration bridges"
        echo "  3. See docs/architecture/ADDONS_STRUCTURE_BOUNDARY.md for guidance"
        echo ""
        echo "To update baseline (if violations are intentional):"
        echo "  ./scripts/ci/check_parity_boundaries.sh update-baseline"
        return 1
    fi

    # All violations are in baseline
    echo ""
    echo "✅ PASS (${#VIOLATIONS[@]} baseline violations, 0 new violations)"
    echo ""
    echo "Baseline violations (grandfathered):"
    printf '  %s\n' "${VIOLATIONS[@]}"
    echo ""
    echo "Target: Zero violations by 2026-08-20 (incremental migration)"
    return 0
}

# Update baseline file
update_baseline() {
    echo "📝 Updating baseline file..."

    # Create baselines directory if needed
    mkdir -p "$(dirname "$BASELINE_FILE")"

    # Generate JSON baseline
    cat > "$BASELINE_FILE" <<EOF
{
  "updated": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "target_date": "2026-08-20",
  "migration_policy": "incremental (7-8 modules per month)",
  "violations": [
$(for v in "${VIOLATIONS[@]}"; do echo "    \"$v\","; done | sed '$ s/,$//')
  ],
  "total": ${#VIOLATIONS[@]}
}
EOF

    echo "✅ Baseline updated: $BASELINE_FILE"
    echo "   Total violations: ${#VIOLATIONS[@]}"

    # Show baseline
    cat "$BASELINE_FILE"
}

# Main execution
main() {
    echo "========================================"
    echo "Parity Boundaries Check ($MODE mode)"
    echo "========================================"
    echo ""

    # Run checks
    check_keyword_violations
    check_justification_files

    # Handle mode
    case "$MODE" in
        update-baseline)
            update_baseline
            exit 0
            ;;
        ci|pre-commit)
            compare_with_baseline
            exit $?
            ;;
        *)
            echo "❌ Unknown mode: $MODE"
            echo "Usage: $0 [ci|pre-commit|update-baseline]"
            exit 1
            ;;
    esac
}

main
