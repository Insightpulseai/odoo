#!/usr/bin/env bash
# Odoo 18 Test Runner
# Runs Odoo tests following official Odoo 18 testing patterns
# Docs: https://www.odoo.com/documentation/18.0/developer/reference/backend/testing.html

set -euo pipefail

# Configuration
DB_NAME="${DB_NAME:-odoo_test}"
ODOO_BIN="${ODOO_BIN:-odoo-bin}"
MODULES="${1:-}"
TAGS="${2:-}"
LOG_LEVEL="${LOG_LEVEL:-test}"

# Auto-detect odoo-bin if not in PATH
if ! command -v "$ODOO_BIN" &> /dev/null; then
  if [ -f "/tmp/odoo/scripts/odoo.sh" ]; then
    ODOO_BIN="/tmp/odoo/scripts/odoo.sh"
  elif [ -f "./scripts/odoo.sh" ]; then
    ODOO_BIN="./scripts/odoo.sh"
  else
    echo "Error: odoo-bin not found. Please set ODOO_BIN environment variable."
    exit 1
  fi
fi

# Color output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}========================================="
echo "Odoo 18 Test Runner"
echo "=========================================${NC}"

# If no modules specified, auto-detect from addons/
if [ -z "$MODULES" ]; then
  echo "Auto-detecting modules from addons/ directory..."
  MODULES=$(find addons -name "__manifest__.py" -exec dirname {} \; 2>/dev/null | xargs -I {} basename {} | tr '\n' ',' | sed 's/,$//' || echo "")

  if [ -z "$MODULES" ]; then
    echo -e "${YELLOW}Warning: No modules found in addons/ directory${NC}"
    echo "Usage: $0 [MODULES] [TAGS]"
    echo ""
    echo "Examples:"
    echo "  $0 ipai_expense"
    echo "  $0 ipai_expense /ipai_expense"
    echo "  $0 \"ipai_expense,ipai_equipment\" \"/ipai_\""
    exit 1
  fi
fi

# If no tags specified, use module-based tags
if [ -z "$TAGS" ]; then
  # Convert modules to tags (e.g., "ipai_expense" -> "/ipai_expense")
  TAGS=$(echo "$MODULES" | tr ',' '\n' | sed 's/^/\//' | tr '\n' ',' | sed 's/,$//')
fi

echo -e "${GREEN}Database:${NC} $DB_NAME"
echo -e "${GREEN}Modules:${NC} $MODULES"
echo -e "${GREEN}Tags:${NC} $TAGS"
echo -e "${GREEN}Log level:${NC} $LOG_LEVEL"
echo -e "${BLUE}=========================================${NC}"
echo ""

# Build test command following Odoo 18 patterns
TEST_CMD="$ODOO_BIN \
  -d $DB_NAME \
  -i $MODULES \
  --test-enable \
  --stop-after-init \
  --log-level=$LOG_LEVEL"

# Add test tags if specified
if [ -n "$TAGS" ]; then
  TEST_CMD="$TEST_CMD --test-tags=$TAGS"
fi

# Run tests
echo -e "${GREEN}Running Odoo 18 tests...${NC}"
echo ""

eval $TEST_CMD

EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
  echo -e "${GREEN}========================================="
  echo "✅ All tests passed!"
  echo "=========================================${NC}"
else
  echo -e "${YELLOW}========================================="
  echo "❌ Tests failed with exit code: $EXIT_CODE"
  echo "=========================================${NC}"
fi

exit $EXIT_CODE
