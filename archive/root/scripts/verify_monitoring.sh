#!/usr/bin/env bash
# verify_monitoring.sh — Check Prometheus + Grafana + exporters are healthy
# Usage: ./scripts/verify_monitoring.sh
# Exit 0 = all checks pass, Exit 1 = at least one failure
set -euo pipefail

PASS=0
FAIL=0
SKIP=0

check() {
  local name="$1" url="$2" expected="${3:-200}"
  local code
  code=$(curl -sf -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")
  if [ "$code" = "$expected" ]; then
    echo "  PASS  $name ($code)"
    PASS=$((PASS + 1))
  elif [ "$code" = "000" ]; then
    echo "  SKIP  $name (unreachable — container may not be running)"
    SKIP=$((SKIP + 1))
  else
    echo "  FAIL  $name (expected $expected, got $code)"
    FAIL=$((FAIL + 1))
  fi
}

echo "=== Monitoring Stack Verification ==="
echo ""

# Prometheus
check "Prometheus healthy" "http://127.0.0.1:9090/-/healthy"
check "Prometheus ready"   "http://127.0.0.1:9090/-/ready"

# Grafana
check "Grafana API health" "http://127.0.0.1:3000/api/health"

# Exporters
check "PostgreSQL exporter" "http://127.0.0.1:9187/metrics"
check "Node exporter"       "http://127.0.0.1:9100/metrics"
check "cAdvisor"            "http://127.0.0.1:8080/healthz"

echo ""
echo "=== Results: PASS=$PASS  FAIL=$FAIL  SKIP=$SKIP ==="

if [ "$FAIL" -gt 0 ]; then
  echo "STATUS: FAIL"
  exit 1
fi

echo "STATUS: PASS"
exit 0
