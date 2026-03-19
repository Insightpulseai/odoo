#!/usr/bin/env bash
# scripts/ci/check_prod_assets.sh
# Verify Odoo production asset bundles serve correctly with compression.
# Usage: ./scripts/ci/check_prod_assets.sh [BASE_URL]
# Exit: 0 if all assets pass, 1 if any fail.
set -euo pipefail

BASE_URL="${1:-https://erp.insightpulseai.com}"
FAIL=0

echo "Checking asset bundles at ${BASE_URL}"
echo "---"

# Extract all asset URLs from the login page
ASSETS=$(curl -sf "${BASE_URL}/web/login" | grep -oE '(src|href)="/web/assets/[^"]*"' | sed 's/.*"\(.*\)"/\1/' | sort -u)

if [ -z "$ASSETS" ]; then
  echo "FAIL: No asset URLs found on login page"
  exit 1
fi

for asset in $ASSETS; do
  # Test 1: No compression (baseline)
  STATUS_RAW=$(curl -sf -o /dev/null -w "%{http_code}" "${BASE_URL}${asset}" 2>/dev/null || echo "000")

  # Test 2: With gzip (what browsers send)
  STATUS_GZ=$(curl -sf -H "Accept-Encoding: gzip, deflate, br" -o /dev/null -w "%{http_code}" "${BASE_URL}${asset}" 2>/dev/null || echo "000")

  LABEL="$(basename "$asset")"

  if [ "$STATUS_RAW" != "200" ]; then
    echo "FAIL: ${LABEL} -> HTTP ${STATUS_RAW} (no compression)"
    FAIL=1
  elif [ "$STATUS_GZ" != "200" ]; then
    echo "FAIL: ${LABEL} -> HTTP ${STATUS_GZ} (with Accept-Encoding: gzip,br)"
    echo "      Raw request returns HTTP ${STATUS_RAW} but compressed request fails."
    echo "      This indicates missing pre-compressed asset variants in ir_attachment."
    echo "      Fix: clear ir_attachment asset cache and let Odoo regenerate."
    FAIL=1
  else
    # Get compressed transfer size
    SIZE=$(curl -sf -H "Accept-Encoding: gzip, deflate, br" -o /dev/null -w "%{size_download}" "${BASE_URL}${asset}" 2>/dev/null || echo "0")
    echo "PASS: ${LABEL} -> HTTP 200 (compressed: ${SIZE} bytes)"
  fi
done

echo "---"
if [ "$FAIL" -eq 0 ]; then
  echo "All asset bundles pass."
else
  echo "Some asset bundles FAILED. See details above."
fi

exit $FAIL
