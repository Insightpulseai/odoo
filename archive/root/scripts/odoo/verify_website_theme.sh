#!/usr/bin/env bash
# scripts/odoo/verify_website_theme.sh
#
# Minimal frontend proof: curl the homepage and assert Rozz theme markers.
# Reads expected theme from ssot/website/theme.yaml (theme_module key).
#
# Usage:
#   scripts/odoo/verify_website_theme.sh [BASE_URL]
#
# Default BASE_URL: https://erp.insightpulseai.com
#
# Exit codes:
#   0 = PASS — theme markers detected
#   1 = FAIL — markers absent or curl error
set -euo pipefail

BASE_URL="${1:-https://erp.insightpulseai.com}"
SSOT="${BASH_SOURCE[0]%/scripts*}/ssot/website/theme.yaml"

# Derive theme_module from SSOT (grep-based; no yq dependency)
THEME_MODULE=""
if [[ -f "$SSOT" ]]; then
    THEME_MODULE=$(grep 'theme_module:' "$SSOT" | head -1 | sed 's/.*theme_module: *//' | tr -d '"')
fi
THEME_MODULE="${THEME_MODULE:-cts_theme_rozz}"

echo "Verifying theme: $THEME_MODULE"
echo "Target URL:      $BASE_URL/"

HTML=$(curl -fsSL --max-time 20 "$BASE_URL/" 2>&1) || {
    echo "FAIL: curl error fetching $BASE_URL/"
    exit 1
}

# Markers that prove the Rozz theme is rendering
MARKERS=(
    "about_theme_rozz"
    "services_theme_rozz"
    "${THEME_MODULE}/static"
)

MISSING=()
for m in "${MARKERS[@]}"; do
    if ! echo "$HTML" | grep -qi "$m"; then
        MISSING+=("$m")
    fi
done

if [[ ${#MISSING[@]} -eq 0 ]]; then
    echo "OK: all theme markers detected on homepage"
    exit 0
else
    echo "FAIL: missing markers: ${MISSING[*]}"
    exit 1
fi
