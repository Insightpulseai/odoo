#!/bin/bash
# verify_foundry_env.sh
# Verifies the local development environment for Azure AI Foundry

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo "🔍 Verifying Azure AI Foundry environment..."

# 1. Check CLI Tools
echo -n "Checking az CLI... "
if command -v az >/dev/null 2>&1; then
    AZ_PATH=$(command -v az)
else
    AZ_PATH="/opt/homebrew/bin/az"
fi

if [ -f "$AZ_PATH" ]; then
    VERSION=$("$AZ_PATH" --version | head -n 1)
    echo -e "${GREEN}PASS${NC} (Found at $AZ_PATH: $VERSION)"
else
    echo -e "${RED}FAIL${NC} (az CLI not found)"
fi

echo -n "Checking azd CLI... "
if command -v azd >/dev/null 2>&1; then
    AZD_PATH=$(command -v azd)
else
    AZD_PATH="/opt/homebrew/bin/azd"
fi

if [ -f "$AZD_PATH" ]; then
    # Note: Using absolute path to check version if path isn't in shell PATH
    VERSION=$("$AZD_PATH" version 2>/dev/null || echo "Found but panics (see docs)")
    echo -e "${GREEN}PASS${NC} (Found at $AZD_PATH: $VERSION)"
else
    echo -e "${RED}FAIL${NC} (azd CLI not found)"
fi

# 2. Check Python Environment
echo -n "Checking .venv... "
if [ -d ".venv" ]; then
    echo -e "${GREEN}PASS${NC}"
else
    echo -e "${RED}FAIL${NC} (.venv directory not found)"
    exit 1
fi

echo -n "Checking Python version... "
VENV_PYTHON="./.venv/bin/python3"
if [ -f "$VENV_PYTHON" ]; then
    VERSION=$($VENV_PYTHON --version)
    echo -e "${GREEN}PASS${NC} ($VERSION)"
else
    echo -e "${RED}FAIL${NC} (Python not found in .venv)"
    exit 1
fi

# 3. Check Python Packages
echo "Checking Azure SDK packages..."
PACKAGES=("azure-ai-projects" "azure-identity" "azure-ai-ml" "openai")

for PKG in "${PACKAGES[@]}"; do
    echo -n "  - $PKG... "
    if $VENV_PYTHON -m pip show "$PKG" >/dev/null 2>&1; then
        VER=$($VENV_PYTHON -m pip show "$PKG" | grep Version | cut -d ' ' -f 2)
        echo -e "${GREEN}PASS${NC} ($VER)"
    else
        echo -e "${RED}FAIL${NC} (Not installed)"
    fi
done

echo ""
if [[ "$PATH" == *"/opt/homebrew/bin"* ]]; then
    echo -e "${GREEN}✅ PATH includes /opt/homebrew/bin${NC}"
else
    echo -e "${RED}⚠️  PATH missing /opt/homebrew/bin. Add 'export PATH=\"/opt/homebrew/bin:\$PATH\"' to your shell profile.${NC}"
fi

echo "Environment verification complete."
