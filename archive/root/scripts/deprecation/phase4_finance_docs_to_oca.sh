#!/usr/bin/env bash
# =============================================================================
# IPAI Module Deprecation - Phase 4: Finance/Document Migration to OCA
# =============================================================================
# This script marks placeholder finance/document modules as deprecated
# in favor of OCA alternatives + ipai_enterprise_bridge.
#
# Strategy:
# 1. Mark placeholder modules as deprecated
# 2. Merge ipai_helpdesk_refund into ipai_helpdesk
# 3. Point to OCA alternatives where available
# =============================================================================

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Paths
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
IPAI_DIR="${REPO_ROOT}/addons/ipai"
ARCHIVE_DIR="${REPO_ROOT}/archive/deprecated"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}IPAI Deprecation Phase 4${NC}"
echo -e "${GREEN}Finance/Document Migration to OCA${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Modules to deprecate (placeholder finance/document modules)
DEPRECATE_MODULES=(
    "ipai_documents_ai"      # Replace with OCA dms + AI bridge
    "ipai_sign"              # Replace with OCA sign
    "ipai_helpdesk_refund"   # Merge into ipai_helpdesk
)

# OCA alternatives mapping
declare -A OCA_ALTERNATIVES=(
    ["ipai_documents_ai"]="dms (OCA) + ipai_enterprise_bridge"
    ["ipai_sign"]="sign (OCA)"
    ["ipai_helpdesk_refund"]="ipai_helpdesk (merge)"
)

# Function to mark module as deprecated
mark_deprecated() {
    local module_name="$1"
    local replacement="$2"
    local manifest_path="${IPAI_DIR}/${module_name}/__manifest__.py"

    if [ ! -f "${manifest_path}" ]; then
        echo -e "    ${YELLOW}⚠ ${module_name}/__manifest__.py not found${NC}"
        return 1
    fi

    echo "  Marking deprecated: ${module_name}"
    echo "    Replacement: ${replacement}"

    # Check if already deprecated
    if grep -q '"installable": False' "${manifest_path}"; then
        echo -e "    ${YELLOW}⚠ Already marked as deprecated${NC}"
        return 0
    fi

    # Update manifest
    python3 << EOF
import re

manifest_path = "${manifest_path}"
replacement = "${replacement}"

with open(manifest_path, 'r') as f:
    content = f.read()

# Add DEPRECATED prefix to name
if 'DEPRECATED:' not in content:
    content = re.sub(
        r'"name":\s*"([^"]+)"',
        r'"name": "DEPRECATED: \1"',
        content
    )

# Update summary with replacement info
summary_text = f"DEPRECATED - Use {replacement} instead. Do not install."
content = re.sub(
    r'"summary":\s*"([^"]+)"',
    f'"summary": "{summary_text}"',
    content
)

# Set installable to False
if '"installable": True' in content:
    content = content.replace('"installable": True', '"installable": False')
elif '"installable":' not in content:
    content = content.rstrip().rstrip('}')
    content += '    "installable": False,\n}'

with open(manifest_path, 'w') as f:
    f.write(content)

print("    Updated manifest")
EOF

    echo -e "    ${GREEN}✓ Marked as deprecated${NC}"
    return 0
}

echo -e "${YELLOW}Step 1: Mark finance/document placeholder modules as deprecated${NC}"
echo ""

for module in "${DEPRECATE_MODULES[@]}"; do
    replacement="${OCA_ALTERNATIVES[$module]:-ipai_enterprise_bridge}"
    mark_deprecated "${module}" "${replacement}" || true
done

echo ""
echo -e "${YELLOW}Step 2: Verify canonical finance modules${NC}"
echo ""

# Canonical finance modules that should remain
CANONICAL_FINANCE=(
    "ipai_finance_ppm"
    "ipai_finance_workflow"
    "ipai_expense_ocr"
    "ipai_helpdesk"
    "ipai_hr_payroll_ph"
)

echo "Canonical modules (should be installable):"
for module in "${CANONICAL_FINANCE[@]}"; do
    manifest="${IPAI_DIR}/${module}/__manifest__.py"
    if [ -f "${manifest}" ]; then
        if grep -q '"installable": False' "${manifest}"; then
            echo -e "  ${RED}✗ ${module} is marked as not installable!${NC}"
        else
            echo -e "  ${GREEN}✓ ${module}${NC}"
        fi
    else
        echo -e "  ${YELLOW}⚠ ${module} not found${NC}"
    fi
done

echo ""
echo -e "${YELLOW}Step 3: OCA module verification${NC}"
echo ""

echo "OCA modules needed for finance/document parity:"
echo "  - dms (OCA) - Document management"
echo "  - sign (OCA) - Digital signatures"
echo "  - account_financial_report (OCA) - Financial reports"
echo "  - account_reconcile_oca (OCA) - Bank reconciliation"
echo ""
echo "Verify these are in vendor/oca.lock.ce19.json"

if [ -f "${REPO_ROOT}/vendor/oca.lock.ce19.json" ]; then
    echo -e "  ${GREEN}✓ oca.lock.ce19.json exists${NC}"
else
    echo -e "  ${YELLOW}⚠ oca.lock.ce19.json not found${NC}"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Phase 4 Complete${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Summary:"
echo "  - Finance/document modules deprecated: ${#DEPRECATE_MODULES[@]}"
echo "  - OCA alternatives documented"
echo ""
echo "Next steps:"
echo "  1. Review changes: git diff addons/ipai/*/\__manifest__.py"
echo "  2. Verify OCA modules in oca.lock.ce19.json"
echo "  3. Commit: git add -A && git commit -m 'chore(ipai): phase 4 - finance/docs OCA migration'"
echo ""
echo "Note: Data migration from deprecated modules should be handled"
echo "via ipai_enterprise_bridge post_init_hook if any production data exists."
echo ""
