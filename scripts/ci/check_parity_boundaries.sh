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

WARNINGS=0
for module_dir in addons/ipai/*/; do
    module=$(basename "$module_dir")
    allowed=0
    for a in "${ALLOWLIST[@]}"; do
        [[ "$module" == "$a" ]] && allowed=1 && break
    done
    [[ "$allowed" == "1" ]] && continue

    if [[ ! -f "$module_dir/PARITY_CONNECTOR_JUSTIFICATION.md" ]]; then
        echo "WARN: $module — no PARITY_CONNECTOR_JUSTIFICATION.md"
        echo "      If EE-parity: move to addons/oca/*"
        echo "      If connector/glue: add justification file"
        WARNINGS=$((WARNINGS + 1))
    fi
done

echo "Parity boundary check: $WARNINGS warning(s)"
# WARN only; exit 0 until remediation sprint completes
exit 0
