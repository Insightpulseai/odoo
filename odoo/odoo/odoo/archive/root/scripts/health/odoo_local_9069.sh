#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:9069}"

echo "=== Odoo Local 9069 Health Check ==="
echo "Target: ${BASE_URL}"
echo

# 1) Check login page HTML
echo "--- [1/4] /web/login HTML ---"
status_html=$(curl -s -o /tmp/odoo_9069_login.html -w "%{http_code}" "${BASE_URL}/web/login" || echo "000")
if [ "$status_html" != "200" ]; then
  echo "❌ /web/login returned HTTP $status_html"
  exit 1
fi
echo "✅ /web/login HTTP 200"

# Verify Odoo marker
if ! grep -q 'meta name="generator" content="Odoo"' /tmp/odoo_9069_login.html; then
  echo "❌ /web/login is not Odoo HTML (missing generator meta)"
  exit 1
fi
echo "✅ Detected Odoo HTML (generator=Odoo)"

# 2) Auto-discover a frontend CSS asset from the login page
echo
echo "--- [2/4] Discover CSS asset from HTML ---"
CSS_PATH="${CSS_PATH:-}"

if [ -z "${CSS_PATH}" ]; then
  # Try to extract /web/assets/...css from HTML
  CSS_PATH=$(grep -oE 'href="(/web/assets/[^"]+\.css)"' /tmp/odoo_9069_login.html | head -n 1 | sed 's/href="//; s/"$//') || true
fi

if [ -z "${CSS_PATH}" ]; then
  echo "⚠️ Could not auto-detect CSS_PATH from HTML"
  echo "   You can override via: CSS_PATH=/web/assets/1/<hash>/web.assets_frontend.min.css scripts/health/odoo_local_9069.sh"
  # Not fatal for overall health: HTML is OK, CSS path may be theme-specific
else
  echo "✅ Auto-detected CSS asset: ${CSS_PATH}"
fi

# 3) If we have a CSS path, validate it
if [ -n "${CSS_PATH}" ]; then
  echo
  echo "--- [3/4] CSS HTTP check ---"
  status_css=$(curl -s -o /tmp/odoo_9069_frontend.css -w "%{http_code}" "${BASE_URL}${CSS_PATH}" || echo "000")
  if [ "$status_css" != "200" ]; then
    echo "❌ CSS asset returned HTTP $status_css"
    echo "   URL: ${BASE_URL}${CSS_PATH}"
    exit 1
  fi
  echo "✅ CSS asset HTTP 200 at ${BASE_URL}${CSS_PATH}"

  echo
  echo "--- [4/4] CSS sanity ---"
  if [ ! -s /tmp/odoo_9069_frontend.css ]; then
    echo "❌ CSS file is empty"
    exit 1
  fi

  if ! head -n 20 /tmp/odoo_9069_frontend.css | grep -q '{'; then
    echo "⚠️ CSS content unusual (no '{' in first 20 lines) – manual check recommended"
  else
    echo "✅ CSS content looks normal"
  fi
else
  echo
  echo "--- [3/4] CSS check skipped (no CSS_PATH) ---"
fi

echo
echo "=== RESULT: Odoo 9069 HEALTHY (HTML OK, CSS checked if available) ==="
echo "No restart required. Any odd look is likely browser cache or theme content."
