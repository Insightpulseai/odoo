#!/bin/bash
# OdooForge Sandbox - Quick UAT Smoke Test
# Run from host machine to verify sandbox installation

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SANDBOX_DIR="$(dirname "$SCRIPT_DIR")"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASS_COUNT=0
FAIL_COUNT=0

test_pass() {
    echo -e "Testing: $1... ${GREEN}✓ PASS${NC}"
    ((PASS_COUNT++))
}

test_fail() {
    echo -e "Testing: $1... ${RED}✗ FAIL${NC}"
    echo -e "  ${YELLOW}$2${NC}"
    ((FAIL_COUNT++))
}

echo ""
echo "=============================================="
echo "   OdooForge Sandbox - Quick UAT"
echo "=============================================="
echo ""

cd "$SANDBOX_DIR"

# Test 1: Docker running
if docker info &> /dev/null; then
    test_pass "Docker running"
else
    test_fail "Docker running" "Docker daemon not running"
fi

# Test 2: Containers up
if docker compose ps | grep -q "running"; then
    test_pass "Containers up"
else
    test_fail "Containers up" "Containers not running. Run: docker compose up -d"
fi

# Test 3: Odoo accessible
if curl -sf http://localhost:8069/web/health &> /dev/null; then
    test_pass "Odoo accessible"
else
    test_fail "Odoo accessible" "Cannot reach http://localhost:8069"
fi

# Test 4: Kit version
if docker compose exec -T kit kit version &> /dev/null; then
    test_pass "kit version"
else
    test_fail "kit version" "Kit CLI not responding"
fi

# Test 5: Kit init
TEST_MODULE="ipai_uat_smoke_$$"
if docker compose exec -T kit kit init "$TEST_MODULE" &> /dev/null; then
    test_pass "kit init"
else
    test_fail "kit init" "Failed to create test module"
fi

# Test 6: Kit validate
if docker compose exec -T kit kit validate "$TEST_MODULE" 2>&1 | grep -qi "pass"; then
    test_pass "kit validate"
else
    test_fail "kit validate" "Module validation failed"
fi

# Cleanup test module
docker compose exec -T kit rm -rf "/workspace/addons/$TEST_MODULE" &> /dev/null || true

# Summary
echo ""
echo "=============================================="
TOTAL=$((PASS_COUNT + FAIL_COUNT))

if [ $FAIL_COUNT -eq 0 ]; then
    echo -e "${GREEN}✅ UAT PASSED${NC} ($PASS_COUNT/$TOTAL tests)"
    exit 0
else
    echo -e "${RED}❌ UAT FAILED${NC} ($PASS_COUNT/$TOTAL passed, $FAIL_COUNT failed)"
    exit 1
fi
