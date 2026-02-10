#!/usr/bin/env bash
set -euo pipefail

# Load env
if [ -f .env.platform.local ]; then
  set -a
  source .env.platform.local
  set +a
fi

TEST_EMAIL="${TEST_EMAIL:-test@insightpulseai.com}"

echo "🔗 Testing Magic Link Flow (via curl)..."
echo "→ Sending magic link to: $TEST_EMAIL"
echo ""

# Send magic link via Supabase Auth API (using service role key for testing)
response=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST "${SUPABASE_URL}/auth/v1/otp" \
  -H "apikey: ${SUPABASE_SERVICE_ROLE_KEY}" \
  -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"${TEST_EMAIL}\",
    \"create_user\": true,
    \"data\": {},
    \"gotrue_meta_security\": {}
  }")

http_code=$(echo "$response" | grep "HTTP_CODE:" | cut -d: -f2)
body=$(echo "$response" | grep -v "HTTP_CODE:")

echo "HTTP Status: $http_code"
echo "Response: $body"
echo ""

if [ "$http_code" = "200" ]; then
  echo "✅ Magic Link sent successfully!"
  echo ""
  echo "Next steps:"
  echo "  1. Check email inbox: $TEST_EMAIL"
  echo "  2. Click the magic link in the email"
  echo "  3. Link expires in 24 hours"
  echo ""
  echo "Expected redirect: https://auth.insightpulseai.com (or configured redirect URL)"
else
  echo "❌ Magic Link failed (HTTP $http_code)"
  echo ""
  echo "Troubleshooting:"
  echo "  - Check SMTP configuration in Supabase Dashboard"
  echo "  - Verify Zoho Mail credentials are correct"
  echo "  - Check Supabase Auth logs for errors"
  exit 1
fi
