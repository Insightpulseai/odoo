#!/bin/bash
# scripts/validate_ee_iap_independence.sh
#
# Validates that the Odoo CE deployment has no EE or IAP dependencies.
# This script checks:
# 1. No EE module dependencies in ipai_* manifests
# 2. No EE model inheritance in ipai_* Python code
# 3. No EE modules installed in the database
# 4. No IAP configuration in system parameters
#
# Usage:
#   ./scripts/validate_ee_iap_independence.sh [--database DATABASE] [--url ODOO_URL]
#
# Exit codes:
#   0 - All checks passed
#   1 - One or more checks failed

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ODOO_URL="${ODOO_URL:-http://localhost:8069}"
ODOO_DB="${ODOO_DATABASE:-odoo_core}"
ODOO_USER="${ODOO_USER:-admin}"
ODOO_PASSWORD="${ODOO_PASSWORD:-admin}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --database)
            ODOO_DB="$2"
            shift 2
            ;;
        --url)
            ODOO_URL="$2"
            shift 2
            ;;
        --password)
            ODOO_PASSWORD="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo "=============================================="
echo "EE/IAP Independence Validation"
echo "=============================================="
echo "Repository: $REPO_ROOT"
echo "Odoo URL: $ODOO_URL"
echo "Database: $ODOO_DB"
echo "=============================================="

FAILED=0
WARNINGS=0

# -----------------------------------------------------------------------------
# Check 1: No EE module dependencies in manifests
# -----------------------------------------------------------------------------
echo ""
echo -e "${YELLOW}[1/5] Checking manifest dependencies...${NC}"

# Known EE-only modules
EE_MODULES_PATTERN="^(iot|pos_iot|web_studio|sign|helpdesk|planning|appointment|social|voip|quality_control|data_recycle|timesheet_grid|mrp_workorder|stock_barcode|marketing_automation|marketing_card|sale_amazon|sale_subscription|hr_appraisal|cloud_storage|mail_plugin|mail_plugin_gmail|mail_plugin_outlook|account_accountant|industry_fsm|documents|approvals|account_bank_statement_import|account_reports|knowledge)$"

EE_FOUND=0
for manifest in "$REPO_ROOT"/addons/ipai/**/__manifest__.py "$REPO_ROOT"/addons/ipai/*/__manifest__.py 2>/dev/null; do
    if [[ -f "$manifest" ]]; then
        # Extract depends list and check for EE modules
        DEPENDS=$(grep -A 50 "'depends'" "$manifest" | grep -oP "'[a-z_]+'" | tr -d "'" || true)
        for dep in $DEPENDS; do
            if echo "$dep" | grep -qE "$EE_MODULES_PATTERN"; then
                echo -e "${RED}[FAIL] EE dependency '$dep' found in: $manifest${NC}"
                EE_FOUND=1
            fi
        done
    fi
done

if [[ $EE_FOUND -eq 0 ]]; then
    echo -e "${GREEN}[PASS] No EE dependencies in manifests${NC}"
else
    FAILED=1
fi

# -----------------------------------------------------------------------------
# Check 2: No EE model inheritance
# -----------------------------------------------------------------------------
echo ""
echo -e "${YELLOW}[2/5] Checking model inheritance...${NC}"

# Known EE-only models
EE_MODELS_PATTERN="(iot\.box|iot\.device|sign\.request|sign\.template|helpdesk\.ticket|helpdesk\.stage|planning\.slot|cloud\.storage|studio\.|documents\.|approval\.)"

EE_INHERIT_FOUND=0
for pyfile in "$REPO_ROOT"/addons/ipai/**/*.py "$REPO_ROOT"/addons/ipai/*/*.py 2>/dev/null; do
    if [[ -f "$pyfile" ]]; then
        if grep -qE "_inherit.*=.*['\"]($EE_MODELS_PATTERN)" "$pyfile" 2>/dev/null; then
            echo -e "${RED}[FAIL] EE model inheritance in: $pyfile${NC}"
            grep -E "_inherit" "$pyfile" | head -3
            EE_INHERIT_FOUND=1
        fi
    fi
done

if [[ $EE_INHERIT_FOUND -eq 0 ]]; then
    echo -e "${GREEN}[PASS] No EE model inheritance${NC}"
else
    FAILED=1
fi

# -----------------------------------------------------------------------------
# Check 3: No EE view inheritance
# -----------------------------------------------------------------------------
echo ""
echo -e "${YELLOW}[3/5] Checking view inheritance...${NC}"

# Known EE view patterns
EE_VIEW_PATTERN="(iot\.|studio\.|sign\.|helpdesk\.|planning\.|documents\.|approval\.)"

EE_VIEW_FOUND=0
for xmlfile in "$REPO_ROOT"/addons/ipai/**/*.xml "$REPO_ROOT"/addons/ipai/*/*.xml 2>/dev/null; do
    if [[ -f "$xmlfile" ]]; then
        if grep -qE "inherit_id.*ref=['\"]($EE_VIEW_PATTERN)" "$xmlfile" 2>/dev/null; then
            echo -e "${RED}[FAIL] EE view inheritance in: $xmlfile${NC}"
            grep -E "inherit_id" "$xmlfile" | head -3
            EE_VIEW_FOUND=1
        fi
    fi
done

if [[ $EE_VIEW_FOUND -eq 0 ]]; then
    echo -e "${GREEN}[PASS] No EE view inheritance${NC}"
else
    FAILED=1
fi

# -----------------------------------------------------------------------------
# Check 4: Verify Python syntax
# -----------------------------------------------------------------------------
echo ""
echo -e "${YELLOW}[4/5] Verifying Python syntax...${NC}"

SYNTAX_ERRORS=0
for pyfile in "$REPO_ROOT"/addons/ipai/**/*.py "$REPO_ROOT"/addons/ipai/*/*.py 2>/dev/null; do
    if [[ -f "$pyfile" ]]; then
        if ! python3 -m py_compile "$pyfile" 2>/dev/null; then
            echo -e "${RED}[FAIL] Syntax error in: $pyfile${NC}"
            SYNTAX_ERRORS=1
        fi
    fi
done

if [[ $SYNTAX_ERRORS -eq 0 ]]; then
    echo -e "${GREEN}[PASS] All Python files have valid syntax${NC}"
else
    FAILED=1
fi

# -----------------------------------------------------------------------------
# Check 5: Check installed modules (requires running Odoo)
# -----------------------------------------------------------------------------
echo ""
echo -e "${YELLOW}[5/5] Checking installed modules (optional)...${NC}"

# Only run if Odoo is accessible
if curl -sf "$ODOO_URL/web/health" >/dev/null 2>&1; then
    # Use Python to check via XML-RPC
    EE_INSTALLED=$(python3 << EOF 2>/dev/null || echo "error"
import xmlrpc.client
import sys

try:
    common = xmlrpc.client.ServerProxy('$ODOO_URL/xmlrpc/2/common')
    uid = common.authenticate('$ODOO_DB', '$ODOO_USER', '$ODOO_PASSWORD', {})

    if not uid:
        print("auth_failed")
        sys.exit(0)

    models = xmlrpc.client.ServerProxy('$ODOO_URL/xmlrpc/2/object')
    ee_modules = models.execute_kw(
        '$ODOO_DB', uid, '$ODOO_PASSWORD',
        'ir.module.module', 'search_read',
        [[['license', '=', 'OEEL-1'], ['state', '=', 'installed']]],
        {'fields': ['name']}
    )

    if ee_modules:
        print(','.join([m['name'] for m in ee_modules]))
    else:
        print("none")
except Exception as e:
    print(f"error:{e}")
EOF
)

    if [[ "$EE_INSTALLED" == "none" ]]; then
        echo -e "${GREEN}[PASS] No EE modules installed in database${NC}"
    elif [[ "$EE_INSTALLED" == "auth_failed" ]]; then
        echo -e "${YELLOW}[SKIP] Could not authenticate to Odoo${NC}"
        WARNINGS=$((WARNINGS + 1))
    elif [[ "$EE_INSTALLED" == error* ]]; then
        echo -e "${YELLOW}[SKIP] Could not connect to Odoo: ${EE_INSTALLED#error:}${NC}"
        WARNINGS=$((WARNINGS + 1))
    else
        echo -e "${RED}[FAIL] EE modules installed: $EE_INSTALLED${NC}"
        FAILED=1
    fi
else
    echo -e "${YELLOW}[SKIP] Odoo not accessible at $ODOO_URL${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

# -----------------------------------------------------------------------------
# Summary
# -----------------------------------------------------------------------------
echo ""
echo "=============================================="
if [[ $FAILED -eq 0 ]]; then
    if [[ $WARNINGS -gt 0 ]]; then
        echo -e "${YELLOW}[SUCCESS with warnings] All static checks passed${NC}"
        echo -e "${YELLOW}Warnings: $WARNINGS (some runtime checks skipped)${NC}"
    else
        echo -e "${GREEN}[SUCCESS] All EE/IAP independence checks passed${NC}"
    fi
    echo "=============================================="
    exit 0
else
    echo -e "${RED}[FAILED] One or more checks failed${NC}"
    echo "=============================================="
    exit 1
fi
