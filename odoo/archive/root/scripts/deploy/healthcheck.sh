#!/bin/bash
ENV=$1
MAX_RETRIES=10
RETRY_INTERVAL=5

if [[ -z "$ENV" ]]; then
  echo "Usage: ./healthcheck.sh <env>"
  exit 1
fi

PORT=8069
if [[ "$ENV" == "prod" ]]; then
  PORT=80
fi

echo "🔍 Checking health for $ENV on port $PORT..."

for i in $(seq 1 $MAX_RETRIES); do
  RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$PORT/web/health || true)
  if [[ "$RESPONSE" == "200" ]]; then
    echo "✅ Healthcheck passed!"
    exit 0
  fi
  echo "⏳ Attempt $i: Waiting for container... (HTTP $RESPONSE)"
  sleep $RETRY_INTERVAL
done

echo "❌ Healthcheck failed after $MAX_RETRIES attempts."
exit 1
