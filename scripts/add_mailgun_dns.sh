#!/bin/bash
# Add Mailgun DNS Records for mg.insightpulseai.net
# Domain is on Google Domains (nameservers: ns-cloud-e*.googledomains.com)

set -e

echo "=================================================="
echo "Mailgun DNS Setup for mg.insightpulseai.net"
echo "=================================================="
echo ""

# Check if domain is accessible
echo "1. Checking domain nameservers..."
NS=$(dig NS insightpulseai.net +short | head -1)
if [[ -z "$NS" ]]; then
    echo "❌ Cannot resolve insightpulseai.net"
    exit 1
fi
echo "✅ Domain found: $NS"
echo ""

# Records to add
echo "2. DNS Records to Add:"
echo "=================================================="
cat <<'EOF'

RECORD 1: SPF (Sender Authorization)
Type: TXT
Name: mg.insightpulseai.net
Value: v=spf1 include:mailgun.org ~all

RECORD 2: DKIM (Email Signature)
Type: TXT
Name: pic._domainkey.mg.insightpulseai.net
Value: k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDcYB3DG10ylI4z6PWaiwyiByMrjwr9kfgJK8ccsZYT4guxi8+Emyf/nUs7IqR/LTZwwymeTZDaS/vQ6pjDhIaF2J9M9XsdgP+nv3wx99BqQ7dA+aa5sNwJKI3WRhr1YMK6IJQJIWSLERPBr74eMBAVa/Zmrfui1BOCgUFvQN9GBQIDAQAB

RECORD 3: MX Record 1 (Incoming Mail)
Type: MX
Name: mg.insightpulseai.net
Value: mxa.mailgun.org
Priority: 10

RECORD 4: MX Record 2 (Incoming Mail)
Type: MX
Name: mg.insightpulseai.net
Value: mxb.mailgun.org
Priority: 10

RECORD 5: CNAME (Tracking)
Type: CNAME
Name: email.mg.insightpulseai.net
Value: mailgun.org

RECORD 6: DMARC (Authentication Policy)
Type: TXT
Name: _dmarc.mg.insightpulseai.net
Value: v=DMARC1; p=none; pct=100; fo=1; ri=3600; rua=mailto:3651085@dmarc.mailgun.org,mailto:682ce2a3@inbox.ondmarc.com; ruf=mailto:3651085@dmarc.mailgun.org,mailto:682ce2a3@inbox.ondmarc.com;

EOF
echo "=================================================="
echo ""

# Instructions
echo "3. How to Add These Records:"
echo "=================================================="
echo "OPTION A - Automatic (Recommended):"
echo "  1. Go to Mailgun dashboard: https://app.mailgun.com/mg/sending/domains/mg.insightpulseai.net/verify"
echo "  2. Click 'Automatic setup'"
echo "  3. Login to Google Domains"
echo "  4. Allow Mailgun to add records automatically"
echo ""
echo "OPTION B - Manual:"
echo "  1. Go to https://domains.google.com/registrar/insightpulseai.net/dns"
echo "  2. Click 'Manage custom records'"
echo "  3. Add each record from above"
echo "  4. Save changes"
echo ""
echo "=================================================="
echo ""

# Verification
echo "4. After Adding (wait 10-60 min for propagation):"
echo "=================================================="
echo "Run these commands to verify:"
echo ""
echo "  dig TXT mg.insightpulseai.net +short"
echo "  dig TXT pic._domainkey.mg.insightpulseai.net +short"
echo "  dig MX mg.insightpulseai.net +short"
echo "  dig CNAME email.mg.insightpulseai.net +short"
echo "  dig TXT _dmarc.mg.insightpulseai.net +short"
echo ""
echo "=================================================="
echo ""

# Open Mailgun dashboard
echo "5. Opening Mailgun dashboard..."
if command -v open &> /dev/null; then
    open "https://app.mailgun.com/mg/sending/domains/mg.insightpulseai.net/verify"
fi

echo ""
echo "✅ Instructions complete!"
echo "Add the DNS records and then verify in Mailgun dashboard."
