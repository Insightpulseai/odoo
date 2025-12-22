#!/bin/bash
# =============================================================================
# Enterprise Module Denylist Check
# =============================================================================
# This script scans the codebase for forbidden Odoo Enterprise modules.
# It enforces the CE-only policy for InsightPulse ERP.
#
# Usage: ./scripts/check-enterprise-modules.sh
# Exit codes:
#   0 - No enterprise modules found
#   1 - Enterprise modules detected (policy violation)
# =============================================================================

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Forbidden Enterprise modules list
FORBIDDEN_MODULES=(
    "web_enterprise"
    "iap"
    "iap_mail"
    "iap_sms"
    "iap_crm"
    "iap_extract"
    "industry_fsm"
    "industry_fsm_sale"
    "industry_fsm_stock"
    "planning"
    "planning_hr"
    "web_studio"
    "web_studio_approval"
    "sign"
    "sign_templates"
    "helpdesk"
    "helpdesk_timesheet"
    "knowledge"
    "knowledge_article"
    "quality_control"
    "quality_control_picking_batch"
    "account_accountant"
    "account_reports"
    "mrp_workorder"
    "mrp_workorder_iot"
    "mrp_plm"
    "mrp_mps"
    "social"
    "social_media"
    "marketing_automation"
    "marketing_automation_sms"
    "appointment"
    "appointment_hr"
    "voip"
    "voip_crm"
    "stock_barcode"
    "stock_barcode_picking"
    "documents"
    "documents_project"
    "documents_spreadsheet"
    "spreadsheet_edition"
    "sale_subscription"
    "sale_subscription_external_tax"
    "fleet_vehicle_request"
    "hr_appraisal"
    "hr_appraisal_survey"
    "hr_payroll"
    "hr_payroll_holidays"
    "l10n_*_reports"
    "website_helpdesk"
    "website_appointment"
)

VIOLATIONS_FOUND=0
VIOLATIONS_LOG=""

echo -e "${YELLOW}Scanning for Enterprise modules...${NC}"
echo "========================================"

# Get repository root
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$REPO_ROOT"

# Directories to scan
SCAN_DIRS=("addons" "oca" "src/addons" "external-src" "vendor/oca")

# Function to check for module directories
check_module_directories() {
    local dir="$1"
    if [ ! -d "$dir" ]; then
        return
    fi

    for module in "${FORBIDDEN_MODULES[@]}"; do
        # Handle glob patterns
        if [[ "$module" == *"*"* ]]; then
            matches=$(find "$dir" -maxdepth 2 -type d -name "$module" 2>/dev/null || true)
        else
            matches=$(find "$dir" -maxdepth 2 -type d -name "$module" 2>/dev/null || true)
        fi

        if [ -n "$matches" ]; then
            while IFS= read -r match; do
                if [ -n "$match" ]; then
                    VIOLATIONS_FOUND=$((VIOLATIONS_FOUND + 1))
                    VIOLATIONS_LOG="${VIOLATIONS_LOG}\n  - Found forbidden module directory: $match"
                fi
            done <<< "$matches"
        fi
    done
}

# Function to check for Enterprise imports in Python files
check_enterprise_imports() {
    local dir="$1"
    if [ ! -d "$dir" ]; then
        return
    fi

    # Check for direct Enterprise module imports
    matches=$(grep -rn "from odoo\.addons\.\(web_enterprise\|iap\|planning\|helpdesk\|sign\|knowledge\|documents\)" "$dir" 2>/dev/null || true)
    if [ -n "$matches" ]; then
        while IFS= read -r match; do
            if [ -n "$match" ]; then
                VIOLATIONS_FOUND=$((VIOLATIONS_FOUND + 1))
                VIOLATIONS_LOG="${VIOLATIONS_LOG}\n  - Enterprise import found: $match"
            fi
        done <<< "$matches"
    fi

    # Check for Enterprise module in depends lists
    matches=$(grep -rn "'depends'.*:" "$dir"/*/__manifest__.py 2>/dev/null | grep -i "enterprise\|iap\|planning\|helpdesk\|sign\|knowledge\|documents" || true)
    if [ -n "$matches" ]; then
        while IFS= read -r match; do
            if [ -n "$match" ]; then
                VIOLATIONS_FOUND=$((VIOLATIONS_FOUND + 1))
                VIOLATIONS_LOG="${VIOLATIONS_LOG}\n  - Enterprise dependency in manifest: $match"
            fi
        done <<< "$matches"
    fi
}

# Function to check for IAP/Enterprise URLs
check_enterprise_urls() {
    local dir="$1"
    if [ ! -d "$dir" ]; then
        return
    fi

    # Check for iap.odoo.com or enterprise.odoo.com URLs in Python/XML files only
    # Exclude CSS files which contain selectors meant to HIDE these elements (e.g., ipai_ce_cleaner)
    # Exclude comments, documentation, and markdown files
    matches=$(grep -rn --include="*.py" --include="*.xml" "iap\.odoo\.com\|enterprise\.odoo\.com" "$dir" 2>/dev/null | \
        grep -v "^#\|# " | grep -v "<!--" | grep -v "_cleaner" || true)
    if [ -n "$matches" ]; then
        while IFS= read -r match; do
            if [ -n "$match" ]; then
                VIOLATIONS_FOUND=$((VIOLATIONS_FOUND + 1))
                VIOLATIONS_LOG="${VIOLATIONS_LOG}\n  - IAP/Enterprise URL found: $match"
            fi
        done <<< "$matches"
    fi
}

# Scan all directories
for dir in "${SCAN_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "Scanning: $dir"
        check_module_directories "$dir"
        check_enterprise_imports "$dir"
        check_enterprise_urls "$dir"
    fi
done

# Report results
echo "========================================"
if [ $VIOLATIONS_FOUND -eq 0 ]; then
    echo -e "${GREEN}No Enterprise modules detected.${NC}"
    echo "CE-only policy compliance: PASSED"
    exit 0
else
    echo -e "${RED}ERROR: Found $VIOLATIONS_FOUND Enterprise module violations!${NC}"
    echo -e "${RED}Violations:${NC}"
    echo -e "$VIOLATIONS_LOG"
    echo ""
    echo -e "${RED}CE-only policy compliance: FAILED${NC}"
    echo ""
    echo "Please remove or replace these modules with OCA equivalents."
    echo "Refer to docs/ODOO18_ENTERPRISE_TO_CE_OCA_MAPPING.md for alternatives."
    exit 1
fi
