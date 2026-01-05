#!/usr/bin/env bash
# ==============================================================================
# SMTP CONNECTIVITY DIAGNOSTIC TOOL
# ==============================================================================
# Tests SMTP connectivity and diagnoses common issues
# Specifically checks for DigitalOcean SMTP port blocking
#
# Usage: ./scripts/diagnose_smtp.sh
# ==============================================================================

set -euo pipefail

CONTAINER_NAME=$(docker ps --format "{{.Names}}" | grep odoo | head -n 1)

if [[ -z "$CONTAINER_NAME" ]]; then
    echo "❌ ERROR: No running Odoo container found"
    exit 1
fi

echo "=================================================="
echo "SMTP CONNECTIVITY DIAGNOSTIC"
echo "=================================================="
echo "Container: $CONTAINER_NAME"
echo "Testing against: smtp.gmail.com"
echo ""

# === Test 1: Check if nc (netcat) is available ===
echo ">>> [Test 1/6] Checking netcat availability..."
if docker exec "$CONTAINER_NAME" which nc > /dev/null 2>&1; then
    echo "✓ netcat available"
    NC_AVAILABLE=true
else
    echo "⚠️  netcat not available in container - installing..."
    docker exec "$CONTAINER_NAME" apt-get update -qq > /dev/null 2>&1
    docker exec "$CONTAINER_NAME" apt-get install -y netcat-openbsd -qq > /dev/null 2>&1
    NC_AVAILABLE=true
    echo "✓ netcat installed"
fi

# === Test 2: DNS Resolution ===
echo ""
echo ">>> [Test 2/6] Testing DNS resolution..."
if docker exec "$CONTAINER_NAME" nslookup smtp.gmail.com > /dev/null 2>&1; then
    GMAIL_IP=$(docker exec "$CONTAINER_NAME" nslookup smtp.gmail.com | grep "Address:" | tail -1 | awk '{print $2}')
    echo "✓ DNS resolves: smtp.gmail.com → $GMAIL_IP"
else
    echo "❌ FAIL: DNS resolution failed for smtp.gmail.com"
    echo "   Check: /etc/resolv.conf in container"
    exit 1
fi

# === Test 3: Port 465 (SSL/TLS) - Primary ===
echo ""
echo ">>> [Test 3/6] Testing SMTP port 465 (SSL/TLS)..."
echo "   This is the CRITICAL test for DigitalOcean SMTP blocking"
echo "   If this times out, DigitalOcean is blocking outbound SMTP"
echo ""

timeout 10 docker exec "$CONTAINER_NAME" nc -zv smtp.gmail.com 465 > /dev/null 2>&1
PORT_465_RESULT=$?

if [[ $PORT_465_RESULT -eq 0 ]]; then
    echo "✓ PASS: Port 465 is open and reachable"
    PORT_465_BLOCKED=false
else
    echo "❌ FAIL: Port 465 is BLOCKED or unreachable"
    echo ""
    echo "⚠️  DIGITALOCEAN SMTP PORT BLOCKING DETECTED"
    echo ""
    echo "DigitalOcean blocks outbound SMTP ports (25, 465, 587) by default"
    echo "to prevent spam. This is a common issue on new Droplets."
    echo ""
    PORT_465_BLOCKED=true
fi

# === Test 4: Port 587 (STARTTLS) - Alternative ===
echo ""
echo ">>> [Test 4/6] Testing SMTP port 587 (STARTTLS)..."

timeout 10 docker exec "$CONTAINER_NAME" nc -zv smtp.gmail.com 587 > /dev/null 2>&1
PORT_587_RESULT=$?

if [[ $PORT_587_RESULT -eq 0 ]]; then
    echo "✓ PASS: Port 587 is open and reachable"
    PORT_587_BLOCKED=false
else
    echo "❌ FAIL: Port 587 is BLOCKED or unreachable"
    PORT_587_BLOCKED=true
fi

# === Test 5: Port 25 (Legacy) ===
echo ""
echo ">>> [Test 5/6] Testing SMTP port 25 (legacy)..."

timeout 10 docker exec "$CONTAINER_NAME" nc -zv smtp.gmail.com 25 > /dev/null 2>&1
PORT_25_RESULT=$?

if [[ $PORT_25_RESULT -eq 0 ]]; then
    echo "✓ PASS: Port 25 is open (but Gmail doesn't use this)"
    PORT_25_BLOCKED=false
else
    echo "❌ FAIL: Port 25 is BLOCKED"
    PORT_25_BLOCKED=true
fi

# === Test 6: Python SMTP Test ===
echo ""
echo ">>> [Test 6/6] Testing Python SMTP library connection..."

docker exec "$CONTAINER_NAME" python3 <<'PYTHON_EOF'
import socket
import sys

try:
    # Test raw socket connection to port 465
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    result = sock.connect_ex(('smtp.gmail.com', 465))
    sock.close()

    if result == 0:
        print('✓ PASS: Python socket connection successful on port 465')
        sys.exit(0)
    else:
        print(f'❌ FAIL: Python socket connection failed (error code: {result})')
        sys.exit(1)
except Exception as e:
    print(f'❌ FAIL: Python socket test error: {e}')
    sys.exit(1)
PYTHON_EOF

PYTHON_TEST_RESULT=$?

# === DIAGNOSTIC SUMMARY ===
echo ""
echo "=================================================="
echo "DIAGNOSTIC SUMMARY"
echo "=================================================="
echo ""

TESTS_PASSED=0
TESTS_FAILED=0

echo "DNS Resolution:        ✓ PASS"
((TESTS_PASSED++))

if [[ $PORT_465_BLOCKED == false ]]; then
    echo "Port 465 (SSL/TLS):    ✓ PASS"
    ((TESTS_PASSED++))
else
    echo "Port 465 (SSL/TLS):    ❌ FAIL (BLOCKED)"
    ((TESTS_FAILED++))
fi

if [[ $PORT_587_BLOCKED == false ]]; then
    echo "Port 587 (STARTTLS):   ✓ PASS"
    ((TESTS_PASSED++))
else
    echo "Port 587 (STARTTLS):   ❌ FAIL (BLOCKED)"
    ((TESTS_FAILED++))
fi

if [[ $PORT_25_BLOCKED == false ]]; then
    echo "Port 25 (Legacy):      ✓ PASS (not used)"
else
    echo "Port 25 (Legacy):      ❌ FAIL (BLOCKED)"
fi

if [[ $PYTHON_TEST_RESULT -eq 0 ]]; then
    echo "Python SMTP Test:      ✓ PASS"
    ((TESTS_PASSED++))
else
    echo "Python SMTP Test:      ❌ FAIL"
    ((TESTS_FAILED++))
fi

echo ""
echo "Tests Passed: $TESTS_PASSED"
echo "Tests Failed: $TESTS_FAILED"
echo ""

# === RECOMMENDATIONS ===
if [[ $PORT_465_BLOCKED == true ]] && [[ $PORT_587_BLOCKED == true ]]; then
    echo "=================================================="
    echo "❌ CRITICAL: DIGITALOCEAN SMTP BLOCKING DETECTED"
    echo "=================================================="
    echo ""
    echo "All SMTP ports (25, 465, 587) are blocked."
    echo "This is DigitalOcean's default spam prevention policy."
    echo ""
    echo "SOLUTION OPTIONS:"
    echo ""
    echo "Option 1: Request SMTP Unblock from DigitalOcean (RECOMMENDED)"
    echo "  1. Submit support ticket: https://cloud.digitalocean.com/support/tickets/new"
    echo "  2. Subject: 'Request to unblock outbound SMTP ports (25, 465, 587)'"
    echo "  3. Explain: 'Production Odoo ERP needs to send transaction emails'"
    echo "  4. Provide: Droplet ID, business use case, anti-spam measures"
    echo "  5. Wait: 24-48 hours for review and approval"
    echo ""
    echo "Option 2: Use SMTP Relay Service (IMMEDIATE WORKAROUND)"
    echo "  - SendGrid (DigitalOcean partner): Free tier 100 emails/day"
    echo "  - Mailgun: Free tier 5,000 emails/month"
    echo "  - Amazon SES: \$0.10 per 1,000 emails"
    echo ""
    echo "  Configure relay in Odoo:"
    echo "    SMTP Server: smtp.sendgrid.net (or relay provider)"
    echo "    Port: 587 (STARTTLS)"
    echo "    Username: apikey (for SendGrid)"
    echo "    Password: <API_KEY>"
    echo ""
    echo "Option 3: Use Alternative Port (if available)"
    echo "  Some providers allow port 2525 (non-standard SMTP)"
    echo ""
    echo "Option 4: Move to Different Cloud Provider"
    echo "  AWS, GCP, Azure don't block SMTP by default"
    echo "  (but requires migration)"
    echo ""
    exit 1
elif [[ $PORT_465_BLOCKED == true ]] && [[ $PORT_587_BLOCKED == false ]]; then
    echo "=================================================="
    echo "⚠️  WARNING: Port 465 blocked, but 587 is open"
    echo "=================================================="
    echo ""
    echo "RECOMMENDATION: Switch to port 587 with STARTTLS"
    echo ""
    echo "Update Odoo SMTP configuration:"
    echo "  SMTP Port: 587 (instead of 465)"
    echo "  Connection Security: STARTTLS (instead of SSL/TLS)"
    echo ""
    echo "Run this command to reconfigure:"
    echo "  ./scripts/configure_gmail_smtp.sh --port 587"
    echo ""
    exit 1
else
    echo "=================================================="
    echo "✅ ALL SMTP CONNECTIVITY TESTS PASSED"
    echo "=================================================="
    echo ""
    echo "SMTP connectivity is working correctly."
    echo "You can proceed with Gmail SMTP configuration."
    echo ""
    echo "Next steps:"
    echo "  1. Configure Gmail SMTP: ./scripts/configure_gmail_smtp.sh"
    echo "  2. Test email sending in Odoo UI"
    echo "  3. Monitor logs: docker logs $CONTAINER_NAME --tail 50 -f"
    echo ""
    exit 0
fi
