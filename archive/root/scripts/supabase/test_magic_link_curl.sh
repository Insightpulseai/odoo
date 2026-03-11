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

echo "🔗 Testing Magic Link Flow (via curl)..."
echo "→ Sending magic link to: $TEST_EMAIL"
echo ""

# Send magic link via Supabase Auth API
# CRITICAL: Auth endpoints require BOTH apikey AND Authorization headers
response=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST "${SUPABASE_URL}/auth/v1/otp" \
  -H "apikey: ${SUPABASE_ANON_KEY}" \
  -H "Authorization: Bearer ${SUPABASE_ANON_KEY}" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"${TEST_EMAIL}\",\"create_user\":true}")

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
  echo "  - Verify SUPABASE_ANON_KEY is correct (use fetch_project_api_keys.sh)"
  exit 1
fi
