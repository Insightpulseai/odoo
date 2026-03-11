#!/usr/bin/env bash
set -euo pipefail

# Load env
if [ -f .env.platform.local ]; then
  set -a
  source .env.platform.local
  set +a
fi

echo "🧪 Invoking secret-smoke function..."
echo "URL: ${SUPABASE_URL}/functions/v1/secret-smoke"
echo ""

# Invoke with service role key
http_code=$(curl -s -w "%{http_code}" -o /tmp/secret-smoke-response.json \
  -X POST "${SUPABASE_URL}/functions/v1/secret-smoke" \
  -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" \
  -H "Content-Type: application/json" \
  --max-time 30)

echo "HTTP Status: $http_code"
echo ""

if [ -f /tmp/secret-smoke-response.json ]; then
  echo "Response:"
  cat /tmp/secret-smoke-response.json | jq . 2>/dev/null || cat /tmp/secret-smoke-response.json
  echo ""
  rm /tmp/secret-smoke-response.json
fi

if [ "$http_code" = "200" ]; then
  echo "✅ Secret smoke test PASSED"
  exit 0
else
  echo "❌ Secret smoke test FAILED (HTTP $http_code)"
  exit 1
fi
