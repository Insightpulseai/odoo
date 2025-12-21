#!/usr/bin/env bash
# Verify all Notion x Finance PPM components
# Usage: ./scripts/ppm/verify-all.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       Notion x Finance PPM - Full Verification             ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

ERRORS=0
WARNINGS=0

# Function to check a component
check_component() {
    local name=$1
    local path=$2
    local required_files=("${@:3}")

    echo -e "${YELLOW}▸ Checking $name...${NC}"

    if [[ ! -d "$ROOT_DIR/$path" ]]; then
        echo -e "  ${RED}✗ Directory not found: $path${NC}"
        ERRORS=$((ERRORS + 1))
        return
    fi

    for file in "${required_files[@]}"; do
        if [[ -f "$ROOT_DIR/$path/$file" ]]; then
            echo -e "  ${GREEN}✓${NC} $file"
        else
            echo -e "  ${RED}✗ Missing: $file${NC}"
            ERRORS=$((ERRORS + 1))
        fi
    done
    echo ""
}

# ============================================================================
# 1. Spec Bundle
# ============================================================================
echo -e "${BLUE}━━━ 1. Spec Bundle ━━━${NC}"
check_component "Spec Bundle" "spec/notion-finance-ppm-control-room" \
    "constitution.md" "prd.md" "plan.md" "tasks.md"

# ============================================================================
# 2. Control Room App
# ============================================================================
echo -e "${BLUE}━━━ 2. Control Room App ━━━${NC}"
check_component "Control Room" "apps/control-room" \
    "package.json" "next.config.js" "tailwind.config.js" "tsconfig.json" ".env.example"

check_component "Control Room Types" "apps/control-room/src/types" \
    "api.ts" "models.ts"

check_component "Control Room Lib" "apps/control-room/src/lib" \
    "config.ts" "databricks.ts" "notion.ts" "schemas.ts"

check_component "Control Room API Routes" "apps/control-room/src/app/api" \
    "health/route.ts" "kpis/route.ts" "jobs/route.ts" "dq/issues/route.ts"

check_component "Control Room Pages" "apps/control-room/src/app" \
    "layout.tsx" "page.tsx" "overview/page.tsx" "pipelines/page.tsx" "data-quality/page.tsx"

# ============================================================================
# 3. Notion Sync Service
# ============================================================================
echo -e "${BLUE}━━━ 3. Notion Sync Service ━━━${NC}"
check_component "Notion Sync" "services/notion-sync" \
    "pyproject.toml" "config/notion_mapping.yaml"

check_component "Notion Sync Package" "services/notion-sync/notion_sync" \
    "__init__.py" "config.py" "models.py" "client.py" "transform.py" "databricks_writer.py" "sync.py" "main.py"

check_component "Notion Sync Tests" "services/notion-sync/tests" \
    "conftest.py" "test_transform.py"

# ============================================================================
# 4. Databricks DAB Bundle
# ============================================================================
echo -e "${BLUE}━━━ 4. Databricks DAB Bundle ━━━${NC}"
check_component "DAB Bundle" "infra/databricks" \
    "databricks.yml" "resources/jobs.yml" "resources/schemas.yml"

check_component "Bronze Notebooks" "infra/databricks/notebooks/bronze" \
    "ingest_notion.py" "ingest_azure_rg.py"

check_component "Silver Notebooks" "infra/databricks/notebooks/silver" \
    "transform_notion.py"

check_component "Gold Notebooks" "infra/databricks/notebooks/gold" \
    "budget_vs_actual.py" "forecast.py" "risk_summary.py" "projects_summary.py" "dq_checks.py" "control_room_status.py"

# ============================================================================
# 5. Azure Infrastructure (Reference)
# ============================================================================
echo -e "${BLUE}━━━ 5. Azure Infrastructure (Reference) ━━━${NC}"
check_component "Azure Bicep" "infra/azure" \
    "main.bicep" "parameters/dev.parameters.json" "parameters/prod.parameters.json"

check_component "Azure Modules" "infra/azure/modules" \
    "keyvault.bicep" "storage.bicep" "databricks.bicep" "appservice.bicep"

# ============================================================================
# 6. Continue Rules
# ============================================================================
echo -e "${BLUE}━━━ 6. Continue Rules ━━━${NC}"
check_component "Continue Rules" ".continue" \
    "config.json" "rules/notion-ppm.yaml" "rules/medallion-architecture.yaml"

# ============================================================================
# 7. GitHub Actions
# ============================================================================
echo -e "${BLUE}━━━ 7. GitHub Actions ━━━${NC}"
check_component "CI Workflows" ".github/workflows" \
    "control-room-ci.yml" "notion-sync-ci.yml" "databricks-dab-ci.yml" "infra-validate.yml" "spec-validate.yml"

# ============================================================================
# Summary
# ============================================================================
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                     Verification Summary                    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

if [[ $ERRORS -eq 0 ]]; then
    echo -e "${GREEN}✓ All components verified successfully!${NC}"
    echo ""
    exit 0
else
    echo -e "${RED}✗ Verification failed with $ERRORS errors${NC}"
    echo ""
    exit 1
fi
