#!/bin/bash
# Health check for all services

set -e

echo "=== ipai-ops-stack Health Check ==="
echo ""

PASS=0
FAIL=0

check_service() {
    local name="$1"
    local url="$2"
    local expected="${3:-200}"

    printf "%-20s " "$name:"

    response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")

    if [ "$response" = "$expected" ]; then
        echo "✓ OK ($response)"
        ((PASS++))
    else
        echo "✗ FAIL (got $response, expected $expected)"
        ((FAIL++))
    fi
}

# Check each service
check_service "Mattermost" "https://chat.insightpulseai.com/api/v4/system/ping"
check_service "Focalboard" "https://boards.insightpulseai.com/api/v2/ping"
check_service "n8n" "https://n8n.insightpulseai.com/healthz"
check_service "Superset" "https://superset.insightpulseai.com/health"

echo ""
echo "=== Summary ==="
echo "Passed: $PASS"
echo "Failed: $FAIL"

if [ "$FAIL" -gt 0 ]; then
    exit 1
fi
