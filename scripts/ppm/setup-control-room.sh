#!/usr/bin/env bash
# Setup Control Room development environment
# Usage: ./scripts/ppm/setup-control-room.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
CONTROL_ROOM_DIR="$ROOT_DIR/apps/control-room"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Setting up Control Room development environment...${NC}"
echo ""

cd "$CONTROL_ROOM_DIR"

# Check Node.js version
echo -e "${YELLOW}▸ Checking Node.js version...${NC}"
NODE_VERSION=$(node --version 2>/dev/null || echo "not installed")
if [[ "$NODE_VERSION" == "not installed" ]]; then
    echo "  Node.js is not installed. Please install Node.js 20+."
    exit 1
fi
echo -e "  ${GREEN}✓${NC} Node.js $NODE_VERSION"

# Install dependencies
echo ""
echo -e "${YELLOW}▸ Installing npm dependencies...${NC}"
npm install
echo -e "  ${GREEN}✓${NC} Dependencies installed"

# Setup environment file
echo ""
echo -e "${YELLOW}▸ Setting up environment file...${NC}"
if [[ ! -f ".env.local" ]]; then
    cp .env.example .env.local
    echo -e "  ${GREEN}✓${NC} Created .env.local from .env.example"
    echo -e "  ${YELLOW}!${NC} Please update .env.local with your actual values"
else
    echo -e "  ${GREEN}✓${NC} .env.local already exists"
fi

# Run type check
echo ""
echo -e "${YELLOW}▸ Running TypeScript type check...${NC}"
npm run type-check || {
    echo -e "  ${YELLOW}!${NC} Type errors found. Please fix before running."
}

# Build check
echo ""
echo -e "${YELLOW}▸ Testing build...${NC}"
npm run build || {
    echo "  Build failed. Please check errors above."
    exit 1
}
echo -e "  ${GREEN}✓${NC} Build successful"

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Control Room setup complete!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo "  To start development server:"
echo "    cd apps/control-room && npm run dev"
echo ""
echo "  To run production build:"
echo "    cd apps/control-room && npm start"
echo ""
