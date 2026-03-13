#!/usr/bin/env bash
set -euo pipefail

# ========================================
# Rate-Limit-Safe Auth Flow Testing
# ========================================
# Tests Magic Link and Email OTP flows with automatic rate limit handling.
# Uses exponential backoff and respects Supabase rate limits.
#
# Usage: ./test_auth_flows_safe.sh [EMAIL]

# Load env
if [ -f .env.platform.local ]; then
  set -a
  source .env.platform.local
  set +a
fi

: "${SUPABASE_URL:?set SUPABASE_URL}"
: "${SUPABASE_ANON_KEY:?set SUPABASE_ANON_KEY}"

TEST_EMAIL="${1:-business@insightpulseai.com}"
MAX_RETRIES=3
RETRY_DELAY=60  # Start with 60s delay

echo "🔐 Testing Auth Flows (Rate-Limit-Safe)"
echo "===================================================="
echo "→ Test Email: $TEST_EMAIL"
echo "→ Max Retries: $MAX_RETRIES"
echo ""

# Function: Send OTP with retry logic
send_otp() {
  local type=$1  # "magic_link" or "email_otp"
  local create_user=$2  # "true" or "false"
  local attempt=1
  local delay=$RETRY_DELAY

  while [ $attempt -le $MAX_RETRIES ]; do
    echo "→ Attempt $attempt/$MAX_RETRIES: Sending $type..."

    response=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST "${SUPABASE_URL}/auth/v1/otp" \
      -H "apikey: ${SUPABASE_ANON_KEY}" \
      -H "Authorization: Bearer ${SUPABASE_ANON_KEY}" \
      -H "Content-Type: application/json" \
      -d "{\"email\":\"${TEST_EMAIL}\",\"create_user\":${create_user}}")

    http_code=$(echo "$response" | grep "HTTP_CODE:" | cut -d: -f2)
    body=$(echo "$response" | grep -v "HTTP_CODE:")

    if [ "$http_code" = "200" ]; then
      echo "  ✅ $type sent successfully (HTTP 200)"
      return 0
    elif [ "$http_code" = "429" ]; then
      echo "  ⏳ Rate limited (HTTP 429) - waiting ${delay}s before retry..."
      sleep $delay
      delay=$((delay * 2))  # Exponential backoff
      attempt=$((attempt + 1))
    else
      echo "  ❌ $type failed (HTTP $http_code): $body"
      return 1
    fi
  done

  echo "  ❌ Max retries exceeded. Rate limit still active."
  return 1
}

# Test 1: Magic Link Flow
echo "Test 1: Magic Link Flow"
echo "--------------------"
if send_otp "magic_link" "true"; then
  echo "✅ Magic Link test PASSED"
  echo ""
else
  echo "❌ Magic Link test FAILED"
  exit 1
fi

# Wait before next test
echo "⏳ Waiting 60s before next test (rate limit cooldown)..."
sleep 60
echo ""

# Test 2: Email OTP Flow
echo "Test 2: Email OTP Flow"
echo "--------------------"
if send_otp "email_otp" "false"; then
  echo "✅ Email OTP test PASSED"
  echo ""
else
  echo "❌ Email OTP test FAILED"
  exit 1
fi

# Summary
echo "===================================================="
echo "✅ All Auth Flow Tests PASSED"
echo ""
echo "Next steps:"
echo "  1. Check email inbox: $TEST_EMAIL"
echo "  2. Verify Magic Link email received"
echo "  3. Verify OTP code email received"
echo "  4. Test auth callback: click Magic Link or enter OTP"
echo ""
