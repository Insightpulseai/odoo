#!/bin/bash
# Odoo 19 EE Parity Test Runner
# Quick-start script for running parity validation

set -e

# Configuration
ODOO_URL="${ODOO_URL:-http://localhost:8069}"
ODOO_DB="${ODOO_DB:-odoo}"
ODOO_USER="${ODOO_USER:-admin}"
ODOO_PASS="${ODOO_PASS:-admin}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "=============================================================="
echo "         ODOO 19 ENTERPRISE EDITION PARITY TESTER             "
echo "=============================================================="
echo -e "${NC}"

# Parse arguments
CATEGORY=""
REPORT_FORMAT="text"
OUTPUT_FILE=""
VERBOSE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -c|--category)
            CATEGORY="$2"
            shift 2
            ;;
        -f|--format)
            REPORT_FORMAT="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE="-v"
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  -c, --category CATEGORY  Test specific category (accounting, payroll, approvals, helpdesk, planning)"
            echo "  -f, --format FORMAT      Output format: text (default), json, html"
            echo "  -o, --output FILE        Write report to file"
            echo "  -v, --verbose            Verbose output"
            echo "  -h, --help               Show this help"
            echo ""
            echo "Environment variables:"
            echo "  ODOO_URL   Odoo URL (default: http://localhost:8069)"
            echo "  ODOO_DB    Database name (default: odoo)"
            echo "  ODOO_USER  Username (default: admin)"
            echo "  ODOO_PASS  Password (default: admin)"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Check if Odoo is reachable
echo -e "${YELLOW}Checking Odoo connection...${NC}"
if curl -s --connect-timeout 5 "${ODOO_URL}/web/health" > /dev/null 2>&1 || \
   curl -s --connect-timeout 5 "${ODOO_URL}/web/login" > /dev/null 2>&1; then
    echo -e "${GREEN}[OK] Odoo reachable at ${ODOO_URL}${NC}"
else
    echo -e "${RED}[FAIL] Cannot connect to Odoo at ${ODOO_URL}${NC}"
    echo ""
    echo "Make sure Odoo is running. For dev sandbox:"
    echo "  cd ~/Documents/GitHub/odoo-ce/sandbox/dev && docker compose up -d"
    exit 1
fi

# Build command
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CMD="python3 ${SCRIPT_DIR}/test_ee_parity.py"
CMD+=" --odoo-url '${ODOO_URL}'"
CMD+=" --db '${ODOO_DB}'"
CMD+=" --username '${ODOO_USER}'"
CMD+=" --password '${ODOO_PASS}'"
CMD+=" --report ${REPORT_FORMAT}"

if [ -n "$CATEGORY" ]; then
    CMD+=" --category ${CATEGORY}"
    echo -e "${BLUE}Testing category: ${CATEGORY}${NC}"
fi

if [ -n "$OUTPUT_FILE" ]; then
    CMD+=" --output '${OUTPUT_FILE}'"
fi

if [ -n "$VERBOSE" ]; then
    CMD+=" ${VERBOSE}"
fi

# Run tests
echo ""
echo -e "${YELLOW}Running parity tests...${NC}"
echo ""

eval $CMD
EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}=============================================================="
    echo "                   PARITY TEST PASSED                         "
    echo "==============================================================${NC}"
else
    echo -e "${YELLOW}=============================================================="
    echo "             PARITY TEST: GAPS IDENTIFIED                     "
    echo "==============================================================${NC}"
fi

if [ -n "$OUTPUT_FILE" ]; then
    echo ""
    echo -e "${BLUE}Report saved to: ${OUTPUT_FILE}${NC}"

    # Open HTML report in browser if applicable
    if [[ "$REPORT_FORMAT" == "html" && "$OSTYPE" == "darwin"* ]]; then
        echo "Opening report in browser..."
        open "$OUTPUT_FILE"
    fi
fi

exit $EXIT_CODE
