# n8n Credential Wiring Specification

**Purpose**: Define credential requirements for MCP meta workflows without exposing secrets in git.

**Status**: Credential provisioning requires n8n UI (Public API limitation as of n8n 2.2.4)

---

## Required Credentials

### 1. Google Gemini API

**Credential Type**: `googlePalmApi` (LangChain Google Gemini)
**Environment Variable**: `GEMINI_API_KEY`
**Required For**:
- Workflow #11 (Telegram OCR)
  - Node: `Gemini 2.5 Flash OCR` (id: `gemini-ocr`)
  - Type: `@n8n/n8n-nodes-langchain.lmChatGoogleGemini`

**Data Schema**:
```json
{
  "apiKey": "${GEMINI_API_KEY}"
}
```

---

### 2. Telegram API

**Credential Type**: `telegramApi`
**Environment Variable**: `TELEGRAM_BOT_TOKEN`
**Required For**:
- Workflow #11 (Telegram OCR)
  - Node: `Telegram Trigger` (id: `telegram-trigger`)
  - Node: `Get Telegram Photo URL` (id: `get-photo-url`)
  - Node: `Download Photo` (id: `download-photo`)
  - Node: `Send Telegram Response` (id: `send-telegram-response`)

**Data Schema**:
```json
{
  "accessToken": "${TELEGRAM_BOT_TOKEN}"
}
```

---

### 3. OpenAI API

**Credential Type**: `openAiApi`
**Environment Variable**: `OPENAI_API_KEY`
**Required For**:
- Workflow #10 (Monitor & Debugger)
  - Node: `OpenAI GPT-4` (id: `openai-model`)
  - Type: `@n8n/n8n-nodes-langchain.lmChatOpenAi`

**Data Schema**:
```json
{
  "apiKey": "${OPENAI_API_KEY}"
}
```

---

### 4. Slack API

**Credential Type**: `slackApi`
**Environment Variables**:
- `SLACK_BOT_TOKEN` (OAuth Bot Token)
- `SLACK_CHANNEL_ID` (for #n8n-alerts)

**Required For**:
- Workflow #10 (Monitor & Debugger)
  - Node: `Send Slack Alert` (id: `send-slack-alert`)

**Data Schema**:
```json
{
  "authentication": "accessToken",
  "accessToken": "${SLACK_BOT_TOKEN}"
}
```

**Channel Configuration**:
- Channel: `#n8n-alerts`
- Channel ID: `C07S0NQ04D7` (hardcoded in workflow)

---

### 5. Supabase API

**Credential Type**: `supabaseApi`
**Environment Variables**:
- `SUPABASE_URL`
- `SUPABASE_SERVICE_KEY`

**Required For**:
- Workflow #10 (Monitor & Debugger)
  - Node: `Log to Supabase` (id: `log-to-supabase`)
- Workflow #11 (Telegram OCR)
  - Node: `Log to Supabase` (id: `log-to-supabase`)

**Data Schema**:
```json
{
  "host": "${SUPABASE_URL}",
  "serviceRole": "${SUPABASE_SERVICE_KEY}"
}
```

**Note**: Both workflows use environment variables in HTTP Request nodes rather than credential objects for Supabase authentication.

---

### 6. n8n API

**Credential Type**: `n8nApi`
**Environment Variables**:
- `N8N_BASE_URL`
- `N8N_API_KEY`

**Required For**:
- Workflow #10 (Monitor & Debugger)
  - Node: `Get Recent Executions` (id: `get-recent-executions`)
  - Node: `Get Execution Details` (id: `get-execution-details`)

**Data Schema**:
```json
{
  "baseUrl": "${N8N_BASE_URL}",
  "apiKey": "${N8N_API_KEY}"
}
```

**Note**: Both nodes use HTTP Request with manual header authentication rather than credential objects.

---

## Credential Attachment Pattern

### For LangChain AI Nodes

LangChain nodes (Gemini, OpenAI) require credentials in this format:

```json
{
  "id": "gemini-ocr",
  "name": "Gemini 2.5 Flash OCR",
  "type": "@n8n/n8n-nodes-langchain.lmChatGoogleGemini",
  "credentials": {
    "googlePalmApi": {
      "id": "CREDENTIAL_ID_FROM_N8N",
      "name": "Google Gemini 2.5 Flash API"
    }
  },
  "parameters": {
    "modelName": "gemini-2.5-flash"
  }
}
```

### For Standard Nodes

Standard nodes (Telegram, Slack) require credentials in this format:

```json
{
  "id": "telegram-trigger",
  "name": "Telegram Trigger",
  "type": "n8n-nodes-base.telegramTrigger",
  "credentials": {
    "telegramApi": {
      "id": "CREDENTIAL_ID_FROM_N8N",
      "name": "Telegram Bot OCR"
    }
  },
  "parameters": {
    "updates": ["message"]
  }
}
```

### For HTTP Request Nodes with Predefined Credentials

HTTP Request nodes using `authentication: "predefinedCredentialType"`:

```json
{
  "id": "download-photo",
  "name": "Download Photo",
  "type": "n8n-nodes-base.httpRequest",
  "credentials": {
    "telegramApi": {
      "id": "CREDENTIAL_ID_FROM_N8N",
      "name": "Telegram Bot OCR"
    }
  },
  "parameters": {
    "authentication": "predefinedCredentialType",
    "nodeCredentialType": "telegramApi"
  }
}
```

---

## Provisioning Workflow (UI-Required)

**API Limitation**: n8n Public API (as of v2.2.4) does **not** support:
- `POST /api/v1/credentials` (credential creation)
- `GET /api/v1/credentials/schema/{type}` (schema retrieval)

**Required Steps** (n8n UI):

1. **Navigate to Credentials**: https://n8n.insightpulseai.com/credentials

2. **Create Each Credential**:
   - Google Gemini: Name = `Google Gemini 2.5 Flash API`
   - Telegram Bot: Name = `Telegram Bot OCR`
   - OpenAI: Name = `OpenAI GPT-4 API`
   - Slack: Name = `Slack n8n Alerts`
   - Supabase: Name = `Supabase Production` (if using credential object)
   - n8n API: Name = `n8n Internal API` (if using credential object)

3. **Record Credential IDs**: After creation, note the credential ID from URL (e.g., `https://n8n.insightpulseai.com/credentials/123`)

4. **Patch Workflow JSONs**: Update workflow exports with credential references using IDs from step 3

5. **Import Updated Workflows**: Use `PUT /api/v1/workflows/{id}` with patched JSON

---

## Verification Commands

### Check Credential Attachment (via API)

```bash
# Workflow #11 - Check Gemini credential
curl -s -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  "https://n8n.insightpulseai.com/api/v1/workflows/2gi85MdqffJ63p9x" | \
  jq '.nodes[] | select(.id == "gemini-ocr") | .credentials'

# Workflow #11 - Check Telegram credential
curl -s -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  "https://n8n.insightpulseai.com/api/v1/workflows/2gi85MdqffJ63p9x" | \
  jq '.nodes[] | select(.id == "telegram-trigger") | .credentials'

# Workflow #10 - Check OpenAI credential
curl -s -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  "https://n8n.insightpulseai.com/api/v1/workflows/0gc957bCR1V63lLS" | \
  jq '.nodes[] | select(.id == "openai-model") | .credentials'
```

### Expected Output (after credential wiring)

```json
{
  "googlePalmApi": {
    "id": "abc123",
    "name": "Google Gemini 2.5 Flash API"
  }
}
```

---

## Environment Variables (for reference)

**Never commit these to git.** Store in:
- Local: `~/.zshrc` or `.env.local`
- CI: GitHub Actions secrets
- Runtime: n8n environment settings

```bash
# Google Gemini
export GEMINI_API_KEY="AIzaSy..."

# Telegram
export TELEGRAM_BOT_TOKEN="123456:ABC..."

# OpenAI
export OPENAI_API_KEY="sk-..."

# Slack
export SLACK_BOT_TOKEN="xoxb-..."
export SLACK_CHANNEL_ID="C07S0NQ04D7"

# Supabase
export SUPABASE_URL="https://spdtwktxdalcfigzeqrz.supabase.co"
export SUPABASE_SERVICE_KEY="eyJhbG..."

# n8n
export N8N_BASE_URL="https://n8n.insightpulseai.com"
export N8N_API_KEY="eyJhbG..."
```

---

## Status Summary

| Credential Type | Status | Workflow Dependencies |
|----------------|--------|----------------------|
| Google Gemini | ⏳ UI provisioning required | Workflow #11 (1 node) |
| Telegram API | ⏳ UI provisioning required | Workflow #11 (4 nodes) |
| OpenAI API | ⏳ UI provisioning required | Workflow #10 (1 node) |
| Slack API | ⏳ UI provisioning required | Workflow #10 (1 node) |
| Supabase API | ℹ️ Using env vars in HTTP nodes | Workflow #10, #11 (2 nodes) |
| n8n API | ℹ️ Using env vars in HTTP nodes | Workflow #10 (2 nodes) |

**Next**: Provision credentials via n8n UI → Patch workflow JSONs → Update via API → Verify attachment
