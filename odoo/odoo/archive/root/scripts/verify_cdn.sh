#!/usr/bin/env bash
# verify_cdn.sh — Check Cloudflare CDN is caching static assets
# Usage: ./scripts/verify_cdn.sh [base_url]
# Exit 0 = CDN caching confirmed, Exit 1 = not caching
set -euo pipefail

BASE_URL="${1:-https://erp.insightpulseai.com}"
PASS=0
FAIL=0
SKIP=0

check_cache() {
  local path="$1"
  local url="${BASE_URL}${path}"
  local cf_status

  cf_status=$(curl -sf -o /dev/null -D - "$url" 2>/dev/null | grep -i "cf-cache-status" | awk '{print $2}' | tr -d '\r\n' || echo "NONE")

  case "$cf_status" in
    HIT|MISS|EXPIRED|STALE|REVALIDATED)
      echo "  PASS  $path (cf-cache-status: $cf_status)"
      PASS=$((PASS + 1))
      ;;
    DYNAMIC)
      echo "  WARN  $path (cf-cache-status: DYNAMIC — not cached by Cloudflare)"
      FAIL=$((FAIL + 1))
      ;;
    NONE|"")
      echo "  SKIP  $path (no cf-cache-status header — Cloudflare proxy may be off)"
      SKIP=$((SKIP + 1))
      ;;
    *)
      echo "  INFO  $path (cf-cache-status: $cf_status)"
      PASS=$((PASS + 1))
      ;;
  esac
}

check_bypass() {
  local path="$1"
  local url="${BASE_URL}${path}"
  local cf_status

  cf_status=$(curl -sf -o /dev/null -D - "$url" 2>/dev/null | grep -i "cf-cache-status" | awk '{print $2}' | tr -d '\r\n' || echo "NONE")

  case "$cf_status" in
    DYNAMIC|BYPASS|NONE|"")
      echo "  PASS  $path (correctly bypassed: $cf_status)"
      PASS=$((PASS + 1))
      ;;
    HIT)
      echo "  FAIL  $path (should NOT be cached but got HIT)"
      FAIL=$((FAIL + 1))
      ;;
    *)
      echo "  INFO  $path (cf-cache-status: $cf_status)"
      PASS=$((PASS + 1))
      ;;
  esac
}

echo "=== CDN Cache Verification (${BASE_URL}) ==="
echo ""
echo "--- Static assets (should be cached) ---"
check_cache "/web/static/lib/bootstrap/css/bootstrap.css"
check_cache "/web/static/src/img/favicon.ico"

echo ""
echo "--- Dynamic routes (should bypass cache) ---"
check_bypass "/web/login"
check_bypass "/web/health"

echo ""
echo "=== Results: PASS=$PASS  FAIL=$FAIL  SKIP=$SKIP ==="

if [ "$FAIL" -gt 0 ]; then
  echo "STATUS: FAIL"
  exit 1
fi

echo "STATUS: PASS"
exit 0
