#!/usr/bin/env bash
set -euo pipefail

BASE="${BASE:-https://erp.insightpulseai.com}"
C="${C:-odoo-prod}"

echo "== 1) Site reachable =="
curl -fsSI "$BASE/web/login" | head -n 1

echo "== 2) No style compilation banner in HTML (debug=assets) =="
# This catches the exact banner you saw in the UI
curl -fsS "$BASE/web?debug=assets" | grep -qi "style compilation failed" && {
  echo "FAIL: style compilation failed banner present"
  exit 1
} || echo "PASS"

echo "== 3) No recent SCSS import errors in Odoo logs =="
docker logs --tail 500 "$C" 2>/dev/null | grep -Eqi "File to import not found|scss|sass|ir_asset" && {
  echo "WARN: found asset-related log lines (inspect output below)"
  docker logs --tail 200 "$C" | tail -200
} || echo "PASS"

echo "== 4) Odoo is serving (internal) =="
docker exec "$C" bash -lc "curl -fsS http://127.0.0.1:8069/web/login >/dev/null && echo PASS"

echo "== OK =="
