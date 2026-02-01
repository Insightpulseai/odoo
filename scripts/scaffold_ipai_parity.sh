#!/bin/bash
# Scaffold all missing ipai_* modules for EE parity
# Usage: ./scripts/scaffold_ipai_parity.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
IPAI_DIR="${REPO_ROOT}/addons/ipai"
ODOO_VERSION="${ODOO_VERSION:-19.0}"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# ipai modules to scaffold with descriptions
declare -A IPAI_MODULES=(
    ["ipai_ai_agent_builder"]="AI Agent Builder|AI agents with system prompts, topics, tools|ipai_dev_studio_base"
    ["ipai_ai_rag"]="AI RAG Pipeline|RAG for document-based context retrieval|ipai_ai_agent_builder"
    ["ipai_ai_tools"]="AI Tool Registry|Audited tool execution for AI agents|ipai_ai_agent_builder"
    ["ipai_ai_fields"]="AI Fields|AI-powered field population|ipai_ai_agent_builder"
    ["ipai_ai_automations"]="AI Automations|AI in server actions|ipai_ai_agent_builder,base_automation"
    ["ipai_ai_livechat"]="AI Livechat|AI agent for live chat|ipai_ai_agent_builder,im_livechat"
    ["ipai_finance_tax_return"]="Tax Return Workflow|Tax return with validation|account"
    ["ipai_whatsapp_connector"]="WhatsApp Connector|WhatsApp messaging integration|mail"
    ["ipai_project_templates"]="Project Templates|Project and task templates|project"
    ["ipai_planning_attendance"]="Planning Attendance|Compare planned vs attended|hr_attendance"
    ["ipai_esg"]="ESG Carbon Analytics|Carbon footprint tracking|base"
    ["ipai_esg_social"]="ESG Social Metrics|Gender parity and pay gap|hr"
    ["ipai_helpdesk_refund"]="Helpdesk Refunds|Gift card reimbursements|ipai_helpdesk"
    ["ipai_documents_ai"]="Documents AI|AI document classification|dms"
    ["ipai_sign"]="Electronic Sign|Document envelopes for signing|mail"
    ["ipai_equity"]="Equity Management|Share and shareholder tracking|base"
)

scaffold_module() {
    local module_name="$1"
    local module_info="${IPAI_MODULES[$module_name]}"
    local module_title module_desc module_deps

    IFS='|' read -r module_title module_desc module_deps <<< "$module_info"
    local module_path="${IPAI_DIR}/${module_name}"

    if [[ -d "$module_path" ]]; then
        log_warn "Module ${module_name} already exists, skipping scaffold"
        return 0
    fi

    log_info "Scaffolding ${module_name}..."
    mkdir -p "${module_path}"/{models,views,security,data,static/description}

    # Create __manifest__.py
    local title_underline
    title_underline=$(printf '=%.0s' $(seq 1 ${#module_title}))
    local depends_list
    depends_list=$(echo "$module_deps" | sed 's/,/", "/g' | sed 's/^/"/' | sed 's/$/"/')

    cat > "${module_path}/__manifest__.py" << EOF
# -*- coding: utf-8 -*-
{
    "name": "${module_title}",
    "version": "${ODOO_VERSION}.1.0.0",
    "category": "InsightPulse AI",
    "summary": "${module_desc}",
    "description": """
${module_title}
${title_underline}

${module_desc}

This module provides Odoo 19 Enterprise Edition parity for CE deployments.

**Features:**
- Feature 1
- Feature 2
- Feature 3

**Configuration:**
- Go to Settings > IPAI > ${module_title}

**Credits:**
- InsightPulse AI Team
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.com",
    "license": "LGPL-3",
    "depends": [${depends_list}],
    "data": [
        "security/ir.model.access.csv",
        "views/menu.xml",
    ],
    "demo": [],
    "installable": True,
    "application": False,
    "auto_install": False,
}
EOF

    # Create __init__.py
    cat > "${module_path}/__init__.py" << 'EOF'
# -*- coding: utf-8 -*-
from . import models
EOF

    # Create models/__init__.py
    local model_name="${module_name/ipai_/}"
    model_name="${model_name//_/.}"
    cat > "${module_path}/models/__init__.py" << EOF
# -*- coding: utf-8 -*-
from . import ${module_name/ipai_/}
EOF

    # Create main model file
    local class_name
    class_name=$(echo "${module_name/ipai_/}" | sed -r 's/(^|_)([a-z])/\U\2/g')
    cat > "${module_path}/models/${module_name/ipai_/}.py" << EOF
# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ${class_name}(models.Model):
    _name = "ipai.${model_name}"
    _description = "${module_title}"

    name = fields.Char(string="Name", required=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
    )
    notes = fields.Text(string="Notes")

    # TODO: Add specific fields for ${module_title}
EOF

    # Create security file
    cat > "${module_path}/security/ir.model.access.csv" << EOF
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_${module_name/ipai_/}_user,${module_name/ipai_/}.user,model_ipai_${model_name//./_},base.group_user,1,0,0,0
access_${module_name/ipai_/}_manager,${module_name/ipai_/}.manager,model_ipai_${model_name//./_},base.group_system,1,1,1,1
EOF

    # Create menu view
    cat > "${module_path}/views/menu.xml" << EOF
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Menu items will be added here -->
    <!--
    <menuitem
        id="menu_${module_name/ipai_/}_root"
        name="${module_title}"
        sequence="100"
    />
    -->
</odoo>
EOF

    # Create README
    cat > "${module_path}/README.md" << EOF
# ${module_title}

## Description

${module_desc}

This module provides Odoo 19 Enterprise Edition parity for CE deployments.

## Dependencies

$(echo "$module_deps" | tr ',' '\n' | sed 's/^/- /')

## Configuration

1. Install the module
2. Go to Settings > IPAI > ${module_title}
3. Configure as needed

## Usage

TODO: Add usage instructions

## Credits

- InsightPulse AI Team

## License

LGPL-3
EOF

    # Create icon placeholder
    cat > "${module_path}/static/description/icon.png" << 'EOF'
EOF
    # Note: Actual icon should be added manually

    log_info "Scaffolded ${module_name} at ${module_path}"
}

check_existing() {
    local existing=0
    local missing=0

    for module in "${!IPAI_MODULES[@]}"; do
        if [[ -d "${IPAI_DIR}/${module}" ]]; then
            ((existing++))
        else
            ((missing++))
        fi
    done

    echo "Existing: ${existing}, Missing: ${missing}"
}

scaffold_all() {
    log_info "Scaffolding all missing ipai_* modules for EE parity..."
    mkdir -p "$IPAI_DIR"

    local created=0
    local skipped=0

    for module in "${!IPAI_MODULES[@]}"; do
        if [[ -d "${IPAI_DIR}/${module}" ]]; then
            log_warn "${module} exists, skipping"
            ((skipped++))
        else
            scaffold_module "$module"
            ((created++))
        fi
    done

    echo ""
    echo "=========================================="
    echo "SCAFFOLD SUMMARY"
    echo "=========================================="
    echo "Created: ${created}"
    echo "Skipped: ${skipped}"
    echo "Total modules: ${#IPAI_MODULES[@]}"
    echo "=========================================="
}

list_modules() {
    echo "ipai_* modules for EE parity:"
    echo ""
    for module in "${!IPAI_MODULES[@]}"; do
        local info="${IPAI_MODULES[$module]}"
        local title deps
        IFS='|' read -r title _ deps <<< "$info"
        local status="[MISSING]"
        [[ -d "${IPAI_DIR}/${module}" ]] && status="[EXISTS]"
        printf "  %-30s %s  (%s)\n" "$module" "$status" "$title"
    done
}

main() {
    local mode="${1:-all}"

    case "$mode" in
        --list)
            list_modules
            ;;
        --check)
            check_existing
            ;;
        --module)
            if [[ -n "${2:-}" ]] && [[ -v "IPAI_MODULES[$2]" ]]; then
                scaffold_module "$2"
            else
                log_error "Unknown module: ${2:-<none>}"
                echo "Available modules:"
                list_modules
                exit 1
            fi
            ;;
        all|"")
            scaffold_all
            ;;
        *)
            echo "Usage: $0 [--list|--check|--module <name>]"
            exit 1
            ;;
    esac
}

main "$@"
