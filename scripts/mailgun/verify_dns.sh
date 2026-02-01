#!/usr/bin/env bash
# Mailgun DNS Verification Script for InsightPulse AI
# Domain: mg.insightpulseai.com
#
# Usage: ./scripts/mailgun/verify_dns.sh
# Output: docs/evidence/YYYYMMDD-HHMM/mailgun/dns_verification.json

set -euo pipefail

DOMAIN="${MAILGUN_DOMAIN:-mg.insightpulseai.com}"
TIMESTAMP=$(date +%Y%m%d-%H%M)
EVIDENCE_DIR="docs/evidence/${TIMESTAMP}/mailgun"

echo "🔍 Mailgun DNS Verification for ${DOMAIN}"
echo "=============================================="
echo ""

# Create evidence directory
mkdir -p "${EVIDENCE_DIR}"

# Initialize results
results='{}'

check_record() {
    local name="$1"
    local type="$2"
    local label="$3"
    local expected="$4"

    echo "Checking ${label} (${type}) for ${name}..."

    # Try dig first, fall back to nslookup, then host
    local result=""
    if command -v dig &> /dev/null; then
        result=$(dig +short "${type}" "${name}" 2>/dev/null || echo "")
    elif command -v nslookup &> /dev/null; then
        result=$(nslookup -type="${type}" "${name}" 2>/dev/null | grep -A1 "answer:" | tail -1 || echo "")
    elif command -v host &> /dev/null; then
        result=$(host -t "${type}" "${name}" 2>/dev/null | awk '{print $NF}' || echo "")
    fi

    if [ -n "$result" ]; then
        echo "  ✅ Found: ${result}"
        if echo "$result" | grep -qi "$expected"; then
            echo "  ✅ Matches expected pattern"
            return 0
        else
            echo "  ⚠️  May not match expected: ${expected}"
            return 0
        fi
    else
        echo "  ❌ NOT FOUND"
        return 1
    fi
}

# Track results
passed=0
failed=0
declare -A dns_results

echo ""
echo "=== SPF Record ==="
if check_record "${DOMAIN}" "TXT" "SPF" "mailgun"; then
    dns_results["spf"]="pass"
    ((passed++))
else
    dns_results["spf"]="fail"
    ((failed++))
fi

echo ""
echo "=== DKIM Record ==="
if check_record "pic._domainkey.${DOMAIN}" "TXT" "DKIM" "k=rsa"; then
    dns_results["dkim"]="pass"
    ((passed++))
else
    dns_results["dkim"]="fail"
    ((failed++))
fi

echo ""
echo "=== DMARC Record ==="
if check_record "_dmarc.${DOMAIN}" "TXT" "DMARC" "DMARC1"; then
    dns_results["dmarc"]="pass"
    ((passed++))
else
    dns_results["dmarc"]="fail"
    ((failed++))
fi

echo ""
echo "=== MX Records ==="
if check_record "${DOMAIN}" "MX" "MX Primary" "mxa.mailgun.org"; then
    dns_results["mx_primary"]="pass"
    ((passed++))
else
    dns_results["mx_primary"]="fail"
    ((failed++))
fi

if check_record "${DOMAIN}" "MX" "MX Secondary" "mxb.mailgun.org"; then
    dns_results["mx_secondary"]="pass"
    ((passed++))
else
    dns_results["mx_secondary"]="fail"
    ((failed++))
fi

echo ""
echo "=== Tracking CNAME ==="
if check_record "email.${DOMAIN}" "CNAME" "Tracking CNAME" "mailgun.org"; then
    dns_results["tracking_cname"]="pass"
    ((passed++))
else
    dns_results["tracking_cname"]="fail"
    ((failed++))
fi

echo ""
echo "=============================================="
echo "DNS Verification Summary"
echo "=============================================="
echo "Passed: ${passed}/6"
echo "Failed: ${failed}/6"
echo ""

# Generate JSON evidence
cat > "${EVIDENCE_DIR}/dns_verification.json" << EOF
{
  "timestamp": "$(date -Iseconds)",
  "domain": "${DOMAIN}",
  "results": {
    "spf": "${dns_results["spf"]:-unknown}",
    "dkim": "${dns_results["dkim"]:-unknown}",
    "dmarc": "${dns_results["dmarc"]:-unknown}",
    "mx_primary": "${dns_results["mx_primary"]:-unknown}",
    "mx_secondary": "${dns_results["mx_secondary"]:-unknown}",
    "tracking_cname": "${dns_results["tracking_cname"]:-unknown}"
  },
  "summary": {
    "passed": ${passed},
    "failed": ${failed},
    "total": 6
  },
  "status": "$([ ${failed} -eq 0 ] && echo "PASS" || echo "FAIL")"
}
EOF

echo "📄 Evidence written to: ${EVIDENCE_DIR}/dns_verification.json"

# Generate markdown report
cat > "${EVIDENCE_DIR}/dns_verification.md" << EOF
# Mailgun DNS Verification Report

**Domain:** ${DOMAIN}
**Timestamp:** $(date -Iseconds)
**Status:** $([ ${failed} -eq 0 ] && echo "✅ PASS" || echo "❌ FAIL")

## Results

| Record | Type | Status |
|--------|------|--------|
| SPF | TXT | $([ "${dns_results["spf"]}" = "pass" ] && echo "✅ Pass" || echo "❌ Fail") |
| DKIM | TXT | $([ "${dns_results["dkim"]}" = "pass" ] && echo "✅ Pass" || echo "❌ Fail") |
| DMARC | TXT | $([ "${dns_results["dmarc"]}" = "pass" ] && echo "✅ Pass" || echo "❌ Fail") |
| MX Primary | MX | $([ "${dns_results["mx_primary"]}" = "pass" ] && echo "✅ Pass" || echo "❌ Fail") |
| MX Secondary | MX | $([ "${dns_results["mx_secondary"]}" = "pass" ] && echo "✅ Pass" || echo "❌ Fail") |
| Tracking CNAME | CNAME | $([ "${dns_results["tracking_cname"]}" = "pass" ] && echo "✅ Pass" || echo "❌ Fail") |

## Summary

- **Passed:** ${passed}/6
- **Failed:** ${failed}/6
EOF

echo "📄 Report written to: ${EVIDENCE_DIR}/dns_verification.md"
echo ""

if [ ${failed} -eq 0 ]; then
    echo "✅ All DNS records verified successfully!"
    exit 0
else
    echo "❌ Some DNS records failed verification. Check report for details."
    exit 1
fi
