#!/bin/bash
set -euo pipefail

# Odoo CE v0.9.1 - Production Smoke Test
# Verifies that the deployment is healthy and functional
# Date: 2025-11-25

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 Odoo CE v0.9.1 Production Smoke Test${NC}"
echo "=========================================="

PASSED=0
FAILED=0
WARNINGS=0

# Test function
run_test() {
    local test_name="$1"
    local test_command="$2"
    local required="${3:-yes}"  # yes/no, default yes
    
    echo -en "${test_name}... "
    
    if eval "$test_command" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PASS${NC}"
        ((PASSED++))
        return 0
    else
        if [[ "$required" == "yes" ]]; then
            echo -e "${RED}❌ FAIL${NC}"
            ((FAILED++))
        else
            echo -e "${YELLOW}⚠️  WARN${NC}"
            ((WARNINGS++))
        fi
        return 1
    fi
}

# Test 1: Container Running
echo -e "\n${BLUE}Container Status Tests${NC}"
run_test "1.1. Odoo container exists" "docker ps -a | grep -q odoo-ce"
run_test "1.2. Odoo container running" "docker ps | grep -q odoo-ce"
run_test "1.3. Database container running" "docker ps | grep -q odoo-db"

# Test 2: Health Checks
echo -e "\n${BLUE}Health Check Tests${NC}"
run_test "2.1. Docker health check" "docker inspect odoo-ce | grep -q '\"Status\": \"healthy\"'" "no"
run_test "2.2. Health endpoint responding" "curl -sf http://127.0.0.1:8069/web/health"
run_test "2.3. Database accepting connections" "docker exec odoo-db pg_isready -U odoo"

# Test 3: Web Interface
echo -e "\n${BLUE}Web Interface Tests${NC}"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8069/web)
if [[ "$HTTP_CODE" == "200" || "$HTTP_CODE" == "302" ]]; then
    echo -e "3.1. Web interface responding... ${GREEN}✅ PASS${NC} (HTTP $HTTP_CODE)"
    ((PASSED++))
else
    echo -e "3.1. Web interface responding... ${RED}❌ FAIL${NC} (HTTP $HTTP_CODE)"
    ((FAILED++))
fi

# Test for HTTPS if on production VPS
if [[ -f "/etc/hostname" ]] && [[ "$(cat /etc/hostname)" == "odoo-erp-prod" ]]; then
    HTTPS_CODE=$(curl -sk -o /dev/null -w "%{http_code}" https://erp.insightpulseai.net/web 2>/dev/null || echo "000")
    if [[ "$HTTPS_CODE" == "200" || "$HTTPS_CODE" == "302" ]]; then
        echo -e "3.2. HTTPS endpoint... ${GREEN}✅ PASS${NC} (HTTP $HTTPS_CODE)"
        ((PASSED++))
    else
        echo -e "3.2. HTTPS endpoint... ${YELLOW}⚠️  WARN${NC} (HTTP $HTTPS_CODE)"
        ((WARNINGS++))
    fi
fi

# Test 4: Custom Modules
echo -e "\n${BLUE}Custom Modules Tests${NC}"

MODULE_COUNT=$(docker exec odoo-ce ls -1 /mnt/extra-addons 2>/dev/null | grep -c "^ipai_" || echo "0")
if [[ "$MODULE_COUNT" -eq 5 ]]; then
    echo -e "4.1. Custom modules present... ${GREEN}✅ PASS${NC} (5 modules)"
    ((PASSED++))
else
    echo -e "4.1. Custom modules present... ${RED}❌ FAIL${NC} (expected 5, found $MODULE_COUNT)"
    ((FAILED++))
fi

# List modules
echo "4.2. Module inventory:"
docker exec odoo-ce ls -1 /mnt/extra-addons 2>/dev/null | grep "^ipai_" | while read -r module; do
    echo "     - ${module}"
done

# Test 5: Configuration
echo -e "\n${BLUE}Configuration Tests${NC}"
run_test "5.1. Config file present" "docker exec odoo-ce test -f /etc/odoo/odoo.conf"
run_test "5.2. Config file readable" "docker exec odoo-ce cat /etc/odoo/odoo.conf > /dev/null"

# Check for placeholder passwords in config
if docker exec odoo-ce cat /etc/odoo/odoo.conf | grep -q "CHANGE_ME"; then
    echo -e "5.3. No placeholder passwords... ${YELLOW}⚠️  WARN${NC} (found CHANGE_ME)"
    ((WARNINGS++))
else
    echo -e "5.3. No placeholder passwords... ${GREEN}✅ PASS${NC}"
    ((PASSED++))
fi

# Test 6: Resource Usage
echo -e "\n${BLUE}Resource Usage Tests${NC}"

MEM_USAGE=$(docker stats odoo-ce --no-stream --format "{{.MemPerc}}" | sed 's/%//')
CPU_USAGE=$(docker stats odoo-ce --no-stream --format "{{.CPUPerc}}" | sed 's/%//')

echo "6.1. Memory usage: ${MEM_USAGE}%"
if (( $(echo "$MEM_USAGE < 80" | bc -l) )); then
    echo -e "     ${GREEN}✅ PASS${NC} (under 80%)"
    ((PASSED++))
else
    echo -e "     ${YELLOW}⚠️  WARN${NC} (over 80%)"
    ((WARNINGS++))
fi

echo "6.2. CPU usage: ${CPU_USAGE}%"
if (( $(echo "$CPU_USAGE < 90" | bc -l) )); then
    echo -e "     ${GREEN}✅ PASS${NC} (under 90%)"
    ((PASSED++))
else
    echo -e "     ${YELLOW}⚠️  WARN${NC} (over 90%)"
    ((WARNINGS++))
fi

# Test 7: Logs
echo -e "\n${BLUE}Log Analysis Tests${NC}"

ERROR_COUNT=$(docker logs odoo-ce --tail 100 2>&1 | grep -c "ERROR\|CRITICAL" || echo "0")
if [[ "$ERROR_COUNT" -eq 0 ]]; then
    echo -e "7.1. No errors in logs... ${GREEN}✅ PASS${NC}"
    ((PASSED++))
else
    echo -e "7.1. No errors in logs... ${YELLOW}⚠️  WARN${NC} ($ERROR_COUNT errors found)"
    ((WARNINGS++))
    echo "     Recent errors:"
    docker logs odoo-ce --tail 100 2>&1 | grep "ERROR\|CRITICAL" | head -3 | while read -r line; do
        echo "     - ${line:0:80}"
    done
fi

# Check for successful startup message
if docker logs odoo-ce --tail 100 2>&1 | grep -q "HTTP service (werkzeug) running"; then
    echo -e "7.2. HTTP service started... ${GREEN}✅ PASS${NC}"
    ((PASSED++))
else
    echo -e "7.2. HTTP service started... ${RED}❌ FAIL${NC}"
    ((FAILED++))
fi

# Test 8: Network
echo -e "\n${BLUE}Network Tests${NC}"
run_test "8.1. Database reachable from Odoo" "docker exec odoo-ce ping -c 1 db"
run_test "8.2. Port 8069 listening" "netstat -tuln 2>/dev/null | grep -q ':8069' || ss -tuln 2>/dev/null | grep -q ':8069'"

# Test 9: Volumes
echo -e "\n${BLUE}Volume Tests${NC}"
run_test "9.1. Filestore volume mounted" "docker exec odoo-ce test -d /var/lib/odoo"
run_test "9.2. Filestore writable" "docker exec odoo-ce test -w /var/lib/odoo"
run_test "9.3. Log directory exists" "docker exec odoo-ce test -d /var/log/odoo" "no"

# Test 10: Security
echo -e "\n${BLUE}Security Tests${NC}"

# Check if running as root (should not be)
USER=$(docker exec odoo-ce whoami)
if [[ "$USER" == "odoo" ]]; then
    echo -e "10.1. Non-root execution... ${GREEN}✅ PASS${NC} (running as: $USER)"
    ((PASSED++))
else
    echo -e "10.1. Non-root execution... ${RED}❌ FAIL${NC} (running as: $USER)"
    ((FAILED++))
fi

# Check SSL mode in config
if docker exec odoo-ce cat /etc/odoo/odoo.conf | grep -q "db_sslmode.*require"; then
    echo -e "10.2. SSL database connections... ${GREEN}✅ PASS${NC}"
    ((PASSED++))
else
    echo -e "10.2. SSL database connections... ${YELLOW}⚠️  WARN${NC} (not enforced)"
    ((WARNINGS++))
fi

# Summary
echo ""
echo -e "${BLUE}=========================================="
echo "Test Results Summary"
echo -e "==========================================${NC}"
echo -e "${GREEN}Passed:   $PASSED${NC}"
echo -e "${YELLOW}Warnings: $WARNINGS${NC}"
echo -e "${RED}Failed:   $FAILED${NC}"
echo ""

# Overall status
if [[ $FAILED -eq 0 ]]; then
    echo -e "${GREEN}✅ All critical tests passed!${NC}"
    echo ""
    echo "System Status: OPERATIONAL"
    echo ""
    echo "Next Steps:"
    echo "  1. Test in browser: https://erp.insightpulseai.net"
    echo "  2. Login and verify custom modules visible"
    echo "  3. Create a test record to verify database writes"
    echo "  4. Monitor logs: docker logs -f odoo-ce"
    echo ""
    exit 0
else
    echo -e "${RED}❌ $FAILED critical test(s) failed${NC}"
    echo ""
    echo "System Status: DEGRADED"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Check logs: docker logs odoo-ce --tail 100"
    echo "  2. Check container status: docker ps -a"
    echo "  3. Check resources: docker stats odoo-ce"
    echo "  4. Review audit report: ODOO_CE_v0.9.0_SECURITY_AUDIT_REPORT.md"
    echo ""
    exit 1
fi
