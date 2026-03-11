#!/usr/bin/env bash
# Setup Notion Sync service development environment
# Usage: ./scripts/ppm/setup-notion-sync.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
NOTION_SYNC_DIR="$ROOT_DIR/services/notion-sync"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Setting up Notion Sync service development environment...${NC}"
echo ""

cd "$NOTION_SYNC_DIR"

# Check Python version
echo -e "${YELLOW}▸ Checking Python version...${NC}"
PYTHON_VERSION=$(python3 --version 2>/dev/null || echo "not installed")
if [[ "$PYTHON_VERSION" == "not installed" ]]; then
    echo "  Python is not installed. Please install Python 3.11+."
    exit 1
fi
echo -e "  ${GREEN}✓${NC} $PYTHON_VERSION"

# Create virtual environment
echo ""
echo -e "${YELLOW}▸ Creating virtual environment...${NC}"
if [[ ! -d ".venv" ]]; then
    python3 -m venv .venv
    echo -e "  ${GREEN}✓${NC} Virtual environment created"
else
    echo -e "  ${GREEN}✓${NC} Virtual environment already exists"
fi

# Activate and install
echo ""
echo -e "${YELLOW}▸ Installing dependencies...${NC}"
source .venv/bin/activate
pip install --upgrade pip
pip install -e ".[dev]"
echo -e "  ${GREEN}✓${NC} Dependencies installed"

# Setup environment file
echo ""
echo -e "${YELLOW}▸ Setting up environment file...${NC}"
if [[ ! -f ".env" ]]; then
    cat > .env << 'EOF'
# Notion Configuration
NOTION_TOKEN=secret_your_notion_integration_token
NOTION_PROGRAMS_DB=your_programs_database_id
NOTION_PROJECTS_DB=your_projects_database_id
NOTION_BUDGET_LINES_DB=your_budget_lines_database_id
NOTION_RISKS_DB=your_risks_database_id
NOTION_ACTIONS_DB=your_actions_database_id

# Databricks Configuration
DATABRICKS_HOST=https://your-workspace.azuredatabricks.net
DATABRICKS_TOKEN=your_databricks_token
DATABRICKS_CATALOG=ppm_catalog
DATABRICKS_SCHEMA_BRONZE=bronze
DATABRICKS_SCHEMA_SILVER=silver
DATABRICKS_SCHEMA_GOLD=gold
EOF
    echo -e "  ${GREEN}✓${NC} Created .env file"
    echo -e "  ${YELLOW}!${NC} Please update .env with your actual values"
else
    echo -e "  ${GREEN}✓${NC} .env file already exists"
fi

# Run tests
echo ""
echo -e "${YELLOW}▸ Running tests...${NC}"
pytest -v --tb=short || {
    echo -e "  ${YELLOW}!${NC} Some tests failed. Please check output above."
}

# Type check
echo ""
echo -e "${YELLOW}▸ Running type check...${NC}"
mypy notion_sync --ignore-missing-imports || {
    echo -e "  ${YELLOW}!${NC} Type errors found. Please review."
}

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Notion Sync setup complete!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo "  To activate virtual environment:"
echo "    source services/notion-sync/.venv/bin/activate"
echo ""
echo "  To run sync:"
echo "    notion-sync run --database programs"
echo ""
echo "  To run full sync:"
echo "    notion-sync run --all"
echo ""
