#!/bin/bash
# Phase 5 Verification Script
# Verifies AI Platform integration components

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=== Phase 5: AI Platform Integration Verification ==="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Part A: Odoo Module
echo "Part A: Odoo Backend Integration"
echo "─────────────────────────────────────"

echo -n "✓ Module directory exists: "
if [ -d "$REPO_ROOT/addons/ipai/ipai_ai_platform" ]; then
    echo -e "${GREEN}YES${NC}"
else
    echo -e "${RED}NO${NC}"
    exit 1
fi

echo -n "✓ Manifest file valid: "
if [ -f "$REPO_ROOT/addons/ipai/ipai_ai_platform/__manifest__.py" ]; then
    python3 -c "import ast; ast.parse(open('$REPO_ROOT/addons/ipai/ipai_ai_platform/__manifest__.py').read())"
    echo -e "${GREEN}YES${NC}"
else
    echo -e "${RED}NO${NC}"
    exit 1
fi

echo -n "✓ AI client model exists: "
if [ -f "$REPO_ROOT/addons/ipai/ipai_ai_platform/models/ai_client.py" ]; then
    echo -e "${GREEN}YES${NC}"
else
    echo -e "${RED}NO${NC}"
    exit 1
fi

echo -n "✓ Config parameters XML valid: "
if [ -f "$REPO_ROOT/addons/ipai/ipai_ai_platform/data/config_parameters.xml" ]; then
    xmllint --noout "$REPO_ROOT/addons/ipai/ipai_ai_platform/data/config_parameters.xml" 2>/dev/null
    echo -e "${GREEN}YES${NC}"
else
    echo -e "${RED}NO${NC}"
    exit 1
fi

echo -n "✓ Security CSV exists: "
if [ -f "$REPO_ROOT/addons/ipai/ipai_ai_platform/security/ir.model.access.csv" ]; then
    echo -e "${GREEN}YES${NC}"
else
    echo -e "${RED}NO${NC}"
    exit 1
fi

echo ""

# Part B: TypeScript SDK
echo "Part B: TypeScript SDK"
echo "─────────────────────────────────────"

echo -n "✓ SDK directory exists: "
if [ -d "$REPO_ROOT/packages/ipai-ai-sdk" ]; then
    echo -e "${GREEN}YES${NC}"
else
    echo -e "${RED}NO${NC}"
    exit 1
fi

echo -n "✓ package.json valid: "
if [ -f "$REPO_ROOT/packages/ipai-ai-sdk/package.json" ]; then
    jq empty "$REPO_ROOT/packages/ipai-ai-sdk/package.json" 2>/dev/null
    echo -e "${GREEN}YES${NC}"
else
    echo -e "${RED}NO${NC}"
    exit 1
fi

echo -n "✓ TypeScript files exist: "
TS_FILES=(
    "src/index.ts"
    "src/types.ts"
    "src/client.ts"
    "src/errors.ts"
)
all_exist=true
for file in "${TS_FILES[@]}"; do
    if [ ! -f "$REPO_ROOT/packages/ipai-ai-sdk/$file" ]; then
        all_exist=false
        break
    fi
done
if [ "$all_exist" = true ]; then
    echo -e "${GREEN}YES${NC}"
else
    echo -e "${RED}NO${NC}"
    exit 1
fi

echo -n "✓ tsconfig.json valid: "
if [ -f "$REPO_ROOT/packages/ipai-ai-sdk/tsconfig.json" ]; then
    jq empty "$REPO_ROOT/packages/ipai-ai-sdk/tsconfig.json" 2>/dev/null
    echo -e "${GREEN}YES${NC}"
else
    echo -e "${RED}NO${NC}"
    exit 1
fi

echo ""

# Part C: Python SDK
echo "Part C: Python SDK"
echo "─────────────────────────────────────"

echo -n "✓ SDK directory exists: "
if [ -d "$REPO_ROOT/packages/ipai-ai-sdk-python" ]; then
    echo -e "${GREEN}YES${NC}"
else
    echo -e "${RED}NO${NC}"
    exit 1
fi

echo -n "✓ setup.py valid: "
if [ -f "$REPO_ROOT/packages/ipai-ai-sdk-python/setup.py" ]; then
    python3 -c "import ast; ast.parse(open('$REPO_ROOT/packages/ipai-ai-sdk-python/setup.py').read())"
    echo -e "${GREEN}YES${NC}"
else
    echo -e "${RED}NO${NC}"
    exit 1
fi

echo -n "✓ Python module files exist: "
PY_FILES=(
    "ipai_ai_sdk/__init__.py"
    "ipai_ai_sdk/types.py"
    "ipai_ai_sdk/client.py"
)
all_exist=true
for file in "${PY_FILES[@]}"; do
    if [ ! -f "$REPO_ROOT/packages/ipai-ai-sdk-python/$file" ]; then
        all_exist=false
        break
    fi
done
if [ "$all_exist" = true ]; then
    echo -e "${GREEN}YES${NC}"
else
    echo -e "${RED}NO${NC}"
    exit 1
fi

echo -n "✓ pyproject.toml valid: "
if [ -f "$REPO_ROOT/packages/ipai-ai-sdk-python/pyproject.toml" ]; then
    python3 -c "import tomllib; tomllib.load(open('$REPO_ROOT/packages/ipai-ai-sdk-python/pyproject.toml', 'rb'))" 2>/dev/null || \
    python3 -c "import toml; toml.load(open('$REPO_ROOT/packages/ipai-ai-sdk-python/pyproject.toml'))" 2>/dev/null
    echo -e "${GREEN}YES${NC}"
else
    echo -e "${RED}NO${NC}"
    exit 1
fi

echo ""

# Part D: Documentation
echo "Part D: Platform Documentation"
echo "─────────────────────────────────────"

echo -n "✓ Platform docs exist: "
if [ -f "$REPO_ROOT/docs/platform/ai.md" ]; then
    echo -e "${GREEN}YES${NC}"
else
    echo -e "${RED}NO${NC}"
    exit 1
fi

echo -n "✓ TypeScript SDK README: "
if [ -f "$REPO_ROOT/packages/ipai-ai-sdk/README.md" ]; then
    echo -e "${GREEN}YES${NC}"
else
    echo -e "${RED}NO${NC}"
    exit 1
fi

echo -n "✓ Python SDK README: "
if [ -f "$REPO_ROOT/packages/ipai-ai-sdk-python/README.md" ]; then
    echo -e "${GREEN}YES${NC}"
else
    echo -e "${RED}NO${NC}"
    exit 1
fi

echo -n "✓ Odoo module README: "
if [ -f "$REPO_ROOT/addons/ipai/ipai_ai_platform/README.md" ]; then
    echo -e "${GREEN}YES${NC}"
else
    echo -e "${RED}NO${NC}"
    exit 1
fi

echo ""

# File count summary
echo "File Count Summary"
echo "─────────────────────────────────────"
echo "Odoo module files:      $(find "$REPO_ROOT/addons/ipai/ipai_ai_platform" -type f | wc -l | tr -d ' ')"
echo "TypeScript SDK files:   $(find "$REPO_ROOT/packages/ipai-ai-sdk" -type f | wc -l | tr -d ' ')"
echo "Python SDK files:       $(find "$REPO_ROOT/packages/ipai-ai-sdk-python" -type f | wc -l | tr -d ' ')"
echo "Documentation files:    $(find "$REPO_ROOT/docs/platform" -type f -name '*.md' | wc -l | tr -d ' ')"

echo ""
echo -e "${GREEN}✅ Phase 5 verification PASSED${NC}"
echo ""
echo "Next Steps:"
echo "1. Odoo: Install module + configure system parameters"
echo "2. TypeScript: pnpm install && pnpm build (in packages/ipai-ai-sdk)"
echo "3. Python: pip install -e . (in packages/ipai-ai-sdk-python)"
echo "4. Test: Run health checks and sample queries"
echo ""
