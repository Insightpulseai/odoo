#!/bin/bash
# verify_module.sh - Quick module structure verification

echo "====================================="
echo "IPAI PPM Demo - Module Verification"
echo "====================================="

MODULE_PATH="/Users/tbwa/odoo-ce/addons/ipai_ppm_demo"
cd "$MODULE_PATH" || exit 1

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1"
        return 0
    else
        echo -e "${RED}✗${NC} $1 (MISSING)"
        return 1
    fi
}

check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $1/"
        return 0
    else
        echo -e "${RED}✗${NC} $1/ (MISSING)"
        return 1
    fi
}

echo ""
echo "Directory Structure:"
echo "--------------------"
check_dir "models"
check_dir "views"
check_dir "data"
check_dir "security"
check_dir "static/lib"
check_dir "static/src/js"
check_dir "static/src/xml"
check_dir "static/src/css"

echo ""
echo "Core Files:"
echo "-----------"
check_file "__init__.py"
check_file "__manifest__.py"
check_file "README.rst"
check_file "INSTALL.md"
check_file "IMPLEMENTATION_SUMMARY.md"

echo ""
echo "Models (7 Python files):"
echo "------------------------"
check_file "models/__init__.py"
check_file "models/project.py"
check_file "models/ppm_financial_period.py"
check_file "models/ppm_dependency_node.py"
check_file "models/ppm_intake_request.py"
check_file "models/ppm_ai_insight.py"
check_file "models/ppm_kanban.py"
check_file "models/ppm_dashboard_kpi.py"

echo ""
echo "Views (3 XML files):"
echo "--------------------"
check_file "views/ppm_menus.xml"
check_file "views/ppm_models_views.xml"
check_file "views/ppm_dashboard_action.xml"

echo ""
echo "Data (1 XML file):"
echo "------------------"
check_file "data/ppm_demo_data.xml"

echo ""
echo "Security (1 CSV file):"
echo "----------------------"
check_file "security/ir.model.access.csv"

echo ""
echo "Static Assets (4 files):"
echo "-------------------------"
check_file "static/lib/echarts.min.js"
check_file "static/src/js/ppm_dashboard.js"
check_file "static/src/xml/ppm_dashboard.xml"
check_file "static/src/css/ppm_dashboard.css"

echo ""
echo "====================================="
echo "Manifest Validation:"
echo "====================================="

# Check manifest version
MANIFEST_VERSION=$(grep "\"version\":" __manifest__.py | cut -d'"' -f4)
echo "Module Version: $MANIFEST_VERSION"

# Check license
MANIFEST_LICENSE=$(grep "\"license\":" __manifest__.py | cut -d'"' -f4)
if [ "$MANIFEST_LICENSE" == "AGPL-3" ]; then
    echo -e "${GREEN}✓${NC} License: $MANIFEST_LICENSE (OCA compliant)"
else
    echo -e "${RED}✗${NC} License: $MANIFEST_LICENSE (should be AGPL-3)"
fi

# Check dependencies
echo ""
echo "Dependencies:"
grep -A 3 "\"depends\":" __manifest__.py | grep -v depends | grep -v "^\s*\]"

# Check data files
echo ""
echo "Data Files:"
grep -A 7 "\"data\":" __manifest__.py | grep -v data | grep -v "^\s*\]"

# Check assets
echo ""
echo "Assets:"
grep -A 7 "\"assets\":" __manifest__.py | grep -v assets | grep -v "^\s*}" | grep -v "^\s*\]"

echo ""
echo "====================================="
echo "File Counts:"
echo "====================================="

PYTHON_COUNT=$(find models -name "*.py" | wc -l | tr -d ' ')
XML_COUNT=$(find views data -name "*.xml" 2>/dev/null | wc -l | tr -d ' ')
JS_COUNT=$(find static/src/js -name "*.js" 2>/dev/null | wc -l | tr -d ' ')
CSS_COUNT=$(find static/src/css -name "*.css" 2>/dev/null | wc -l | tr -d ' ')

echo "Python files: $PYTHON_COUNT (expected: 8)"
echo "XML files: $XML_COUNT (expected: 4)"
echo "JavaScript files: $JS_COUNT (expected: 1)"
echo "CSS files: $CSS_COUNT (expected: 1)"

# ECharts file size
if [ -f "static/lib/echarts.min.js" ]; then
    ECHARTS_SIZE=$(ls -lh static/lib/echarts.min.js | awk '{print $5}')
    echo "ECharts library: $ECHARTS_SIZE (expected: ~1MB)"
fi

echo ""
echo "====================================="
echo "Installation Command:"
echo "====================================="
echo ""
echo "  odoo-bin -d production -i ipai_ppm_demo --stop-after-init"
echo ""
echo "====================================="
echo "Access URL (after install):"
echo "====================================="
echo ""
echo "  Project → PPM Demo → PPM Dashboard"
echo ""
echo "====================================="
echo "Verification Complete!"
echo "====================================="
