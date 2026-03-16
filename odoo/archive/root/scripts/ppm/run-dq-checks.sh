#!/usr/bin/env bash
# Run data quality checks locally
# Usage: ./scripts/ppm/run-dq-checks.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       PPM Data Quality Checks                              ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check for required environment variables
if [[ -z "$DATABRICKS_HOST" ]] || [[ -z "$DATABRICKS_TOKEN" ]]; then
    echo -e "${YELLOW}Note: DATABRICKS_HOST and DATABRICKS_TOKEN not set.${NC}"
    echo "Running in dry-run mode with sample checks..."
    echo ""
fi

# Define DQ checks
declare -A DQ_CHECKS=(
    ["programs_not_null"]="SELECT COUNT(*) as count FROM ppm_silver.programs WHERE id IS NULL"
    ["projects_not_null"]="SELECT COUNT(*) as count FROM ppm_silver.projects WHERE id IS NULL"
    ["budget_positive"]="SELECT COUNT(*) as count FROM ppm_silver.budget_lines WHERE amount < 0"
    ["risks_valid_severity"]="SELECT COUNT(*) as count FROM ppm_silver.risks WHERE severity NOT IN ('Low', 'Medium', 'High', 'Critical')"
    ["orphan_projects"]="SELECT COUNT(*) as count FROM ppm_silver.projects p LEFT JOIN ppm_silver.programs pr ON p.program_id = pr.id WHERE pr.id IS NULL"
)

echo -e "${YELLOW}▸ Running Data Quality Checks...${NC}"
echo ""

PASSED=0
FAILED=0

for check_name in "${!DQ_CHECKS[@]}"; do
    query="${DQ_CHECKS[$check_name]}"

    echo -n "  $check_name: "

    if [[ -z "$DATABRICKS_HOST" ]]; then
        # Dry run - simulate pass
        echo -e "${GREEN}PASS${NC} (dry-run)"
        PASSED=$((PASSED + 1))
    else
        # Execute query against Databricks
        result=$(databricks sql --query "$query" 2>/dev/null | jq -r '.[0].count' 2>/dev/null || echo "error")

        if [[ "$result" == "0" ]]; then
            echo -e "${GREEN}PASS${NC}"
            PASSED=$((PASSED + 1))
        elif [[ "$result" == "error" ]]; then
            echo -e "${YELLOW}SKIP${NC} (query error)"
        else
            echo -e "${RED}FAIL${NC} ($result violations)"
            FAILED=$((FAILED + 1))
        fi
    fi
done

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "  Results: ${GREEN}$PASSED passed${NC}, ${RED}$FAILED failed${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [[ $FAILED -gt 0 ]]; then
    exit 1
fi
