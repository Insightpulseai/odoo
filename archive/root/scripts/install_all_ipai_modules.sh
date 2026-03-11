#!/usr/bin/env bash
#
# IPAI Custom Modules - Complete Installation Script
# Installs all 33 ipai_* modules in correct dependency order
#
set -euo pipefail

CONTAINER="${ODOO_CONTAINER:-odoo-core}"
DB="${ODOO_DB:-odoo_core}"

echo "================================================================================"
echo "IPAI Custom Modules - Complete Installation"
echo "================================================================================"
echo "Container: ${CONTAINER}"
echo "Database:  ${DB}"
echo ""

# Define installation phases with dependencies
# Phase 1: Core Odoo modules (prerequisites)
PHASE_1_CORE=(
    "account"
    "project"
    "hr"
    "resource"
    "crm"
    "sale"
    "stock"
)

# Phase 2: IPAI Platform foundation
PHASE_2_PLATFORM=(
    "ipai_platform_audit"
    "ipai_platform_permissions"
    "ipai_platform_theme"
    "ipai_platform_workflow"
    "ipai_platform_approvals"
)

# Phase 3: IPAI Core utilities
PHASE_3_UTILITIES=(
    "ipai_ask_ai"
    "ipai_ask_ai_chatter"
    "ipai_grid_view"
    "ipai_ocr_gateway"
    "ipai_sms_gateway"
)

# Phase 4: Finance & BIR modules
PHASE_4_FINANCE=(
    "ipai_tbwa_finance"
    "ipai_bir_tax_compliance"
    "ipai_month_end"
    "ipai_finance_closing"
    "ipai_finance_close_seed"
    "ipai_month_end_closing"
)

# Phase 5: PPM & Project modules
PHASE_5_PPM=(
    "ipai_finance_ppm_golive"
    "ipai_finance_ppm_umbrella"
    "ipai_ppm_a1"
    "ipai_close_orchestration"
)

# Phase 6: WorkOS foundation
PHASE_6_WORKOS_CORE=(
    "ipai_workos_core"
    "ipai_workos_blocks"
    "ipai_workos_db"
)

# Phase 7: WorkOS features
PHASE_7_WORKOS_FEATURES=(
    "ipai_workos_canvas"
    "ipai_workos_collab"
    "ipai_workos_search"
    "ipai_workos_templates"
    "ipai_workos_views"
)

# Phase 8: WorkOS umbrella
PHASE_8_WORKOS_UMBRELLA=(
    "ipai_workos_affine"
)

# Phase 9: Integrations & Themes
PHASE_9_INTEGRATIONS=(
    "ipai_superset_connector"
    "ipai_crm_pipeline"
    "ipai_web_theme_chatgpt"
    "ipai_theme_tbwa_backend"
)

# Function to install modules in a phase
install_phase() {
    local phase_name="$1"
    shift
    local modules=("$@")

    if [ ${#modules[@]} -eq 0 ]; then
        echo "⚠️  ${phase_name}: No modules to install"
        return 0
    fi

    echo ""
    echo "================================================================================"
    echo "${phase_name}"
    echo "================================================================================"

    local module_list=$(IFS=,; echo "${modules[*]}")

    echo "📦 Installing: ${module_list}"
    echo ""

    docker exec -i "${CONTAINER}" bash -lc "
        set -euo pipefail
        odoo -c /etc/odoo/odoo.conf -d '${DB}' -i '${module_list}' --stop-after-init
    " 2>&1 | tee -a /tmp/ipai_install.log

    local exit_code=${PIPESTATUS[0]}

    if [ $exit_code -eq 0 ]; then
        echo "✅ ${phase_name} completed successfully"
    else
        echo "❌ ${phase_name} failed with exit code ${exit_code}"
        echo "   Check /tmp/ipai_install.log for details"
        return $exit_code
    fi
}

# Create log file
echo "Installation started: $(date)" > /tmp/ipai_install.log

# Execute installation phases
install_phase "PHASE 1: Core Odoo Modules" "${PHASE_1_CORE[@]}"
install_phase "PHASE 2: IPAI Platform Foundation" "${PHASE_2_PLATFORM[@]}"
install_phase "PHASE 3: IPAI Core Utilities" "${PHASE_3_UTILITIES[@]}"
install_phase "PHASE 4: Finance & BIR Modules" "${PHASE_4_FINANCE[@]}"
install_phase "PHASE 5: PPM & Project Modules" "${PHASE_5_PPM[@]}"
install_phase "PHASE 6: WorkOS Core Foundation" "${PHASE_6_WORKOS_CORE[@]}"
install_phase "PHASE 7: WorkOS Features" "${PHASE_7_WORKOS_FEATURES[@]}"
install_phase "PHASE 8: WorkOS Umbrella" "${PHASE_8_WORKOS_UMBRELLA[@]}"
install_phase "PHASE 9: Integrations & Themes" "${PHASE_9_INTEGRATIONS[@]}"

echo ""
echo "================================================================================"
echo "🔄 Restarting Odoo container..."
echo "================================================================================"
docker restart "${CONTAINER}"

echo ""
echo "⏳ Waiting for container to be ready..."
sleep 10

echo ""
echo "================================================================================"
echo "✅ Installation Complete!"
echo "================================================================================"
echo ""
echo "Verification:"
echo "  1. Check logs: docker logs --tail=200 ${CONTAINER}"
echo "  2. Access Odoo: http://localhost:8069"
echo "  3. Verify modules: Apps menu → filter 'ipai'"
echo ""
echo "Full installation log: /tmp/ipai_install.log"
echo ""
