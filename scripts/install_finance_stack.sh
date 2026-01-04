#!/bin/bash
#
# install_finance_stack.sh
# ========================
# Deployment script for IPAI Document Digitalization & Finance Kanban Stack
#
# This script installs and updates the following modules:
# 1. ipai_finance_ppm - Finance Kanban Board with toggle features
# 2. ipai_expense - PH-focused expense workflows
# 3. ipai_ocr_expense - AI/OCR receipt digitization
# 4. ipai_finance_close_automation - Month-end close with alerts
# 5. ipai_ask_ai - Finance RAG Engine
# 6. ipai_ask_ai_chatter - Chatter AI integration
#
# Usage:
#   ./scripts/install_finance_stack.sh [options]
#
# Options:
#   --database, -d    Database name (default: odoo)
#   --update, -u      Update existing modules instead of install
#   --container, -c   Docker container name (default: odoo-web-1)
#   --help, -h        Show this help message
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
DATABASE="odoo"
CONTAINER="odoo-web-1"
UPDATE_MODE=false

# Core Finance Stack Modules (in dependency order)
CORE_MODULES=(
    "ipai_finance_close_seed"
    "ipai_finance_ppm"
    "ipai_expense"
    "ipai_finance_close_automation"
)

# AI Stack Modules
AI_MODULES=(
    "ipai_ask_ai"
    "ipai_ask_ai_chatter"
    "ipai_ocr_expense"
)

# All modules combined
ALL_MODULES=("${CORE_MODULES[@]}" "${AI_MODULES[@]}")

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--database)
            DATABASE="$2"
            shift 2
            ;;
        -c|--container)
            CONTAINER="$2"
            shift 2
            ;;
        -u|--update)
            UPDATE_MODE=true
            shift
            ;;
        -h|--help)
            echo "IPAI Finance Stack Installer"
            echo ""
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  -d, --database    Database name (default: odoo)"
            echo "  -c, --container   Docker container name (default: odoo-web-1)"
            echo "  -u, --update      Update existing modules instead of install"
            echo "  -h, --help        Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}=======================================${NC}"
echo -e "${BLUE}  IPAI Finance Stack Installer${NC}"
echo -e "${BLUE}=======================================${NC}"
echo ""
echo -e "Database: ${GREEN}$DATABASE${NC}"
echo -e "Container: ${GREEN}$CONTAINER${NC}"
echo -e "Mode: ${GREEN}$([ "$UPDATE_MODE" = true ] && echo "Update" || echo "Install")${NC}"
echo ""

# Function to check if container is running
check_container() {
    if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
        echo -e "${RED}Error: Container '$CONTAINER' is not running${NC}"
        echo "Please start the Odoo stack first: docker compose up -d"
        exit 1
    fi
}

# Function to install/update a single module
install_module() {
    local module=$1
    local action=$([ "$UPDATE_MODE" = true ] && echo "-u" || echo "-i")

    echo -e "${YELLOW}  → Processing: $module${NC}"

    docker exec -it "$CONTAINER" odoo \
        --database="$DATABASE" \
        "$action" "$module" \
        --stop-after-init \
        --no-http \
        2>&1 | grep -E "(INFO|WARNING|ERROR)" || true

    echo -e "${GREEN}  ✓ $module completed${NC}"
}

# Function to install all modules
install_all() {
    local modules_csv=$(IFS=,; echo "${ALL_MODULES[*]}")
    local action=$([ "$UPDATE_MODE" = true ] && echo "-u" || echo "-i")

    echo -e "${YELLOW}Installing all modules...${NC}"

    docker exec -it "$CONTAINER" odoo \
        --database="$DATABASE" \
        "$action" "$modules_csv" \
        --stop-after-init \
        --no-http

    echo -e "${GREEN}✓ All modules installed successfully${NC}"
}

# Main execution
echo -e "${YELLOW}Checking prerequisites...${NC}"
check_container
echo -e "${GREEN}✓ Container is running${NC}"
echo ""

echo -e "${BLUE}Installing Core Finance Modules...${NC}"
for module in "${CORE_MODULES[@]}"; do
    install_module "$module"
done
echo ""

echo -e "${BLUE}Installing AI Stack Modules...${NC}"
for module in "${AI_MODULES[@]}"; do
    install_module "$module"
done
echo ""

echo -e "${GREEN}=======================================${NC}"
echo -e "${GREEN}  Installation Complete!${NC}"
echo -e "${GREEN}=======================================${NC}"
echo ""
echo -e "Installed modules:"
for module in "${ALL_MODULES[@]}"; do
    echo -e "  ${GREEN}✓${NC} $module"
done
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo "1. Restart Odoo: docker compose restart odoo"
echo "2. Access Finance Kanban: Finance PPM → Finance Kanban"
echo "3. Configure OCR: Settings → Technical → Parameters → ipai_ocr_expense.*"
echo "4. Configure Ask AI: Settings → Technical → Parameters → ipai_ask_ai.*"
echo ""
echo -e "${YELLOW}Configuration Options:${NC}"
echo ""
echo "OCR Provider (ipai_ocr_expense.provider):"
echo "  - mock: Testing (no external API)"
echo "  - azure: Azure Form Recognizer"
echo "  - google: Google Cloud Vision"
echo ""
echo "AI Provider (ipai_ask_ai.provider):"
echo "  - mock: Testing (no external API)"
echo "  - openai: OpenAI GPT-4"
echo "  - azure: Azure OpenAI"
echo ""
