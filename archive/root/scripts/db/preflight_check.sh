#!/usr/bin/env bash
# =============================================================================
# DB Hardening Preflight Check
# =============================================================================
# Purpose: Verify PostgreSQL database has required IMMUTABLE wrapper before
#          Odoo module installation (prevents "functions in index expression
#          must be marked IMMUTABLE" errors)
#
# Usage:
#   ./scripts/db/preflight_check.sh [database_name] [--strict]
#
# Exit codes:
#   0 - All checks passed
#   1 - Checks failed (in strict mode)
#   2 - Database not accessible
#
# Environment detection:
#   ODOO_ENV=dev|staging  → Fail-fast on errors
#   ODOO_ENV=prod         → Warn-only (unless --strict)
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

DB_NAME="${1:-odoo_dev}"
STRICT_MODE="${2:-}"
ODOO_ENV="${ODOO_ENV:-dev}"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check if running in strict mode or dev/staging
FAIL_FAST=false
if [[ "${STRICT_MODE}" == "--strict" ]] || [[ "${ODOO_ENV}" =~ ^(dev|staging)$ ]]; then
    FAIL_FAST=true
fi

echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}DB Hardening Preflight Check${NC}"
echo -e "${YELLOW}Database: ${DB_NAME} | Environment: ${ODOO_ENV} | Fail-fast: ${FAIL_FAST}${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check if database is accessible
if ! docker-compose ps db 2>/dev/null | grep -q "Up"; then
    echo -e "${RED}✗ Database container is not running${NC}"
    echo -e "${YELLOW}Run: docker-compose up -d db${NC}"
    exit 2
fi

# Function to run SQL and check result
check_sql() {
    local description="$1"
    local query="$2"
    local expected_pattern="$3"

    echo -n "→ ${description}... "

    if ! result=$(docker-compose exec -T db psql -U odoo -d "${DB_NAME}" -t -c "${query}" 2>&1); then
        echo -e "${RED}✗ Query failed${NC}"
        echo "  Error: ${result}"
        return 1
    fi

    if echo "${result}" | grep -q "${expected_pattern}"; then
        echo -e "${GREEN}✓${NC}"
        return 0
    else
        echo -e "${RED}✗ Not found${NC}"
        echo "  Expected pattern: ${expected_pattern}"
        echo "  Got: ${result}"
        return 1
    fi
}

# Track failures
FAILED_CHECKS=0

# Check 1: unaccent extension exists
if ! check_sql "Checking unaccent extension" \
    "SELECT COUNT(*) FROM pg_extension WHERE extname = 'unaccent';" \
    "1"; then
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
    echo -e "${YELLOW}  Remediation: Run ./scripts/db/apply_unaccent_fix.sh${NC}"
fi

# Check 2: pg_trgm extension exists
if ! check_sql "Checking pg_trgm extension" \
    "SELECT COUNT(*) FROM pg_extension WHERE extname = 'pg_trgm';" \
    "1"; then
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
    echo -e "${YELLOW}  Remediation: Run ./scripts/db/apply_unaccent_fix.sh${NC}"
fi

# Check 3: unaccent_immutable function exists and is IMMUTABLE
if ! check_sql "Checking unaccent_immutable(text) exists and is IMMUTABLE" \
    "SELECT CASE p.provolatile WHEN 'i' THEN 'IMMUTABLE' ELSE 'NOT_IMMUTABLE' END
     FROM pg_proc p
     JOIN pg_namespace n ON n.oid = p.pronamespace
     WHERE n.nspname = 'public'
       AND p.proname = 'unaccent_immutable'
       AND pg_get_function_identity_arguments(p.oid) = 'text';" \
    "IMMUTABLE"; then
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
    echo -e "${YELLOW}  Remediation: Run ./scripts/db/apply_unaccent_fix.sh${NC}"
fi

# Check 4: public.unaccent(text) is IMMUTABLE (best-effort, may not exist)
echo -n "→ Checking public.unaccent(text) volatility... "
volatility=$(docker-compose exec -T db psql -U odoo -d "${DB_NAME}" -t -c "
SELECT CASE p.provolatile
    WHEN 'i' THEN 'IMMUTABLE'
    WHEN 's' THEN 'STABLE'
    WHEN 'v' THEN 'VOLATILE'
END
FROM pg_proc p
JOIN pg_namespace n ON n.oid = p.pronamespace
WHERE n.nspname = 'public'
  AND p.proname = 'unaccent'
  AND pg_get_function_identity_arguments(p.oid) = 'text';" 2>/dev/null | tr -d '[:space:]')

if [[ "${volatility}" == "IMMUTABLE" ]]; then
    echo -e "${GREEN}✓ IMMUTABLE${NC}"
elif [[ -z "${volatility}" ]]; then
    echo -e "${YELLOW}⊘ Not found (wrapper is sufficient)${NC}"
else
    echo -e "${YELLOW}⚠ ${volatility} (recommend IMMUTABLE)${NC}"
    echo -e "${YELLOW}  Note: Wrapper function works, but setting unaccent to IMMUTABLE improves OCA compatibility${NC}"
    echo -e "${YELLOW}  Remediation: Run ./scripts/db/apply_unaccent_fix.sh${NC}"
fi

echo ""

# Summary
if [[ ${FAILED_CHECKS} -eq 0 ]]; then
    echo -e "${GREEN}✅ All preflight checks passed${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    exit 0
else
    echo -e "${RED}❌ ${FAILED_CHECKS} preflight check(s) failed${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    if [[ "${FAIL_FAST}" == "true" ]]; then
        echo -e "${RED}Failing fast (${ODOO_ENV} environment or --strict mode)${NC}"
        echo ""
        echo "Quick fix:"
        echo "  ./scripts/db/apply_unaccent_fix.sh ${DB_NAME}"
        echo ""
        exit 1
    else
        echo -e "${YELLOW}Warning only (production environment)${NC}"
        echo -e "${YELLOW}Please apply the fix before installing OCA modules:${NC}"
        echo "  ./scripts/db/apply_unaccent_fix.sh ${DB_NAME}"
        echo ""
        exit 0
    fi
fi
