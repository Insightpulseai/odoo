#!/usr/bin/env bash
# =============================================================================
# Verify that ipai_website_coming_soon is serving the homepage.
# Checks: HTTP 200, "Pulsating Soon" marker, "Coming soon" heading.
# =============================================================================
set -euo pipefail

: "${SITE_URL:=http://localhost:8069}"
PASS=0
FAIL=0

check() {
    local label="$1" pattern="$2"
    if curl -fsSL "$SITE_URL" 2>/dev/null | grep -qi "$pattern"; then
        echo "  PASS: $label"
        ((PASS++))
    else
        echo "  FAIL: $label (pattern '$pattern' not found)"
        ((FAIL++))
    fi
}

echo "Verifying Coming Soon page at $SITE_URL ..."
check "Pulsating Soon kicker" "Pulsating Soon"
check "Coming soon heading"   "Coming soon"
check "Pulser dot element"    "ipai-cs-dot"
check "Request a Demo CTA"    "Request a Demo"

echo ""
echo "Results: $PASS passed, $FAIL failed"
[[ $FAIL -eq 0 ]] && echo "OK: All checks passed." || { echo "FAIL: Some checks failed."; exit 1; }
