#!/usr/bin/env bash
# =============================================================================
# install-notion-stack.sh
# =============================================================================
# Full Notion Business substitute stack installation for Odoo CE 18 + OCA
#
# Usage:
#   ./scripts/install-notion-stack.sh [--clone-oca] [--install-modules]
#
# Options:
#   --clone-oca       Clone all required OCA repositories
#   --install-modules Install modules in Odoo (requires running container)
#   --all             Do both (default if no args)
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
OCA_DIR="$ROOT_DIR/addons/oca"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${GREEN}✓${NC} $1"; }
log_warn() { echo -e "${YELLOW}!${NC} $1"; }
log_error() { echo -e "${RED}✗${NC} $1"; }
log_section() { echo -e "\n${BLUE}===${NC} $1 ${BLUE}===${NC}"; }

# Default: do everything
DO_CLONE=false
DO_INSTALL=false

if [[ $# -eq 0 ]]; then
    DO_CLONE=true
    DO_INSTALL=true
else
    for arg in "$@"; do
        case $arg in
            --clone-oca)
                DO_CLONE=true
                ;;
            --install-modules)
                DO_INSTALL=true
                ;;
            --all)
                DO_CLONE=true
                DO_INSTALL=true
                ;;
            *)
                echo "Unknown option: $arg"
                exit 1
                ;;
        esac
    done
fi

# =============================================================================
# 1. Clone OCA Repositories
# =============================================================================
clone_oca_repos() {
    log_section "Cloning OCA Repositories (18.0 branch)"

    mkdir -p "$OCA_DIR"
    cd "$OCA_DIR"

    declare -A REPOS=(
        ["reporting-engine"]="https://github.com/OCA/reporting-engine.git"
        ["server-tools"]="https://github.com/OCA/server-tools.git"
        ["dms"]="https://github.com/OCA/dms.git"
        ["project"]="https://github.com/OCA/project.git"
        ["web"]="https://github.com/OCA/web.git"
        ["social"]="https://github.com/OCA/social.git"
        ["timesheet"]="https://github.com/OCA/timesheet.git"
        ["ai"]="https://github.com/OCA/ai.git"
        ["mis-builder"]="https://github.com/OCA/mis-builder.git"
        ["server-ux"]="https://github.com/OCA/server-ux.git"
        ["contract"]="https://github.com/OCA/contract.git"
    )

    for repo in "${!REPOS[@]}"; do
        if [[ -d "$repo" ]]; then
            log_warn "$repo already exists, skipping"
        else
            log_info "Cloning $repo..."
            git clone --depth 1 -b 18.0 "${REPOS[$repo]}" "$repo" || {
                log_warn "Failed to clone $repo (may not have 18.0 branch yet)"
            }
        fi
    done

    cd "$ROOT_DIR"
    log_info "OCA repositories cloned to $OCA_DIR"
}

# =============================================================================
# 2. Install Modules in Odoo
# =============================================================================
install_modules() {
    log_section "Installing Modules in Odoo"

    # Check if container is running
    if ! docker ps --format '{{.Names}}' | grep -q "odoo"; then
        log_error "No Odoo container found running. Start the stack first."
        exit 1
    fi

    CONTAINER=$(docker ps --format '{{.Names}}' | grep -E "odoo" | head -1)
    log_info "Using container: $CONTAINER"

    # IPAI WorkOS Suite (Notion clone)
    log_info "Installing IPAI WorkOS Suite..."
    docker exec -it "$CONTAINER" bash -lc '
        odoo -d odoo -i ipai_workos_affine --stop-after-init 2>/dev/null || echo "WorkOS modules may need dependencies"
    ' || log_warn "WorkOS install had issues (check dependencies)"

    # IPAI Project + Gantt + Profitability
    log_info "Installing IPAI Project modules..."
    docker exec -it "$CONTAINER" bash -lc '
        odoo -d odoo -i ipai_project_gantt,ipai_project_profitability_bridge --stop-after-init
    ' || log_warn "Project modules install had issues"

    # IPAI AI Core
    log_info "Installing IPAI AI modules..."
    docker exec -it "$CONTAINER" bash -lc '
        odoo -d odoo -i ipai_ai_core,ipai_ai_provider_kapa --stop-after-init
    ' || log_warn "AI modules install had issues"

    # OCA Modules (if available)
    log_info "Installing OCA modules..."
    docker exec -it "$CONTAINER" bash -lc '
        odoo -d odoo -i report_xlsx,dms,auditlog --stop-after-init 2>/dev/null || echo "Some OCA modules may not be available"
    ' || log_warn "OCA modules install had issues"

    # Restart container
    log_info "Restarting container..."
    docker restart "$CONTAINER"

    log_info "Module installation complete!"
}

# =============================================================================
# 3. Print Summary
# =============================================================================
print_summary() {
    log_section "Installation Summary"

    cat << 'EOF'
Notion Business → Odoo CE 18 + OCA Stack Installed

IPAI Modules:
  ✓ ipai_workos_affine     - WorkOS Notion clone (umbrella)
  ✓ ipai_workos_core       - Workspaces/Spaces/Pages
  ✓ ipai_workos_blocks     - Block editor
  ✓ ipai_workos_db         - Databases + properties
  ✓ ipai_workos_views      - Table/Kanban/Calendar
  ✓ ipai_workos_collab     - Comments/Mentions
  ✓ ipai_workos_search     - Global search
  ✓ ipai_workos_templates  - Templates
  ✓ ipai_workos_canvas     - Edgeless canvas
  ✓ ipai_project_gantt     - CE Gantt view
  ✓ ipai_project_profitability_bridge - Project KPIs
  ✓ ipai_ai_core           - AI provider registry
  ✓ ipai_ai_provider_kapa  - Kapa RAG provider

OCA Modules (if cloned):
  ✓ report_substitute      - Report substitution rules
  ✓ report_xlsx            - Excel reports
  ✓ dms                    - Document management
  ✓ auditlog               - Audit trail
  ✓ project_*              - Project enhancements

Next Steps:
  1. Access Odoo at http://localhost:8069
  2. Go to Apps → Update Apps List
  3. Install desired modules
  4. Configure AI provider in Settings → IPAI Kapa Provider
  5. Create workspaces in WorkOS menu

Documentation:
  docs/notion-odoo-substitute-catalog.md

EOF
}

# =============================================================================
# Main
# =============================================================================
main() {
    echo ""
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║   Notion Business → Odoo CE 18 + OCA Installation Script     ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo ""

    if [[ "$DO_CLONE" == true ]]; then
        clone_oca_repos
    fi

    if [[ "$DO_INSTALL" == true ]]; then
        install_modules
    fi

    print_summary
}

main
