#!/usr/bin/env bash
# =============================================================================
# IPAI Module Deprecation - Phase 2: Consolidate Placeholder AI Modules
# =============================================================================
# This script marks placeholder AI modules as deprecated.
# These modules all have the pattern: single model with TODO comments.
#
# Strategy:
# 1. Mark manifests as installable: false
# 2. Add deprecation notice to summary
# 3. Modules remain in repo but won't load
# 4. Future: Remove completely after migration verified
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

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}IPAI Deprecation Phase 2${NC}"
echo -e "${GREEN}Mark Placeholder AI Modules Deprecated${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Placeholder AI modules from DEPRECATION_PLAN.md
# These all have: single model with TODO comments, no real business logic
PLACEHOLDER_AI_MODULES=(
    "ipai_ai_agent_builder"
    "ipai_ai_automations"
    "ipai_ai_fields"
    "ipai_ai_livechat"
    "ipai_ai_rag"
    "ipai_ai_tools"
)

# Business placeholder modules
PLACEHOLDER_BUSINESS_MODULES=(
    "ipai_equity"
    "ipai_esg"
    "ipai_esg_social"
    "ipai_planning_attendance"
    "ipai_project_templates"
    "ipai_whatsapp_connector"
    "ipai_finance_tax_return"
)

# Function to mark module as deprecated
mark_deprecated() {
    local module_name="$1"
    local manifest_path="${IPAI_DIR}/${module_name}/__manifest__.py"

    if [ ! -f "${manifest_path}" ]; then
        echo -e "    ${YELLOW}⚠ ${module_name}/__manifest__.py not found${NC}"
        return 1
    fi

    echo "  Marking deprecated: ${module_name}"

    # Check if already deprecated
    if grep -q '"installable": False' "${manifest_path}"; then
        echo -e "    ${YELLOW}⚠ Already marked as deprecated${NC}"
        return 0
    fi

    # Update manifest: set installable to False and add deprecation notice
    python3 << EOF
import re

manifest_path = "${manifest_path}"

with open(manifest_path, 'r') as f:
    content = f.read()

# Add DEPRECATED prefix to name if not already there
if 'DEPRECATED:' not in content:
    content = re.sub(
        r'"name":\s*"([^"]+)"',
        r'"name": "DEPRECATED: \1"',
        content
    )

# Update summary to include deprecation notice
content = re.sub(
    r'"summary":\s*"([^"]+)"',
    r'"summary": "DEPRECATED - Migrated to ipai_enterprise_bridge. Do not install."',
    content
)

# Set installable to False
if '"installable": True' in content:
    content = content.replace('"installable": True', '"installable": False')
elif '"installable":' not in content:
    # Add installable: False before the closing brace
    content = content.rstrip().rstrip('}')
    content += '    "installable": False,\n}'

with open(manifest_path, 'w') as f:
    f.write(content)

print("    Updated manifest")
EOF

    echo -e "    ${GREEN}✓ Marked as deprecated${NC}"
    return 0
}

echo -e "${YELLOW}Step 1: Mark AI placeholder modules as deprecated${NC}"
echo ""

for module in "${PLACEHOLDER_AI_MODULES[@]}"; do
    mark_deprecated "${module}" || true
done

echo ""
echo -e "${YELLOW}Step 2: Mark business placeholder modules as deprecated${NC}"
echo ""

for module in "${PLACEHOLDER_BUSINESS_MODULES[@]}"; do
    mark_deprecated "${module}" || true
done

echo ""
echo -e "${YELLOW}Step 3: Verify changes${NC}"
echo ""

# Count deprecated modules
deprecated_count=$(grep -l '"installable": False' ${IPAI_DIR}/ipai_*/\__manifest__.py 2>/dev/null | wc -l)
echo "  Total modules marked as installable: False: ${deprecated_count}"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Phase 2 Complete${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Summary:"
echo "  - AI modules deprecated: ${#PLACEHOLDER_AI_MODULES[@]}"
echo "  - Business modules deprecated: ${#PLACEHOLDER_BUSINESS_MODULES[@]}"
echo ""
echo "Next steps:"
echo "  1. Review changes: git diff addons/ipai/*/\__manifest__.py"
echo "  2. Verify no broken dependencies"
echo "  3. Commit: git add -A && git commit -m 'chore(ipai): phase 2 - deprecate placeholder modules'"
echo ""
echo "Note: Modules remain in repo but won't load (installable: False)."
echo "Complete removal will be done in a future cleanup pass."
echo ""
