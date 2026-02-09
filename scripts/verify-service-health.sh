#!/usr/bin/env bash
set -euo pipefail

DOMAIN="insightpulseai.com"

echo "=== Service Health Checks ==="
echo ""

# Function to check HTTP endpoint
check_endpoint() {
  local name="$1"
  local url="$2"
  local expect_code="${3:-200}"

  echo -n "  $name ($url) ... "
  status=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$url" || echo "TIMEOUT")

  if [[ "$status" == "$expect_code" ]]; then
    echo "✅ $status"
  else
    echo "❌ $status (expected $expect_code)"
  fi
}

# ERP
echo "1. ERP (erp.$DOMAIN):"
check_endpoint "HTTP→HTTPS redirect" "http://erp.$DOMAIN" "301"
check_endpoint "HTTPS login page" "https://erp.$DOMAIN/web/login" "200"
echo ""

# n8n
echo "2. n8n (n8n.$DOMAIN):"
check_endpoint "Health check" "https://n8n.$DOMAIN/healthz" "200"
echo ""

# OCR
echo "3. OCR (ocr.$DOMAIN):"
check_endpoint "Health check" "http://ocr.$DOMAIN/health" "200"
echo ""

# Auth
echo "4. Auth (auth.$DOMAIN):"
check_endpoint "OIDC discovery" "https://auth.$DOMAIN/.well-known/openid-configuration" "200"
echo ""

# MCP (may not exist yet)
echo "5. MCP (mcp.$DOMAIN):"
check_endpoint "Health check" "https://mcp.$DOMAIN/healthz" "200"
echo ""

# Superset (may not exist yet)
echo "6. Superset (superset.$DOMAIN):"
check_endpoint "Health check" "https://superset.$DOMAIN/health" "200"
echo ""

echo "=== Health Checks Complete ==="
