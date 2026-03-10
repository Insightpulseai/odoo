#!/usr/bin/env bash
# Odoo Copilot — Azure Bot Service Registration (F0 free tier)
# Registers a bot with Azure Bot Service pointing to n8n webhook.
# No hosting — n8n handles all bot logic.
#
# Prerequisites:
#   - az CLI authenticated
#   - Resource group exists
#
# Usage: ./scripts/azure/deploy-bot-service.sh

set -euo pipefail

RESOURCE_GROUP="${AZURE_RESOURCE_GROUP:-ipai-rg}"
BOT_NAME="${AZURE_BOT_NAME:-ipai-openbrain-bot}"
LOCATION="${AZURE_LOCATION:-southeastasia}"
N8N_ENDPOINT="https://n8n.insightpulseai.com/webhook/teams-bot-activity"

echo "=== Odoo Copilot: Azure Bot Service Registration ==="

# Check az CLI
if ! command -v az &>/dev/null; then
    echo "ERROR: az CLI not found. Install: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Create resource group if missing
az group create --name "$RESOURCE_GROUP" --location "$LOCATION" --output none 2>/dev/null || true

# Create bot registration (F0 = free tier, registration only)
echo "Creating bot registration: $BOT_NAME"
az bot create \
    --resource-group "$RESOURCE_GROUP" \
    --name "$BOT_NAME" \
    --kind registration \
    --sku F0 \
    --endpoint "$N8N_ENDPOINT" \
    --description "Odoo Copilot by InsightPulse AI" \
    --output json

# Enable Teams channel
echo "Enabling Teams channel..."
az bot msteams create \
    --resource-group "$RESOURCE_GROUP" \
    --name "$BOT_NAME" \
    --output json

# Show bot details
echo ""
echo "=== Bot Registration Complete ==="
az bot show \
    --resource-group "$RESOURCE_GROUP" \
    --name "$BOT_NAME" \
    --query "{name:name, endpoint:properties.endpoint, appId:properties.msaAppId}" \
    --output table

echo ""
echo "Next: Set MicrosoftAppId and MicrosoftAppPassword in n8n credentials."
echo "The MicrosoftAppId is shown above. Get the password from Azure Portal → App registrations."
