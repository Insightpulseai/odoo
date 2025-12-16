#!/usr/bin/env bash
# CI Local Preflight Script
# Runs the same checks as GitHub Actions CI locally
# Usage: ./scripts/ci_local.sh
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================"
echo "  Odoo CE CI Preflight Checks"
echo "========================================"
echo ""

# Track failures
FAILURES=0

# 1. Environment Info
echo -e "${YELLOW}[INFO]${NC} Environment Information:"
echo "  Python: $(python3 --version 2>&1 || echo 'Not installed')"
echo "  Node: $(node --version 2>&1 || echo 'Not installed')"
echo "  Git: $(git --version 2>&1 || echo 'Not installed')"
echo ""

# 2. Submodules Check
echo -e "${YELLOW}[CHECK]${NC} Verifying git submodules..."
if git submodule status 2>&1 | grep -q "^fatal"; then
    echo -e "${RED}[FAIL]${NC} Submodule configuration error!"
    git submodule status 2>&1
    FAILURES=$((FAILURES + 1))
else
    echo -e "${GREEN}[PASS]${NC} Submodules configured correctly"
fi
echo ""

# 3. Addons Path Validation
echo -e "${YELLOW}[CHECK]${NC} Validating addons paths..."
ADDONS_DIRS="addons external-src oca-addons"
for dir in $ADDONS_DIRS; do
    if [ -d "$dir" ]; then
        COUNT=$(find "$dir" -name "__manifest__.py" 2>/dev/null | wc -l)
        echo "  $dir: $COUNT modules found"
    else
        echo -e "  ${YELLOW}$dir: directory not found (optional)${NC}"
    fi
done
echo ""

# 4. Enterprise View Mode Check (gantt is Enterprise-only)
echo -e "${YELLOW}[CHECK]${NC} Scanning for Enterprise-only view modes (gantt)..."
GANTT_MATCHES=""
if [ -d "addons" ]; then
    GANTT_MATCHES=$(grep -Rn "view_mode.*gantt\|view_type.*gantt" addons --include="*.xml" --include="*.py" 2>/dev/null || true)
fi
if [ -d "oca-addons" ]; then
    GANTT_MATCHES="$GANTT_MATCHES$(grep -Rn "view_mode.*gantt\|view_type.*gantt" oca-addons --include="*.xml" --include="*.py" 2>/dev/null || true)"
fi
if [ -n "$GANTT_MATCHES" ]; then
    echo -e "${RED}[FAIL]${NC} Found gantt view references (Enterprise-only):"
    echo "$GANTT_MATCHES" | head -10
    FAILURES=$((FAILURES + 1))
else
    echo -e "${GREEN}[PASS]${NC} No Enterprise view modes found"
fi
echo ""

# 5. Missing web_icon Check
echo -e "${YELLOW}[CHECK]${NC} Checking for missing web_icon references..."
ICON_ISSUES=0
if [ -d "addons" ]; then
    for manifest in addons/*/__manifest__.py; do
        if [ -f "$manifest" ]; then
            ICON_PATH=$(grep -o "'web_icon':\s*['\"][^'\"]*['\"]" "$manifest" 2>/dev/null | sed "s/'web_icon':\s*['\"]//;s/['\"]$//" || true)
            if [ -n "$ICON_PATH" ]; then
                MODULE_DIR=$(dirname "$manifest")
                # Handle paths like module_name/static/...
                if [[ "$ICON_PATH" == *"/"* ]]; then
                    FULL_PATH="addons/$ICON_PATH"
                else
                    FULL_PATH="$MODULE_DIR/$ICON_PATH"
                fi
                if [ ! -f "$FULL_PATH" ]; then
                    echo -e "  ${RED}Missing icon:${NC} $FULL_PATH (in $manifest)"
                    ICON_ISSUES=$((ICON_ISSUES + 1))
                fi
            fi
        fi
    done
fi
if [ $ICON_ISSUES -gt 0 ]; then
    echo -e "${RED}[FAIL]${NC} Found $ICON_ISSUES missing web_icon files"
    FAILURES=$((FAILURES + 1))
else
    echo -e "${GREEN}[PASS]${NC} All web_icon references valid"
fi
echo ""

# 6. Module Manifest Validation
echo -e "${YELLOW}[CHECK]${NC} Validating module manifests..."
MANIFEST_ISSUES=0
if [ -d "addons" ]; then
    for module_dir in addons/*/; do
        if [ -d "$module_dir" ]; then
            MODULE_NAME=$(basename "$module_dir")
            if [ ! -f "$module_dir/__manifest__.py" ]; then
                echo -e "  ${RED}Missing __manifest__.py:${NC} $MODULE_NAME"
                MANIFEST_ISSUES=$((MANIFEST_ISSUES + 1))
            fi
            if [ ! -f "$module_dir/__init__.py" ]; then
                echo -e "  ${RED}Missing __init__.py:${NC} $MODULE_NAME"
                MANIFEST_ISSUES=$((MANIFEST_ISSUES + 1))
            fi
        fi
    done
fi
if [ $MANIFEST_ISSUES -gt 0 ]; then
    echo -e "${RED}[FAIL]${NC} Found $MANIFEST_ISSUES manifest issues"
    FAILURES=$((FAILURES + 1))
else
    echo -e "${GREEN}[PASS]${NC} All module manifests valid"
fi
echo ""

# 7. Python Syntax Check
echo -e "${YELLOW}[CHECK]${NC} Checking Python syntax..."
if [ -d "addons" ]; then
    if python3 -m py_compile addons/*/*.py addons/*/*/*.py 2>/dev/null; then
        echo -e "${GREEN}[PASS]${NC} Python syntax OK"
    else
        echo -e "${RED}[FAIL]${NC} Python syntax errors found"
        FAILURES=$((FAILURES + 1))
    fi
fi
echo ""

# 8. Enterprise Contamination Check
echo -e "${YELLOW}[CHECK]${NC} Checking for Enterprise module dependencies..."
ENTERPRISE_DEPS=""
if [ -d "addons" ]; then
    ENTERPRISE_DEPS=$(grep -Rn "from odoo\.addons\..*_enterprise\|import odoo\.addons\..*_enterprise" addons 2>/dev/null || true)
fi
if [ -n "$ENTERPRISE_DEPS" ]; then
    echo -e "${RED}[FAIL]${NC} Found Enterprise dependencies:"
    echo "$ENTERPRISE_DEPS" | head -10
    FAILURES=$((FAILURES + 1))
else
    echo -e "${GREEN}[PASS]${NC} No Enterprise contamination"
fi
echo ""

# 9. Formatting Check (if tools available)
echo -e "${YELLOW}[CHECK]${NC} Checking code formatting..."
if command -v black &> /dev/null; then
    if black --check --line-length 88 addons 2>/dev/null; then
        echo -e "${GREEN}[PASS]${NC} Black formatting OK"
    else
        echo -e "${RED}[FAIL]${NC} Black formatting issues found (run: black addons)"
        FAILURES=$((FAILURES + 1))
    fi
else
    echo -e "${YELLOW}[SKIP]${NC} Black not installed"
fi

if command -v isort &> /dev/null; then
    if isort --check --profile black --line-length 88 addons 2>/dev/null; then
        echo -e "${GREEN}[PASS]${NC} isort OK"
    else
        echo -e "${RED}[FAIL]${NC} isort issues found (run: isort --profile black addons)"
        FAILURES=$((FAILURES + 1))
    fi
else
    echo -e "${YELLOW}[SKIP]${NC} isort not installed"
fi
echo ""

# Summary
echo "========================================"
if [ $FAILURES -gt 0 ]; then
    echo -e "${RED}  PREFLIGHT FAILED: $FAILURES issue(s)${NC}"
    echo "========================================"
    exit 1
else
    echo -e "${GREEN}  PREFLIGHT PASSED${NC}"
    echo "========================================"
    exit 0
fi
