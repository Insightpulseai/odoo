#!/usr/bin/env bash
# =============================================================================
# IPAI Module Deprecation - Phase 1: Archive Deprecated & Prototype Modules
# =============================================================================
# This script archives modules that are:
# 1. Already marked as deprecated (installable: false)
# 2. In Alpha/prototype state
# 3. Incomplete scaffolds
#
# Safe to run: No data migration needed (these modules have no production data)
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
PROTOTYPE_DIR="${REPO_ROOT}/prototypes"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}IPAI Deprecation Phase 1${NC}"
echo -e "${GREEN}Archive Deprecated & Prototype Modules${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check we're in the right place
if [ ! -d "${IPAI_DIR}" ]; then
    echo -e "${RED}ERROR: ${IPAI_DIR} not found${NC}"
    exit 1
fi

# Create archive directories
mkdir -p "${ARCHIVE_DIR}"
mkdir -p "${PROTOTYPE_DIR}"

echo -e "${YELLOW}Step 1: Archive explicitly deprecated modules${NC}"
echo ""

# Already deprecated modules
DEPRECATED_MODULES=(
    "ipai_theme_tbwa_backend"  # Manifest says: "THIS MODULE IS DEPRECATED"
)

for module in "${DEPRECATED_MODULES[@]}"; do
    if [ -d "${IPAI_DIR}/${module}" ]; then
        echo "  Archiving: ${module}"
        mv "${IPAI_DIR}/${module}" "${ARCHIVE_DIR}/"
        echo -e "    ${GREEN}✓ Moved to archive/deprecated/${module}${NC}"
    else
        echo -e "    ${YELLOW}⚠ ${module} not found (already archived?)${NC}"
    fi
done

echo ""
echo -e "${YELLOW}Step 2: Move prototype/alpha modules${NC}"
echo ""

# Prototype/Alpha modules
PROTOTYPE_MODULES=(
    "ipai_fluent_web_365_copilot"  # development_status: Alpha
    "ipai_aiux_chat"               # Scaffold module
    "ipai_theme_aiux"              # Scaffold module
)

for module in "${PROTOTYPE_MODULES[@]}"; do
    if [ -d "${IPAI_DIR}/${module}" ]; then
        echo "  Moving to prototypes: ${module}"
        mv "${IPAI_DIR}/${module}" "${PROTOTYPE_DIR}/"
        echo -e "    ${GREEN}✓ Moved to prototypes/${module}${NC}"
    else
        echo -e "    ${YELLOW}⚠ ${module} not found (already moved?)${NC}"
    fi
done

echo ""
echo -e "${YELLOW}Step 3: Create archive README${NC}"

cat > "${ARCHIVE_DIR}/README.md" << 'EOF'
# Archived Deprecated Modules

These modules have been deprecated and archived as part of the EE parity consolidation.

## Why Archived

- `ipai_theme_tbwa_backend`: Replaced by `ipai_theme_tbwa`

## Data Migration

No data migration needed - these modules had no production data.

## Restoration

If you need to restore a module:

```bash
git mv archive/deprecated/<module_name> addons/ipai/
```

Then update the manifest to set `installable: True`.

---

*Archived: 2026-01-28*
*Deprecation Plan: docs/DEPRECATION_PLAN.md*
EOF

cat > "${PROTOTYPE_DIR}/README.md" << 'EOF'
# Prototype Modules

These modules are in development/alpha state and not ready for production.

## Modules

- `ipai_fluent_web_365_copilot`: SAP Joule / Microsoft 365 Copilot-style AI assistant (Alpha)
- `ipai_aiux_chat`: AI chat widget scaffold
- `ipai_theme_aiux`: AI UX theme scaffold

## Usage

These modules are NOT loaded in production images. To develop on them:

```bash
# Add to addons path during development
docker run ... -v $(pwd)/prototypes:/mnt/prototypes \
  -e ODOO_ADDONS_PATH=/mnt/addons/ipai,/mnt/addons/oca,/mnt/prototypes
```

## Promotion to Production

When a prototype is ready:

1. Move to `addons/ipai/`
2. Update manifest: remove `development_status: Alpha`
3. Add tests
4. Update dependencies

---

*Created: 2026-01-28*
*Deprecation Plan: docs/DEPRECATION_PLAN.md*
EOF

echo -e "    ${GREEN}✓ Created README files${NC}"

echo ""
echo -e "${YELLOW}Step 4: Update Dockerfile.ce19 to exclude archived modules${NC}"

# No changes needed - Dockerfile copies addons/ipai/ which no longer includes these

echo -e "    ${GREEN}✓ No changes needed (modules already excluded)${NC}"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Phase 1 Complete${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Summary:"
echo "  - Archived: ${#DEPRECATED_MODULES[@]} deprecated module(s)"
echo "  - Prototyped: ${#PROTOTYPE_MODULES[@]} prototype module(s)"
echo ""
echo "Next steps:"
echo "  1. Review changes: git status"
echo "  2. Commit: git add -A && git commit -m 'chore(ipai): phase 1 - archive deprecated and prototype modules'"
echo "  3. Push: git push origin <branch>"
echo ""
echo "To verify no broken dependencies:"
echo "  grep -r 'ipai_theme_tbwa_backend\\|ipai_fluent_web_365_copilot\\|ipai_aiux_chat\\|ipai_theme_aiux' addons/ipai/*/__manifest__.py"
echo ""
