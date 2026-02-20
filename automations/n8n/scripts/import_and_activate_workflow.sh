#!/usr/bin/env bash
set -euo pipefail

# Parse flags
CREATE_CREDS=false
ATTACH_CREDS=false
DRY_RUN=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --create-creds)
      CREATE_CREDS=true
      shift
      ;;
    --attach-creds)
      ATTACH_CREDS=true
      shift
      ;;
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    *)
      WORKFLOW_FILE="$1"
      shift
      ;;
  esac
done

: "${WORKFLOW_FILE:?Usage: $0 [--create-creds] [--attach-creds] [--dry-run] <workflow.json>}"
: "${N8N_BASE_URL:?N8N_BASE_URL not set}"
: "${N8N_API_KEY:?N8N_API_KEY not set}"

# Credential creation requires secrets
if [[ "$CREATE_CREDS" == "true" ]]; then
  : "${TELEGRAM_BOT_TOKEN:?TELEGRAM_BOT_TOKEN required for --create-creds}"
fi

# Dry-run mode prints planned API calls
if [[ "$DRY_RUN" == "true" ]]; then
  echo "🔍 DRY-RUN MODE (no actual API calls)"
  echo ""
fi

# Create credentials via API if requested
TELEGRAM_CRED_ID=""
if [[ "$CREATE_CREDS" == "true" ]]; then
  echo "📝 Creating Telegram credential via API..."

  TELEGRAM_CRED_PAYLOAD=$(jq -n \
    --arg token "${TELEGRAM_BOT_TOKEN}" \
    '{
      "name": "Telegram Bot OCR",
      "type": "telegramApi",
      "data": {
        "accessToken": $token
      }
    }')

  if [[ "$DRY_RUN" == "true" ]]; then
    echo "POST ${N8N_BASE_URL}/api/v1/credentials"
    echo "Body:"
    echo "${TELEGRAM_CRED_PAYLOAD}" | jq '.'
    TELEGRAM_CRED_ID="DRY_RUN_CRED_ID"
  else
    TELEGRAM_CRED_ID=$(curl -sS -X POST \
      -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
      -H "Content-Type: application/json" \
      -d "${TELEGRAM_CRED_PAYLOAD}" \
      "${N8N_BASE_URL}/api/v1/credentials" | jq -r '.id')

    echo "✅ Created Telegram credential ID: ${TELEGRAM_CRED_ID}"
  fi
fi

# Strip UI-only fields from workflow JSON
IMPORT_JSON="/tmp/$(basename "${WORKFLOW_FILE}" .json)_import.json"
jq 'del(.versionId, .meta.instanceId, .meta.templateId, .id) |
    walk(if type == "object" then del(.webhookId) else . end) |
    walk(if type == "object" and has("credentials") then
      .credentials |= with_entries(.value |= del(.id))
    else . end)' \
  "${WORKFLOW_FILE}" > "${IMPORT_JSON}"

# Attach credentials to workflow JSON if requested
if [[ "$ATTACH_CREDS" == "true" && -n "$TELEGRAM_CRED_ID" ]]; then
  echo "🔗 Attaching credential IDs to workflow nodes..."

  jq --arg cred_id "${TELEGRAM_CRED_ID}" '
    walk(
      if type == "object" and (.type == "n8n-nodes-base.telegramTrigger" or .type == "n8n-nodes-base.telegram") then
        .credentials.telegramApi.id = $cred_id |
        .credentials.telegramApi.name = "Telegram Bot OCR"
      else . end
    )' "${IMPORT_JSON}" > "${IMPORT_JSON}.tmp"

  mv "${IMPORT_JSON}.tmp" "${IMPORT_JSON}"
  echo "✅ Attached Telegram credential to nodes"
fi

# Import workflow
echo "📦 Importing workflow..."

if [[ "$DRY_RUN" == "true" ]]; then
  echo "POST ${N8N_BASE_URL}/api/v1/workflows"
  echo "Body: (sanitized workflow JSON)"
  WORKFLOW_ID="DRY_RUN_WORKFLOW_ID"
else
  WORKFLOW_ID=$(curl -sS -X POST \
    -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
    -H "Content-Type: application/json" \
    -d @"${IMPORT_JSON}" \
    "${N8N_BASE_URL}/api/v1/workflows" | jq -r '.id')

  echo "✅ Imported workflow ID: ${WORKFLOW_ID}"
fi

# Activate workflow
echo "🚀 Activating workflow..."

if [[ "$DRY_RUN" == "true" ]]; then
  echo "POST ${N8N_BASE_URL}/api/v1/workflows/${WORKFLOW_ID}/activate"
else
  curl -sS -X POST \
    -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
    "${N8N_BASE_URL}/api/v1/workflows/${WORKFLOW_ID}/activate"

  echo "✅ Activated workflow: ${N8N_BASE_URL}/workflow/${WORKFLOW_ID}"
fi

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 Workflow deployment complete"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Workflow URL: ${N8N_BASE_URL}/workflow/${WORKFLOW_ID}"

if [[ "$CREATE_CREDS" == "false" ]]; then
  echo ""
  echo "⚠️  Manual action required:"
  echo "   Attach Telegram credential to nodes in n8n UI"
  echo "   OR re-run with: --create-creds --attach-creds"
fi

if [[ "$CREATE_CREDS" == "true" && "$ATTACH_CREDS" == "false" ]]; then
  echo ""
  echo "⚠️  Credential created but not attached to workflow"
  echo "   Re-run with: --attach-creds to automate attachment"
fi

if [[ -n "$TELEGRAM_CRED_ID" && "$TELEGRAM_CRED_ID" != "DRY_RUN_CRED_ID" ]]; then
  echo ""
  echo "ℹ️  Known limitation:"
  echo "   Credentials created via API may land in personal space."
  echo "   If project-scoping is required, move credential via UI."
  echo "   See: https://community.n8n.io/t/n8n-api-creating-credentials-in-a-project/185779"
fi

echo ""
