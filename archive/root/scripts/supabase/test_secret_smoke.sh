#!/usr/bin/env bash
set -euo pipefail

# Load env
set -a
source .env.platform.local
set +a

echo "Testing secret-smoke function..."
echo "URL: ${SUPABASE_URL}/functions/v1/secret-smoke"

# Try with service role key (has full access)
response=$(curl -s -w "\n%{http_code}" -X POST "${SUPABASE_URL}/functions/v1/secret-smoke" \
  -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" \
  -H "Content-Type: application/json" \
  --max-time 10)

http_code=$(echo "$response" | tail -n 1)
body=$(echo "$response" | head -n -1)

echo "HTTP Code: $http_code"
echo "Response: $body"

if [ "$http_code" = "200" ]; then
  echo "✅ Secret smoke test passed"
  echo "$body" | jq . 2>/dev/null || echo "$body"
else
  echo "❌ Secret smoke test failed"
  exit 1
fi
