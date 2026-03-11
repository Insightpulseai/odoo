#!/usr/bin/env bash
set -euo pipefail

# Load env
if [ -f .env.platform.local ]; then
  set -a
  source .env.platform.local
  set +a
fi

: "${SUPABASE_URL:?set SUPABASE_URL}"
: "${SUPABASE_ANON_KEY:?set SUPABASE_ANON_KEY (publishable/anon)}"

TEST_EMAIL="${TEST_EMAIL:-business@insightpulseai.com}"

echo "🔢 Testing Email OTP Flow (via curl)..."
echo "→ Sending OTP to: $TEST_EMAIL"
echo ""

# Send OTP via Supabase Auth API
# CRITICAL: Auth endpoints require BOTH apikey AND Authorization headers
response=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST "${SUPABASE_URL}/auth/v1/otp" \
  -H "apikey: ${SUPABASE_ANON_KEY}" \
  -H "Authorization: Bearer ${SUPABASE_ANON_KEY}" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"${TEST_EMAIL}\",\"create_user\":false}")

http_code=$(echo "$response" | grep "HTTP_CODE:" | cut -d: -f2)
body=$(echo "$response" | grep -v "HTTP_CODE:")

echo "HTTP Status: $http_code"
echo "Response: $body"
echo ""

if [ "$http_code" = "200" ]; then
  echo "✅ Email OTP sent successfully!"
  echo ""
  echo "Next steps:"
  echo "  1. Check email inbox: $TEST_EMAIL"
  echo "  2. Copy the 6-digit code from the email"
  echo "  3. Code expires in 5 minutes"
  echo ""
  echo "To verify OTP (after receiving code):"
  echo "  curl -X POST '${SUPABASE_URL}/auth/v1/verify' \\"
  echo "    -H 'apikey: ${SUPABASE_ANON_KEY}' \\"
  echo "    -H 'Authorization: Bearer ${SUPABASE_ANON_KEY}' \\"
  echo "    -H 'Content-Type: application/json' \\"
  echo "    -d '{\"type\": \"email\", \"email\": \"${TEST_EMAIL}\", \"token\": \"123456\"}'"
else
  echo "❌ Email OTP failed (HTTP $http_code)"
  echo ""
  echo "Troubleshooting:"
  echo "  - Check SMTP configuration in Supabase Dashboard"
  echo "  - Verify user exists (create_user: false requires existing user)"
  echo "  - Check Supabase Auth logs for errors"
  echo "  - Verify SUPABASE_ANON_KEY is correct (use fetch_project_api_keys.sh)"
  exit 1
fi
