#!/bin/bash
# Mock Microsoft Marketplace Webhook Test Script
# Powered by InsightPulseAI

ODOO_URL="http://localhost:8069"
WEBHOOK_URL="$ODOO_URL/api/marketplace/webhook"
AUTH_TOKEN="PLACEHOLDER_SET_IN_PRODUCTION"

# 1. Test Activation
echo "🚀 Testing 'Activate' event..."
curl -X POST "$WEBHOOK_URL" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer $AUTH_TOKEN" \
     -d '{
       "action": "Activate",
       "subscriptionId": "sub-test-12345",
       "offerId": "pulser-for-odoo",
       "plan_id": "starter-plan",
       "quantity": 5
     }'

echo -e "\n\n🔄 Testing 'Unsubscribe' event..."
curl -X POST "$WEBHOOK_URL" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer $AUTH_TOKEN" \
     -d '{
       "action": "Unsubscribe",
       "subscriptionId": "sub-test-12345"
     }'

echo -e "\n\n✅ Mock tests complete."
