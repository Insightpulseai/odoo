#!/usr/bin/env bash
# Deploy Databricks DAB bundle to specified environment
# Usage: ./scripts/ppm/deploy-databricks.sh [dev|staging|prod]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
DAB_DIR="$ROOT_DIR/infra/databricks"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Default environment
ENV="${1:-dev}"

# Validate environment
case "$ENV" in
    dev|staging|prod)
        ;;
    *)
        echo -e "${RED}Invalid environment: $ENV${NC}"
        echo "Usage: $0 [dev|staging|prod]"
        exit 1
        ;;
esac

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       Databricks DAB Bundle Deployment                     ║${NC}"
echo -e "${BLUE}║       Environment: ${YELLOW}$ENV${BLUE}                                     ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

cd "$DAB_DIR"

# Check Databricks CLI
echo -e "${YELLOW}▸ Checking Databricks CLI...${NC}"
if ! command -v databricks &> /dev/null; then
    echo -e "  ${RED}✗ Databricks CLI not found${NC}"
    echo "  Install with: pip install databricks-cli"
    exit 1
fi
echo -e "  ${GREEN}✓${NC} Databricks CLI found"

# Check authentication
echo ""
echo -e "${YELLOW}▸ Checking authentication...${NC}"
if [[ -z "$DATABRICKS_HOST" ]] || [[ -z "$DATABRICKS_TOKEN" ]]; then
    echo -e "  ${RED}✗ DATABRICKS_HOST and DATABRICKS_TOKEN must be set${NC}"
    exit 1
fi
echo -e "  ${GREEN}✓${NC} Authentication configured"

# Validate bundle
echo ""
echo -e "${YELLOW}▸ Validating bundle...${NC}"
databricks bundle validate -t "$ENV"
echo -e "  ${GREEN}✓${NC} Bundle validation passed"

# Deploy
echo ""
echo -e "${YELLOW}▸ Deploying to $ENV...${NC}"
databricks bundle deploy -t "$ENV"
echo -e "  ${GREEN}✓${NC} Deployment complete"

# Show deployed resources
echo ""
echo -e "${YELLOW}▸ Deployed Jobs:${NC}"
databricks bundle summary -t "$ENV" 2>/dev/null || true

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Deployment to $ENV complete!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo "  To run a job manually:"
echo "    databricks bundle run notion_sync_bronze_job -t $ENV"
echo ""
