#!/usr/bin/env bash
# ==============================================================================
# Dev Container Verification Script
# ==============================================================================
# Verifies Dev Container setup and service health
#
# Usage:
#   ./.devcontainer/scripts/verify-devcontainer.sh
#
# Exit codes:
#   0 - All checks passed
#   1 - One or more checks failed
# ==============================================================================

set -euo pipefail

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

checks_passed=0
checks_failed=0

echo "======================================================================"
echo "Dev Container Verification"
echo "======================================================================"
echo ""

# Helper function for check results
check_result() {
    local description="$1"
    local command="$2"

    echo -n "[$description] ... "

    if eval "$command" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ PASS${NC}"
        ((checks_passed++))
        return 0
    else
        echo -e "${RED}❌ FAIL${NC}"
        ((checks_failed++))
        return 1
    fi
}

# Helper function with output
check_with_output() {
    local description="$1"
    local command="$2"

    echo -n "[$description] ... "

    if output=$(eval "$command" 2>&1); then
        echo -e "${GREEN}✅ PASS${NC}"
        echo "   → $output"
        ((checks_passed++))
        return 0
    else
        echo -e "${RED}❌ FAIL${NC}"
        echo "   → $output"
        ((checks_failed++))
        return 1
    fi
}

echo "--- Environment Checks ---"
check_with_output "Python version" "python --version"
check_with_output "Node version" "node --version"
check_with_output "pnpm version" "pnpm --version"
check_result "uv installed" "command -v uv"
check_result "specify installed" "command -v specify"
check_result "Docker accessible" "command -v docker"
echo ""

echo "--- Docker Compose Services ---"
check_result "Docker Compose accessible" "docker compose version"
check_with_output "PostgreSQL service" "docker compose ps db | grep -q healthy"
check_with_output "Redis service" "docker compose ps redis | grep -q healthy"
check_with_output "Odoo service" "docker compose ps odoo | grep -q healthy || docker compose ps odoo | grep -q Up"
echo ""

echo "--- Database Checks ---"
check_result "PostgreSQL connection" "docker compose exec -T db pg_isready -U odoo"
check_result "Database odoo_dev exists" "docker compose exec -T db psql -U odoo -lqt | cut -d \\| -f 1 | grep -qw odoo_dev"
check_result "Database odoo_stage exists" "docker compose exec -T db psql -U odoo -lqt | cut -d \\| -f 1 | grep -qw odoo_stage"
check_result "Database odoo_prod exists" "docker compose exec -T db psql -U odoo -lqt | cut -d \\| -f 1 | grep -qw odoo_prod"
echo ""

echo "--- Service Health Checks ---"
check_result "Odoo HTTP responds" "curl -sf -o /dev/null http://localhost:8069/web/health || curl -sf -o /dev/null http://localhost:8069/web/login"
check_result "Redis ping" "docker compose exec -T redis redis-cli ping | grep -q PONG"
echo ""

echo "--- Workspace Checks ---"
check_result "Workspace file exists" "test -f /workspace/odoo.code-workspace"
check_result "IPAI modules directory" "test -d /workspace/addons/ipai"
check_result "OCA modules directory" "test -d /workspace/addons/oca"
check_result "Scripts directory" "test -d /workspace/scripts"
check_result "Docs directory" "test -d /workspace/docs"
check_result "Spec directory" "test -d /workspace/spec"
echo ""

echo "--- Git Configuration ---"
check_result "Git safe directory" "git config --get-all safe.directory | grep -q /workspace/odoo || git config --get-all safe.directory | grep -q /workspace"
check_result "Pre-commit installed" "command -v pre-commit"
echo ""

echo "--- Python Development Tools ---"
check_result "black installed" "python -c 'import black'"
check_result "flake8 installed" "python -c 'import flake8'"
check_result "isort installed" "python -c 'import isort'"
check_result "pytest installed" "python -c 'import pytest'"
echo ""

echo "======================================================================"
echo "Verification Summary"
echo "======================================================================"
echo -e "${GREEN}Passed: $checks_passed${NC}"
echo -e "${RED}Failed: $checks_failed${NC}"
echo ""

if [ $checks_failed -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed! Dev Container is ready.${NC}"
    echo ""
    echo "Next steps:"
    echo "  • Odoo:      http://localhost:8069"
    echo "  • Database:  psql -U odoo -d odoo_dev"
    echo "  • Docker:    docker ps"
    echo ""
    exit 0
else
    echo -e "${RED}❌ Some checks failed. See errors above.${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "  • Check Docker Compose: docker compose ps"
    echo "  • View logs: docker compose logs db odoo redis"
    echo "  • Retry setup: ./.devcontainer/scripts/post-create.sh"
    echo ""
    exit 1
fi
