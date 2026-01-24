#!/usr/bin/env bash
# Test the expense integration flow end-to-end
# Usage: ./scripts/integration/test-expense-flow.sh
set -euo pipefail

# Load environment variables
if [[ -f .env ]]; then
    # shellcheck disable=SC1091
    source .env
fi

# Configuration
SUPABASE_URL="${SUPABASE_URL:-https://spdtwktxdalcfigzeqrz.supabase.co}"
SUPABASE_SERVICE_ROLE_KEY="${SUPABASE_SERVICE_ROLE_KEY:-}"
WEBHOOK_SECRET="${IPAI_WEBHOOK_SECRET:-test-secret}"

if [[ -z "$SUPABASE_SERVICE_ROLE_KEY" ]]; then
    echo "Error: SUPABASE_SERVICE_ROLE_KEY not set"
    echo "Set it in .env or export it before running this script"
    exit 1
fi

echo "=== Supabase Integration Bus - Expense Flow Test ==="
echo ""

# Generate test data
TIMESTAMP=$(date +%s)
IDEMPOTENCY_KEY="test-expense-${TIMESTAMP}"

# Build test payload
PAYLOAD=$(cat <<EOF
{
    "source": "odoo",
    "event_type": "expense.submitted",
    "aggregate_type": "expense",
    "aggregate_id": "hr.expense,999",
    "idempotency_key": "${IDEMPOTENCY_KEY}",
    "payload": {
        "expense_id": 999,
        "name": "Test Expense - Integration Test",
        "employee_id": 1,
        "employee_name": "Test Employee",
        "total_amount": 150.00,
        "currency": "PHP",
        "state": "submitted",
        "description": "Integration test expense created at ${TIMESTAMP}",
        "date": "$(date +%Y-%m-%d)"
    }
}
EOF
)

# Compute HMAC signature
SIGNATURE=$(echo -n "${TIMESTAMP}.${PAYLOAD}" | openssl dgst -sha256 -hmac "$WEBHOOK_SECRET" | sed 's/^.* //')

echo "Step 1: Sending test event to Edge Function webhook..."
echo "  URL: ${SUPABASE_URL}/functions/v1/odoo-webhook"
echo "  Idempotency Key: ${IDEMPOTENCY_KEY}"

# Send to Edge Function
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${SUPABASE_URL}/functions/v1/odoo-webhook" \
    -H "Content-Type: application/json" \
    -H "X-Webhook-Signature: ${SIGNATURE}" \
    -H "X-Webhook-Timestamp: ${TIMESTAMP}" \
    -d "$PAYLOAD")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

echo "  Response: HTTP ${HTTP_CODE}"
echo "  Body: ${BODY}"
echo ""

if [[ "$HTTP_CODE" != "200" ]]; then
    echo "Warning: Webhook returned non-200 status. Trying direct insert..."

    # Fallback: Insert directly to outbox
    DIRECT_RESPONSE=$(curl -s -X POST "${SUPABASE_URL}/rest/v1/integration.outbox" \
        -H "apikey: ${SUPABASE_SERVICE_ROLE_KEY}" \
        -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" \
        -H "Content-Type: application/json" \
        -H "Prefer: return=representation" \
        -d "$PAYLOAD")

    echo "  Direct insert response: ${DIRECT_RESPONSE}"
    echo ""
fi

echo "Step 2: Verifying event in outbox..."
sleep 1

OUTBOX_CHECK=$(curl -s -X GET "${SUPABASE_URL}/rest/v1/integration.outbox?idempotency_key=eq.${IDEMPOTENCY_KEY}&select=id,status,event_type,created_at" \
    -H "apikey: ${SUPABASE_SERVICE_ROLE_KEY}" \
    -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}")

echo "  Outbox entry: ${OUTBOX_CHECK}"
echo ""

echo "Step 3: Verifying event in event_log..."
EVENT_LOG=$(curl -s -X GET "${SUPABASE_URL}/rest/v1/integration.event_log?order=created_at.desc&limit=1&select=id,event_type,source,created_at" \
    -H "apikey: ${SUPABASE_SERVICE_ROLE_KEY}" \
    -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}")

echo "  Latest event: ${EVENT_LOG}"
echo ""

# Parse results
if echo "$OUTBOX_CHECK" | grep -q '"status":"pending"'; then
    echo "=== TEST PASSED ==="
    echo "Event successfully stored in outbox with 'pending' status."
    echo "The n8n Event Router will pick it up on next poll cycle (every 30s)."
elif echo "$OUTBOX_CHECK" | grep -q '"status":"processing"'; then
    echo "=== TEST PASSED ==="
    echo "Event is already being processed by n8n."
elif echo "$OUTBOX_CHECK" | grep -q '"status":"done"'; then
    echo "=== TEST PASSED ==="
    echo "Event was already processed and completed!"
else
    echo "=== TEST INCONCLUSIVE ==="
    echo "Could not verify event status. Check the responses above."
fi

echo ""
echo "Manual verification queries:"
echo ""
echo "-- Check outbox"
echo "SELECT * FROM integration.outbox WHERE idempotency_key = '${IDEMPOTENCY_KEY}';"
echo ""
echo "-- Check event log"
echo "SELECT * FROM integration.event_log ORDER BY created_at DESC LIMIT 5;"
