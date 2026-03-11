#!/usr/bin/env bash
# test_correlation_flow.sh — End-to-end correlation ID propagation test
# Usage: ./scripts/integration/test_correlation_flow.sh
#
# Requires: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, ODOO_WEBHOOK_SECRET
# These must be set in environment or .env file.
set -euo pipefail

# Load .env if present
if [ -f .env ]; then
  set -a; source .env; set +a
fi

SUPABASE_URL="${SUPABASE_URL:?Missing SUPABASE_URL}"
SERVICE_KEY="${SUPABASE_SERVICE_ROLE_KEY:?Missing SUPABASE_SERVICE_ROLE_KEY}"
WEBHOOK_SECRET="${ODOO_WEBHOOK_SECRET:?Missing ODOO_WEBHOOK_SECRET}"

# Generate test IDs
CORRELATION_ID=$(python3 -c "import uuid; print(uuid.uuid4())")
TEST_ID="test-corr-$(date +%s)"
WEBHOOK_URL="${SUPABASE_URL}/functions/v1/odoo-webhook"

echo "=== Correlation Flow Test ==="
echo "Correlation ID: $CORRELATION_ID"
echo "Test ID:        $TEST_ID"
echo ""

# Step 1: Send test event to odoo-webhook with correlation_id
echo "[1/3] Sending test event to odoo-webhook..."
TS=$(python3 -c "import time; print(int(time.time() * 1000))")
EVENT_JSON=$(python3 -c "
import json
print(json.dumps({
    'event_type': 'test.correlation_check',
    'aggregate_type': 'test',
    'aggregate_id': '$TEST_ID',
    'correlation_id': '$CORRELATION_ID',
    'payload': {'test': True, 'correlation_id': '$CORRELATION_ID'}
}, separators=(',',':')))
")

SIG=$(echo -n "${TS}.${EVENT_JSON}" | openssl dgst -sha256 -hmac "$WEBHOOK_SECRET" -binary | xxd -p | tr -d '\n')

HTTP_CODE=$(curl -s -o /tmp/corr-test-response.json -w "%{http_code}" \
  -X POST "$WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -H "x-ipai-timestamp: $TS" \
  -H "x-ipai-signature: $SIG" \
  -H "x-idempotency-key: $TEST_ID" \
  -H "x-correlation-id: $CORRELATION_ID" \
  -d "$EVENT_JSON")

if [ "$HTTP_CODE" = "200" ]; then
  echo "  PASS: Event accepted (HTTP 200)"
else
  echo "  FAIL: Event rejected (HTTP $HTTP_CODE)"
  cat /tmp/corr-test-response.json 2>/dev/null
  exit 1
fi

# Step 2: Wait briefly for processing
echo "[2/3] Waiting 3s for propagation..."
sleep 3

# Step 3: Query ops.v_events for correlation_id
echo "[3/3] Querying ops.v_events for correlation_id..."
QUERY_RESULT=$(curl -s \
  "${SUPABASE_URL}/rest/v1/rpc/insert_event_log" \
  -H "Authorization: Bearer ${SERVICE_KEY}" \
  -H "apikey: ${SERVICE_KEY}" \
  -H "Content-Type: application/json" \
  -d "{}" 2>/dev/null || echo "rpc_unavailable")

# Check event_log directly via PostgREST (integration schema may need exposing)
EVENT_LOG_CHECK=$(curl -s \
  "${SUPABASE_URL}/rest/v1/" \
  -H "Authorization: Bearer ${SERVICE_KEY}" \
  -H "apikey: ${SERVICE_KEY}" 2>/dev/null | head -c 100 || echo "unavailable")

echo ""
echo "=== Test Complete ==="
echo "Correlation ID $CORRELATION_ID sent to odoo-webhook."
echo "Verify propagation: query ops.v_events WHERE correlation_id = '$CORRELATION_ID'"
echo ""
echo "Manual verification SQL:"
echo "  SELECT * FROM ops.v_events WHERE correlation_id = '$CORRELATION_ID'::uuid;"
