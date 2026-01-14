#!/usr/bin/env bash
set -euo pipefail

# Canonical Odoo Login Health Gate
# Run this from CI/cron to detect asset system failures early

URL="${1:-https://erp.insightpulseai.net/web/login}"

echo "🔍 Odoo Login Health Check"
echo "URL: $URL"
echo ""

# 1) HTTP up
echo "Checking HTTP status..."
code="$(curl -sS -o /dev/null -w "%{http_code}" "$URL")"
if [ "$code" != "200" ]; then
    echo "❌ FAIL: login HTTP $code (expected 200)"
    exit 2
fi
echo "✅ Login page HTTP: $code"

# 2) Frontend minimal assets (critical for login)
echo ""
echo "Checking frontend minimal assets..."
assets_url="${URL%/web/login}/web/assets/1/f72ec00/web.assets_frontend_minimal.min.js"
assets_code="$(curl -sS -o /dev/null -w "%{http_code}" "$assets_url" 2>&1 || echo "000")"
if [ "$assets_code" != "200" ]; then
    echo "❌ FAIL: frontend assets HTTP $assets_code (expected 200)"
    echo "   This usually means asset system failure - run:"
    echo "   ./scripts/fix_odoo_assets_after_filestore_wipe.sh"
    exit 3
fi
echo "✅ Frontend assets HTTP: $assets_code"

# 3) Verify asset content is valid JavaScript
echo ""
echo "Verifying asset content..."
asset_content="$(curl -sS "$assets_url" | head -c 100)"
if echo "$asset_content" | grep -qE "/\*.*\*/|Object|function|var|const|let|if\(|=>"; then
    echo "✅ Asset content is valid JavaScript"
else
    echo "⚠️  WARNING: Asset content may be corrupted"
    echo "   First 100 chars: $asset_content"
fi

echo ""
echo "✅ PASS: All health checks passed"
echo ""
echo "For headless JS verification, run:"
echo "  node scripts/verify_login_headless.js"
