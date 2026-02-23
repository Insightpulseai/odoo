#!/usr/bin/env bash
set -euo pipefail

WORKFLOW_FILE="${1:?Usage: $0 <workflow.json>}"
: "${N8N_BASE_URL:?N8N_BASE_URL not set}"
: "${N8N_API_KEY:?N8N_API_KEY not set}"

# Strip UI-only fields
IMPORT_JSON="/tmp/$(basename "${WORKFLOW_FILE}" .json)_import.json"
jq 'del(.versionId, .meta.instanceId, .meta.templateId, .id) |
    walk(if type == "object" then del(.webhookId) else . end) |
    walk(if type == "object" and has("credentials") then
      .credentials |= with_entries(.value |= del(.id))
    else . end)' \
  "${WORKFLOW_FILE}" > "${IMPORT_JSON}"

# Import
WORKFLOW_ID=$(curl -sS -X POST \
  -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  -H "Content-Type: application/json" \
  -d @"${IMPORT_JSON}" \
  "${N8N_BASE_URL}/api/v1/workflows" | jq -r '.id')

echo "✅ Imported workflow ID: ${WORKFLOW_ID}"

# Activate
curl -sS -X POST \
  -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  "${N8N_BASE_URL}/api/v1/workflows/${WORKFLOW_ID}/activate"

echo "✅ Activated workflow: ${N8N_BASE_URL}/workflow/${WORKFLOW_ID}"
echo "⚠️  [MANUAL] Attach Telegram credentials to nodes (see TELEGRAM_OCR_IMPLEMENTATION.md)"
