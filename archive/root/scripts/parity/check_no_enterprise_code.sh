#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# Enterprise Code Compliance Check
# =============================================================================
# Purpose: Verify no Odoo Enterprise Edition code is present
# Exit Code: 0 = compliant, 1 = violations found
# =============================================================================

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo ".")"
cd "$REPO_ROOT"

echo "=== Odoo Enterprise Code Compliance Check ==="
echo "Repository: $REPO_ROOT"
echo "Date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo

VIOLATIONS=0

# Check 1: No Enterprise imports
echo "--- Check 1: No Enterprise imports ---"
if grep -r "from odoo.addons.enterprise" addons/ 2>/dev/null | grep -v "\.pyc"; then
    echo "❌ FAIL: Found Enterprise imports"
    VIOLATIONS=$((VIOLATIONS + 1))
else
    echo "✅ PASS: No Enterprise imports"
fi
echo

# Check 2: No EE web modules
echo "--- Check 2: No Enterprise web modules ---"
if grep -r "odoo.addons.web_enterprise" addons/ 2>/dev/null | grep -v "\.pyc"; then
    echo "❌ FAIL: Found web_enterprise references"
    VIOLATIONS=$((VIOLATIONS + 1))
else
    echo "✅ PASS: No web_enterprise modules"
fi
echo

# Check 3: No IAP dependencies
echo "--- Check 3: No IAP dependencies ---"
if grep -r "iap\.account" addons/ipai/ 2>/dev/null | grep -v "\.pyc" | grep -v "Binary"; then
    echo "❌ FAIL: Found IAP account references in IPAI modules"
    VIOLATIONS=$((VIOLATIONS + 1))
else
    echo "✅ PASS: No IAP dependencies in IPAI modules"
    echo "ℹ️  Note: OCA iap_alternative_provider module provides IAP replacement (safe)"
fi
echo

# Check 4: No Odoo.com services
echo "--- Check 4: No Odoo.com subscription services ---"
if grep -r "services\.odoo\.com" addons/ 2>/dev/null | grep -v "\.pyc"; then
    echo "❌ FAIL: Found Odoo.com service endpoints"
    VIOLATIONS=$((VIOLATIONS + 1))
else
    echo "✅ PASS: No Odoo.com services"
fi
echo

# Check 5: No Enterprise dependencies in manifests
echo "--- Check 5: No Enterprise module dependencies ---"
if find addons/ipai -name "__manifest__.py" -type f -exec grep -l '"enterprise"' {} \; | while read file; do
    # Exclude ipai_enterprise_bridge itself and summary fields
    if ! grep -q "ipai_enterprise_bridge" "$file" && grep '"enterprise"' "$file" | grep -v "summary" | grep -v "description"; then
        echo "Found in: $file"
    fi
done | grep .; then
    echo "❌ FAIL: Found Enterprise dependencies in manifests"
    VIOLATIONS=$((VIOLATIONS + 1))
else
    echo "✅ PASS: No Enterprise dependencies"
fi
echo

# Check 6: License headers present
echo "--- Check 6: License headers in Python files ---"
MISSING_HEADERS=0
while IFS= read -r file; do
    if ! grep -q "License.*LGPL\|License.*AGPL" "$file"; then
        echo "Missing header: $file"
        MISSING_HEADERS=$((MISSING_HEADERS + 1))
    fi
done < <(find addons/ipai -name "*.py" -type f ! -name "__init__.py")

if [ $MISSING_HEADERS -gt 0 ]; then
    echo "❌ FAIL: $MISSING_HEADERS files missing license headers"
    VIOLATIONS=$((VIOLATIONS + 1))
else
    echo "✅ PASS: All files have license headers"
fi
echo

# Check 7: Verify Odoo 18 CE pin
echo "--- Check 7: Odoo CE version pin ---"
if [ -f "addons/oca/ODOO_PIN.txt" ]; then
    ODOO_VERSION=$(grep -E "^[0-9]+\.[0-9]+" addons/oca/ODOO_PIN.txt | head -1)
    if [ "$ODOO_VERSION" = "18.0" ]; then
        echo "✅ PASS: Odoo pinned to 18.0 CE"
    else
        echo "❌ FAIL: Unexpected Odoo version: $ODOO_VERSION"
        VIOLATIONS=$((VIOLATIONS + 1))
    fi
else
    echo "⚠️  WARN: ODOO_PIN.txt not found"
fi
echo

# Summary
echo "=== Compliance Check Summary ==="
if [ $VIOLATIONS -eq 0 ]; then
    echo "✅ COMPLIANT: No Enterprise code violations detected"
    echo "Status: Safe for production deployment"
    exit 0
else
    echo "❌ NON-COMPLIANT: $VIOLATIONS violation(s) found"
    echo "Status: Fix violations before deployment"
    exit 1
fi
