#!/usr/bin/env bash
# =============================================================================
# IPAI Module Deprecation - Phase 3: Theme Architecture Cleanup
# =============================================================================
# This script consolidates the theme/design system modules.
# ipai_design_system_apps_sdk is the canonical SSOT.
#
# Strategy:
# 1. Mark duplicate theme modules as deprecated
# 2. Update dependencies to point to canonical module
# 3. Keep modules in repo but prevent loading
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
echo -e "${GREEN}IPAI Deprecation Phase 3${NC}"
echo -e "${GREEN}Theme Architecture Cleanup${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Canonical theme module (SSOT)
CANONICAL_THEME="ipai_design_system_apps_sdk"

# Theme modules to keep
KEEP_THEME_MODULES=(
    "ipai_design_system_apps_sdk"  # SSOT
    "ipai_theme_tbwa"              # Primary brand
    "ipai_theme_fluent2"           # Fluent 2 tokens
    "ipai_theme_copilot"           # Copilot styling
    "ipai_web_icons_fluent"        # Icon library
)

# Theme modules to deprecate (duplicates or superseded)
DEPRECATE_THEME_MODULES=(
    "ipai_platform_theme"          # Superseded by design_system_apps_sdk
    "ipai_design_system"           # Duplicate of apps_sdk
    "ipai_ui_brand_tokens"         # Duplicate token system
    "ipai_web_theme_tbwa"          # Duplicate of theme_tbwa
    "ipai_web_fluent2"             # Duplicate of theme_fluent2
    "ipai_copilot_ui"              # Merge into theme_copilot
    "ipai_chatgpt_sdk_theme"       # Niche, move to prototypes
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

    # Update manifest
    python3 << EOF
import re

manifest_path = "${manifest_path}"

with open(manifest_path, 'r') as f:
    content = f.read()

# Add DEPRECATED prefix to name
if 'DEPRECATED:' not in content:
    content = re.sub(
        r'"name":\s*"([^"]+)"',
        r'"name": "DEPRECATED: \1"',
        content
    )

# Update summary
content = re.sub(
    r'"summary":\s*"([^"]+)"',
    r'"summary": "DEPRECATED - Use ${CANONICAL_THEME} instead. Do not install."',
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

# Function to update dependencies in other modules
update_theme_dependencies() {
    echo -e "${YELLOW}Step 2: Update theme dependencies in other modules${NC}"
    echo ""

    # Deprecated themes to replace in depends
    local old_deps=(
        "ipai_platform_theme"
        "ipai_design_system"
        "ipai_ui_brand_tokens"
    )

    for manifest in ${IPAI_DIR}/*/\__manifest__.py; do
        local module_name=$(basename $(dirname "${manifest}"))

        # Skip the canonical module and deprecated modules
        if [[ " ${DEPRECATE_THEME_MODULES[*]} " =~ " ${module_name} " ]]; then
            continue
        fi

        for old_dep in "${old_deps[@]}"; do
            if grep -q "\"${old_dep}\"" "${manifest}" 2>/dev/null; then
                echo "  Updating ${module_name}: ${old_dep} -> ${CANONICAL_THEME}"
                sed -i "s/\"${old_dep}\"/\"${CANONICAL_THEME}\"/g" "${manifest}"
            fi
        done
    done
}

echo -e "${YELLOW}Step 1: Mark duplicate theme modules as deprecated${NC}"
echo ""

for module in "${DEPRECATE_THEME_MODULES[@]}"; do
    mark_deprecated "${module}" || true
done

echo ""
update_theme_dependencies

echo ""
echo -e "${YELLOW}Step 3: Verify canonical theme modules${NC}"
echo ""

echo "Canonical modules (should be installable):"
for module in "${KEEP_THEME_MODULES[@]}"; do
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
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Phase 3 Complete${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Summary:"
echo "  - Theme modules deprecated: ${#DEPRECATE_THEME_MODULES[@]}"
echo "  - Canonical theme: ${CANONICAL_THEME}"
echo ""
echo "Next steps:"
echo "  1. Review changes: git diff addons/ipai/*/\__manifest__.py"
echo "  2. Commit: git add -A && git commit -m 'chore(ipai): phase 3 - theme architecture cleanup'"
echo ""
