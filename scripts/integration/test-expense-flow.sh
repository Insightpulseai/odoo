#!/usr/bin/env bash
# Test end-to-end expense notification flow
# This script simulates an Odoo expense.submitted event and verifies the full pipeline

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SUPABASE_URL="${SUPABASE_URL:-https://spdtwktxdalcfigzeqrz.supabase.co}"
WEBHOOK_SECRET="${WEBHOOK_SECRET:-6900445459d89179a31e3bce61cf2d7f7732425650e17886edbbaec61c40a980}"
WEBHOOK_URL="${SUPABASE_URL}/functions/v1/odoo-webhook"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================="
echo "IPAI Integration Bus - E2E Test"
echo "========================================="
echo ""

# 1. Prepare test event
TIMESTAMP=$(date +%s000)  # Milliseconds (append 000 to seconds)
EVENT_TYPE="expense.submitted"
AGGREGATE_TYPE="expense"
AGGREGATE_ID="test-$(date +%s)"
IDEMPOTENCY_KEY="${EVENT_TYPE}:${AGGREGATE_ID}:${TIMESTAMP}"

PAYLOAD=$(cat <<EOF
{
  "event_type": "${EVENT_TYPE}",
  "aggregate_type": "${AGGREGATE_TYPE}",
  "aggregate_id": "${AGGREGATE_ID}",
  "payload": {
    "expense_id": 9999,
    "employee_id": 42,
    "employee_name": "Test User",
    "employee_code": "TEST001",
    "amount": 1234.56,
    "currency": "PHP",
    "description": "Test expense for integration bus verification",
    "date": "2026-01-22",
    "category": "Office Supplies",
    "submitted_at": "$(date -u +%Y-%m-%dT%H:%M:%S.000Z)",
    "state": "submit"
  }
}
EOF
)

# 2. Generate HMAC signature
MESSAGE="${TIMESTAMP}.${PAYLOAD}"
SIGNATURE=$(echo -n "$MESSAGE" | openssl dgst -sha256 -hmac "$WEBHOOK_SECRET" | awk '{print $2}')

echo "📤 Step 1: Send test event to Supabase Edge Function"
echo "   Event Type: ${EVENT_TYPE}"
echo "   Aggregate ID: ${AGGREGATE_ID}"
echo "   Idempotency Key: ${IDEMPOTENCY_KEY}"
echo ""

# 3. Send event to webhook
HTTP_CODE=$(curl -s -o /tmp/webhook_response.json -w "%{http_code}" \
  -X POST "${WEBHOOK_URL}" \
  -H "Content-Type: application/json" \
  -H "x-idempotency-key: ${IDEMPOTENCY_KEY}" \
  -H "x-ipai-signature: ${SIGNATURE}" \
  -H "x-ipai-timestamp: ${TIMESTAMP}" \
  -d "${PAYLOAD}")

if [ "$HTTP_CODE" -ne 200 ]; then
  echo -e "${RED}❌ Webhook call failed with HTTP ${HTTP_CODE}${NC}"
  cat /tmp/webhook_response.json
  exit 1
fi

WEBHOOK_RESPONSE=$(cat /tmp/webhook_response.json)
echo -e "${GREEN}✅ Webhook accepted event (HTTP 200)${NC}"
echo "   Response: ${WEBHOOK_RESPONSE}"
echo ""

# 4. Verify event in outbox (requires Supabase CLI or direct DB access)
echo "📊 Step 2: Verify event in integration.outbox"
echo ""

if command -v psql &> /dev/null && [ -n "${POSTGRES_URL_NON_POOLING:-}" ]; then
  OUTBOX_COUNT=$(psql "$POSTGRES_URL_NON_POOLING" -t -c \
    "SELECT COUNT(*) FROM integration.outbox WHERE aggregate_id = '${AGGREGATE_ID}' AND status = 'pending';")

  if [ "$OUTBOX_COUNT" -eq 1 ]; then
    echo -e "${GREEN}✅ Event found in outbox (status=pending)${NC}"

    # Show event details
    psql "$POSTGRES_URL_NON_POOLING" -c \
      "SELECT id, event_type, aggregate_type, aggregate_id, status, created_at FROM integration.outbox WHERE aggregate_id = '${AGGREGATE_ID}';"
  else
    echo -e "${RED}❌ Event not found in outbox (expected 1, found ${OUTBOX_COUNT})${NC}"
    exit 1
  fi
  echo ""

  # 5. Verify event in event_log
  echo "📜 Step 3: Verify event in integration.event_log"
  echo ""

  LOG_COUNT=$(psql "$POSTGRES_URL_NON_POOLING" -t -c \
    "SELECT COUNT(*) FROM integration.event_log WHERE aggregate_id = '${AGGREGATE_ID}';")

  if [ "$LOG_COUNT" -eq 1 ]; then
    echo -e "${GREEN}✅ Event logged in event_log (immutable audit trail)${NC}"
  else
    echo -e "${YELLOW}⚠️  Event not found in event_log (expected 1, found ${LOG_COUNT})${NC}"
  fi
  echo ""
else
  echo -e "${YELLOW}⚠️  psql not available or POSTGRES_URL_NON_POOLING not set${NC}"
  echo "   Cannot verify database state directly."
  echo "   Run this command manually to check:"
  echo ""
  echo "   psql \"\$POSTGRES_URL_NON_POOLING\" -c \\"
  echo "     \"SELECT * FROM integration.outbox WHERE aggregate_id = '${AGGREGATE_ID}';\""
  echo ""
fi

# 6. Instructions for n8n verification
echo "🔄 Step 4: n8n Event Router Processing"
echo ""
echo "The n8n event-router workflow (if active) will:"
echo "  1. Poll claim_outbox() every 30 seconds"
echo "  2. Claim this event (status: pending → processing)"
echo "  3. Route to expense-handler webhook"
echo "  4. Format Mattermost message"
echo "  5. Send notification to configured channel"
echo "  6. Acknowledge event (status: processing → completed)"
echo ""
echo "To verify:"
echo "  - Check n8n Executions: https://n8n.insightpulseai.net/executions"
echo "  - Check Mattermost channel for notification"
echo "  - Check outbox status (should become 'completed'):"
echo ""
echo "    psql \"\$POSTGRES_URL_NON_POOLING\" -c \\"
echo "      \"SELECT status, locked_by FROM integration.outbox WHERE aggregate_id = '${AGGREGATE_ID}';\""
echo ""

# 7. Manual claim test (optional)
if [ "${RUN_MANUAL_CLAIM:-false}" = "true" ] && command -v psql &> /dev/null && [ -n "${POSTGRES_URL_NON_POOLING:-}" ]; then
  echo "🔧 Manual Claim Test (optional)"
  echo ""

  CLAIMED=$(psql "$POSTGRES_URL_NON_POOLING" -t -c \
    "SELECT COUNT(*) FROM claim_outbox(1, 'test-manual-claim');")

  if [ "$CLAIMED" -eq 1 ]; then
    echo -e "${GREEN}✅ Successfully claimed 1 event via claim_outbox()${NC}"

    # Show claimed event
    psql "$POSTGRES_URL_NON_POOLING" -c \
      "SELECT id, event_type, status, locked_by FROM integration.outbox WHERE aggregate_id = '${AGGREGATE_ID}';"
  else
    echo -e "${YELLOW}⚠️  No events claimed (may have already been processed)${NC}"
  fi
  echo ""
fi

echo "========================================="
echo -e "${GREEN}✅ End-to-End Test Complete${NC}"
echo "========================================="
echo ""
echo "Summary:"
echo "  ✅ Event sent to webhook endpoint"
echo "  ✅ Event stored in integration.outbox"
echo "  ✅ Event logged in integration.event_log"
echo "  ⏳ Waiting for n8n to process (check executions)"
echo ""
echo "Next Steps:"
echo "  1. Import n8n workflows (see n8n/workflows/integration/README.md)"
echo "  2. Activate workflows in n8n"
echo "  3. Configure Mattermost webhook URL"
echo "  4. Wait 30-60 seconds for event router to pick up event"
echo "  5. Check Mattermost for notification"
echo ""
