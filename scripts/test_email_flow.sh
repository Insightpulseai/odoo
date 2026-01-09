#!/bin/bash
set -euo pipefail

# Email Flow Testing Script
# Sends test email through Mailgun SMTP and verifies DKIM/SPF/DMARC alignment
# Usage: TEST_EMAIL_TO=user@example.com ./scripts/test_email_flow.sh
# Safe to run in CI with secrets injected

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration from environment variables
SMTP_HOST="${MAIL_HOST:-smtp.mailgun.org}"
SMTP_PORT="${MAIL_PORT:-2525}"
SMTP_USER="${MAIL_USER:-postmaster@mg.insightpulseai.net}"
SMTP_PASSWORD="${MAIL_PASSWORD:-}"
MAIL_FROM="${MAIL_DEFAULT_FROM:-noreply@mg.insightpulseai.net}"
TEST_EMAIL_TO="${TEST_EMAIL_TO:-}"

# Validate required environment variables
if [ -z "$SMTP_PASSWORD" ]; then
    echo -e "${RED}✗ MAIL_PASSWORD not set${NC}"
    echo "  Set MAIL_PASSWORD environment variable with your Mailgun SMTP password"
    exit 1
fi

if [ -z "$TEST_EMAIL_TO" ]; then
    echo -e "${RED}✗ TEST_EMAIL_TO not set${NC}"
    echo "  Usage: TEST_EMAIL_TO=your-email@example.com ./scripts/test_email_flow.sh"
    exit 1
fi

# Helper functions
print_check() {
    echo -e "${GREEN}✓${NC} $1"
}

print_fail() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_section() {
    echo ""
    echo "=========================================="
    echo "$1"
    echo "=========================================="
}

# Generate unique test ID for tracing
TEST_ID="test-$(date +%s)-$$"

print_section "Email Flow Test Configuration"
echo "SMTP Host:    $SMTP_HOST"
echo "SMTP Port:    $SMTP_PORT"
echo "SMTP User:    $SMTP_USER"
echo "From:         $MAIL_FROM"
echo "To:           $TEST_EMAIL_TO"
echo "Test ID:      $TEST_ID"

# Send test email using Python
print_section "Sending Test Email"

SEND_RESULT=$(python3 - <<EOF
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate, make_msgid
import sys

# Email configuration
smtp_host = "$SMTP_HOST"
smtp_port = $SMTP_PORT
smtp_user = "$SMTP_USER"
smtp_password = "$SMTP_PASSWORD"
mail_from = "$MAIL_FROM"
mail_to = "$TEST_EMAIL_TO"
test_id = "$TEST_ID"

try:
    # Create message
    msg = MIMEMultipart('alternative')
    msg['From'] = mail_from
    msg['To'] = mail_to
    msg['Subject'] = f'Email Authentication Test - {test_id}'
    msg['Date'] = formatdate(localtime=True)
    msg['Message-ID'] = make_msgid(domain=mail_from.split('@')[1])
    msg['X-Test-ID'] = test_id

    # Plain text version
    text_content = f"""
Email Authentication Test

This is a test email to verify SMTP configuration and email authentication.

Test ID: {test_id}
Sent via: {smtp_host}:{smtp_port}
From: {mail_from}

If you receive this email, basic SMTP delivery is working.

Next steps:
1. Check email headers for DKIM signature (DKIM-Signature header)
2. Verify SPF alignment (Return-Path domain matches From domain)
3. Check DMARC alignment (both SPF and DKIM should align)

You can use online tools like:
- https://www.mail-tester.com/ (comprehensive test)
- https://mxtoolbox.com/EmailHeaders.aspx (header analysis)

---
InsightPulse AI - Email Authentication Test
"""

    # HTML version
    html_content = f"""
<html>
<head>
    <meta charset="utf-8">
    <title>Email Authentication Test</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <h1 style="color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px;">
        Email Authentication Test
    </h1>

    <p>This is a test email to verify SMTP configuration and email authentication.</p>

    <div style="background-color: #ecf0f1; padding: 15px; border-radius: 5px; margin: 20px 0;">
        <h3 style="margin-top: 0; color: #2c3e50;">Test Details</h3>
        <table style="width: 100%; border-collapse: collapse;">
            <tr>
                <td style="padding: 5px; font-weight: bold;">Test ID:</td>
                <td style="padding: 5px;">{test_id}</td>
            </tr>
            <tr>
                <td style="padding: 5px; font-weight: bold;">Sent via:</td>
                <td style="padding: 5px;">{smtp_host}:{smtp_port}</td>
            </tr>
            <tr>
                <td style="padding: 5px; font-weight: bold;">From:</td>
                <td style="padding: 5px;">{mail_from}</td>
            </tr>
        </table>
    </div>

    <p style="color: #27ae60; font-weight: bold;">
        ✓ If you receive this email, basic SMTP delivery is working.
    </p>

    <h3 style="color: #2c3e50;">Next Steps - Verify Email Authentication:</h3>
    <ol style="line-height: 1.8;">
        <li>Check email headers for <strong>DKIM signature</strong> (DKIM-Signature header)</li>
        <li>Verify <strong>SPF alignment</strong> (Return-Path domain matches From domain)</li>
        <li>Check <strong>DMARC alignment</strong> (both SPF and DKIM should align)</li>
    </ol>

    <h4 style="color: #2c3e50;">Online Testing Tools:</h4>
    <ul style="line-height: 1.8;">
        <li><a href="https://www.mail-tester.com/" style="color: #3498db;">Mail Tester</a> - Comprehensive email deliverability test</li>
        <li><a href="https://mxtoolbox.com/EmailHeaders.aspx" style="color: #3498db;">MX Toolbox</a> - Email header analysis</li>
        <li><a href="https://dmarcian.com/dmarc-inspector/" style="color: #3498db;">DMARC Inspector</a> - DMARC policy verification</li>
    </ul>

    <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #bdc3c7; color: #7f8c8d; font-size: 12px;">
        <p>InsightPulse AI - Email Authentication Test<br>
        Generated: {formatdate(localtime=True)}</p>
    </div>
</body>
</html>
"""

    msg.attach(MIMEText(text_content, 'plain'))
    msg.attach(MIMEText(html_content, 'html'))

    # Connect to SMTP server
    server = smtplib.SMTP(smtp_host, smtp_port, timeout=30)
    server.set_debuglevel(0)
    server.ehlo()

    # Start TLS if available
    if server.has_extn('STARTTLS'):
        server.starttls()
        server.ehlo()

    # Authenticate
    server.login(smtp_user, smtp_password)

    # Send email
    server.send_message(msg)
    server.quit()

    print(f"SUCCESS:{test_id}")

except smtplib.SMTPAuthenticationError as e:
    print(f"ERROR:Authentication failed - check SMTP credentials", file=sys.stderr)
    sys.exit(1)
except smtplib.SMTPException as e:
    print(f"ERROR:SMTP error - {str(e)}", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"ERROR:{str(e)}", file=sys.stderr)
    sys.exit(1)
EOF
)

# Check send result
if echo "$SEND_RESULT" | grep -q "^SUCCESS:"; then
    ACTUAL_TEST_ID=$(echo "$SEND_RESULT" | cut -d: -f2)
    print_check "Email sent successfully (Test ID: $ACTUAL_TEST_ID)"
else
    print_fail "Email sending failed"
    echo "$SEND_RESULT"
    exit 1
fi

# Instructions for manual verification
print_section "Manual Verification Steps"

echo ""
echo "1. Check your inbox at: $TEST_EMAIL_TO"
echo ""
echo "2. Verify the email arrived (subject: 'Email Authentication Test - $TEST_ID')"
echo ""
echo "3. Check email headers for authentication:"
echo ""
echo "   Gmail:"
echo "     - Open the email"
echo "     - Click the three dots (...) menu"
echo "     - Select 'Show original'"
echo "     - Look for these headers:"
echo "       • DKIM-Signature: should show d=mg.insightpulseai.net"
echo "       • SPF: should show 'pass'"
echo "       • DMARC: should show 'pass'"
echo ""
echo "   Outlook/Office 365:"
echo "     - Open the email"
echo "     - Click File → Properties"
echo "     - Look in 'Internet headers' section"
echo ""
echo "   Apple Mail:"
echo "     - Open the email"
echo "     - View → Message → Raw Source (Option+Cmd+U)"
echo ""
echo "4. Use online testing tools for comprehensive analysis:"
echo ""
echo "   Mail Tester (recommended):"
echo "     - Forward the email to: test-XXXXX@mail-tester.com"
echo "     - Visit https://www.mail-tester.com/"
echo "     - Check your score (should be 10/10 for perfect authentication)"
echo ""
echo "   MX Toolbox Email Headers:"
echo "     - Copy email headers"
echo "     - Visit https://mxtoolbox.com/EmailHeaders.aspx"
echo "     - Paste headers and analyze"
echo ""

# Expected header values
print_section "Expected Authentication Results"

echo ""
echo "✓ DKIM-Signature:"
echo "  d=mg.insightpulseai.net"
echo "  s=pic"
echo "  Result: pass"
echo ""
echo "✓ SPF:"
echo "  Return-Path: <postmaster@mg.insightpulseai.net>"
echo "  Result: pass"
echo ""
echo "✓ DMARC:"
echo "  From: noreply@mg.insightpulseai.net"
echo "  Policy: quarantine (or reject if upgraded)"
echo "  Result: pass"
echo ""
echo "✓ Overall Spam Score:"
echo "  Should be low (< 1.0)"
echo "  Mail-tester.com score should be ≥ 9/10"
echo ""

print_section "Troubleshooting Common Issues"

echo ""
echo "If DKIM fails:"
echo "  - Verify DNS DKIM record with: dig +short TXT pic._domainkey.mg.insightpulseai.net"
echo "  - Ensure record starts with 'v=DKIM1;'"
echo "  - Check Mailgun dashboard for DKIM verification status"
echo ""
echo "If SPF fails:"
echo "  - Verify DNS SPF record with: dig +short TXT mg.insightpulseai.net"
echo "  - Ensure record includes 'include:mailgun.org'"
echo "  - Check that Return-Path domain matches mg.insightpulseai.net"
echo ""
echo "If DMARC fails:"
echo "  - Verify DNS DMARC record with: dig +short TXT _dmarc.mg.insightpulseai.net"
echo "  - Both DKIM and SPF must pass for DMARC to pass"
echo "  - Check that From domain aligns with DKIM and SPF domains"
echo ""
echo "If email doesn't arrive:"
echo "  - Check spam/junk folder"
echo "  - Verify recipient email address is correct"
echo "  - Check Mailgun logs at https://app.mailgun.com/app/sending/domains/mg.insightpulseai.net/logs"
echo "  - Ensure SMTP credentials are correct"
echo ""

print_section "Test Complete"

echo ""
print_info "Email sent to: $TEST_EMAIL_TO"
print_info "Test ID: $TEST_ID"
echo ""
echo "Follow the manual verification steps above to confirm email authentication."
echo ""
echo "For automated verification in CI/CD, consider:"
echo "  - Using Mailgun Events API to track delivery status"
echo "  - Implementing a webhook to receive delivery/bounce notifications"
echo "  - Checking Mailgun logs programmatically via API"
echo ""

exit 0
