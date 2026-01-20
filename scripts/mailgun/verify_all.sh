#!/usr/bin/env bash
# Complete Mailgun Verification Suite for InsightPulse AI
# Domain: mg.insightpulseai.net
#
# Usage:
#   # DNS verification only (no credentials needed)
#   ./scripts/mailgun/verify_all.sh --dns-only
#
#   # Full verification (requires MAILGUN_API_KEY)
#   export MAILGUN_API_KEY=key-xxxxx
#   ./scripts/mailgun/verify_all.sh
#
#   # Full verification + test email
#   ./scripts/mailgun/verify_all.sh --test-email recipient@example.com

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DNS_ONLY=false
TEST_EMAIL=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dns-only)
            DNS_ONLY=true
            shift
            ;;
        --test-email)
            TEST_EMAIL="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--dns-only] [--test-email recipient@example.com]"
            exit 1
            ;;
    esac
done

TIMESTAMP=$(date +%Y%m%d-%H%M)
EVIDENCE_DIR="docs/evidence/${TIMESTAMP}/mailgun"

echo "=============================================="
echo "Mailgun Complete Verification Suite"
echo "=============================================="
echo "Timestamp: $(date -Iseconds)"
echo "Evidence Dir: ${EVIDENCE_DIR}"
echo ""

# Track overall status
declare -A step_status
overall_status="PASS"

# Step 1: DNS Verification
echo "╔══════════════════════════════════════════╗"
echo "║ Step 1: DNS Verification                 ║"
echo "╚══════════════════════════════════════════╝"
if "${SCRIPT_DIR}/verify_dns.sh"; then
    step_status["dns"]="PASS"
    echo "✅ DNS verification passed"
else
    step_status["dns"]="FAIL"
    overall_status="FAIL"
    echo "❌ DNS verification failed"
fi
echo ""

if [ "$DNS_ONLY" = true ]; then
    echo "=============================================="
    echo "DNS-only mode. Skipping remaining steps."
    echo "=============================================="
    exit $([ "${overall_status}" = "PASS" ] && echo 0 || echo 1)
fi

# Step 2: SMTP Test
echo "╔══════════════════════════════════════════╗"
echo "║ Step 2: SMTP Connection Test             ║"
echo "╚══════════════════════════════════════════╝"
if "${SCRIPT_DIR}/test_smtp.sh"; then
    step_status["smtp"]="PASS"
    echo "✅ SMTP test passed"
else
    step_status["smtp"]="FAIL"
    overall_status="FAIL"
    echo "❌ SMTP test failed"
fi
echo ""

# Step 3: Webhook Setup (requires API key)
echo "╔══════════════════════════════════════════╗"
echo "║ Step 3: Webhook Configuration            ║"
echo "╚══════════════════════════════════════════╝"
if [ -n "${MAILGUN_API_KEY:-}" ]; then
    if "${SCRIPT_DIR}/setup_webhooks.sh"; then
        step_status["webhooks"]="PASS"
        echo "✅ Webhook setup passed"
    else
        step_status["webhooks"]="FAIL"
        overall_status="FAIL"
        echo "❌ Webhook setup failed"
    fi
else
    step_status["webhooks"]="SKIP"
    echo "⏭️  Skipped (MAILGUN_API_KEY not set)"
fi
echo ""

# Step 4: Test Email (optional)
echo "╔══════════════════════════════════════════╗"
echo "║ Step 4: Test Email                       ║"
echo "╚══════════════════════════════════════════╝"
if [ -n "$TEST_EMAIL" ]; then
    if [ -n "${MAILGUN_API_KEY:-}" ]; then
        if "${SCRIPT_DIR}/send_test_email.sh" "$TEST_EMAIL"; then
            step_status["email"]="PASS"
            echo "✅ Test email sent"
        else
            step_status["email"]="FAIL"
            overall_status="FAIL"
            echo "❌ Test email failed"
        fi
    else
        step_status["email"]="SKIP"
        echo "⏭️  Skipped (MAILGUN_API_KEY not set)"
    fi
else
    step_status["email"]="SKIP"
    echo "⏭️  Skipped (no --test-email provided)"
fi
echo ""

# Generate summary report
echo "=============================================="
echo "VERIFICATION SUMMARY"
echo "=============================================="
echo ""
echo "| Step | Status |"
echo "|------|--------|"
echo "| DNS  | ${step_status["dns"]:-UNKNOWN} |"
echo "| SMTP | ${step_status["smtp"]:-UNKNOWN} |"
echo "| Webhooks | ${step_status["webhooks"]:-UNKNOWN} |"
echo "| Test Email | ${step_status["email"]:-UNKNOWN} |"
echo ""
echo "Overall Status: ${overall_status}"
echo ""

# Generate summary JSON
cat > "${EVIDENCE_DIR}/verification_summary.json" << EOF
{
  "timestamp": "$(date -Iseconds)",
  "domain": "${MAILGUN_DOMAIN:-mg.insightpulseai.net}",
  "steps": {
    "dns": "${step_status["dns"]:-unknown}",
    "smtp": "${step_status["smtp"]:-unknown}",
    "webhooks": "${step_status["webhooks"]:-unknown}",
    "test_email": "${step_status["email"]:-unknown}"
  },
  "overall_status": "${overall_status}",
  "evidence_dir": "${EVIDENCE_DIR}"
}
EOF

echo "📄 Summary written to: ${EVIDENCE_DIR}/verification_summary.json"
echo ""

if [ "${overall_status}" = "PASS" ]; then
    echo "✅ All verification steps passed!"
    exit 0
else
    echo "❌ Some verification steps failed. Review evidence files for details."
    exit 1
fi
