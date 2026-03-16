# Gemini 2.5 Flash Update - CORRECTED

**Date**: 2026-02-21T03:10:00+0800
**Status**: ✅ COMPLETE
**Workflow ID**: `2gi85MdqffJ63p9x`

---

## Correction: Gemini Model Versions

**Previous Error**: Incorrectly stated that "Gemini 2.5 does not exist" and "Gemini 3 does not exist"

**Ground Truth** (per official Google AI documentation):
- ✅ **Gemini 2.5 Flash** exists - Model ID: `gemini-2.5-flash`
- ✅ **Gemini 3.1 Pro Preview** exists - Model ID: `gemini-3.1-pro-preview`

**Sources**:
- Gemini 2.5 Flash: https://ai.google.dev/gemini-api/docs/models/gemini-2.5-flash
- Gemini 3.1 Pro Preview: https://ai.google.dev/gemini-api/docs/models/gemini-3.1-pro-preview
- Models overview: https://ai.google.dev/gemini-api/docs/models

---

## Model Selection for OCR Workflow

**Recommendation**: Use **`gemini-2.5-flash`** for OCR workflows (per Google AI documentation)

**Rationale**:
- **Speed**: Low latency multimodal processing
- **Cost**: More cost-effective than Pro models
- **Performance**: Strong multimodal throughput
- **"Thinking" capability**: Enhanced reasoning for complex OCR tasks

**Alternative**: `gemini-3.1-pro-preview`
- Use only if maximum accuracy/grounding required
- Higher latency and cost
- Better for complex/agentic workflows (not typical OCR)

**Decision**: Selected **`gemini-2.5-flash`** for Telegram OCR workflow

---

## Update Process

### Step 1: Fetch Current Workflow

```bash
curl -s -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  "https://n8n.insightpulseai.com/api/v1/workflows/2gi85MdqffJ63p9x"
```

**Current State**:
```json
{
  "name": "MCP Tool: Telegram OCR with Gemini 3.1 Pro",
  "nodes": [
    {
      "name": "Gemini 2.0 Flash OCR",
      "type": "@n8n/n8n-nodes-langchain.lmChatGoogleGemini",
      "parameters": {
        "modelName": "gemini-3.1-pro-preview"
      }
    }
  ]
}
```

### Step 2: Update to Gemini 2.5 Flash

**Changed Fields**:
1. Workflow name: `"MCP Tool: Telegram OCR with Gemini 2.5 Flash"`
2. Model parameter: `"modelName": "gemini-2.5-flash"`
3. Node name: `"Gemini 2.5 Flash OCR"`

**Update Request**:
```bash
curl -X PUT \
  -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "MCP Tool: Telegram OCR with Gemini 2.5 Flash",
    "nodes": [
      {
        "name": "Gemini 2.5 Flash OCR",
        "type": "@n8n/n8n-nodes-langchain.lmChatGoogleGemini",
        "parameters": {
          "modelName": "gemini-2.5-flash"
        }
      }
    ],
    "connections": {...},
    "settings": {...}
  }' \
  "https://n8n.insightpulseai.com/api/v1/workflows/2gi85MdqffJ63p9x"
```

**Response**: HTTP 200 (Success)

### Step 3: Verify Persistence

```bash
curl -s -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  "https://n8n.insightpulseai.com/api/v1/workflows/2gi85MdqffJ63p9x" | \
  jq -r '.nodes[] | select(.type == "@n8n/n8n-nodes-langchain.lmChatGoogleGemini") | .parameters.modelName'
```

**Output**: `gemini-2.5-flash`

✅ **Verification**: Model change persisted successfully

---

## JSON Diff (Before → After)

### Before
```json
{
  "name": "Gemini 2.0 Flash OCR",
  "type": "@n8n/n8n-nodes-langchain.lmChatGoogleGemini",
  "parameters": {
    "modelName": "gemini-3.1-pro-preview"
  }
}
```

### After
```json
{
  "name": "Gemini 2.5 Flash OCR",
  "type": "@n8n/n8n-nodes-langchain.lmChatGoogleGemini",
  "parameters": {
    "modelName": "gemini-2.5-flash"
  }
}
```

### Diff Summary
```diff
- "modelName": "gemini-3.1-pro-preview"
+ "modelName": "gemini-2.5-flash"

- "name": "Gemini 2.0 Flash OCR"
+ "name": "Gemini 2.5 Flash OCR"
```

---

## Credential Configuration (API-First Approach)

**API Key Provided**: `AIzaSyCpotW0q81UxWvq40_G4Qs2P_BoGXpQXVw`

**Status**: ⏳ BLOCKED by n8n API limitation

**Technical Constraint**: n8n Public API (v2.2.4) does **not** support:
- `POST /api/v1/credentials` (credential creation)
- `GET /api/v1/credentials/schema/{type}` (schema retrieval)

**Workaround**: Credentials must be provisioned via n8n UI, then workflow JSON can be patched with credential IDs and updated via API.

### API-First Provisioning Workflow

**Step 1: Provision Credentials (UI-constrained)**

Create credentials via n8n UI (https://n8n.insightpulseai.com/credentials):

| Credential Type | Name | Environment Variable | Node Dependencies |
|----------------|------|---------------------|-------------------|
| `googlePalmApi` | Google Gemini 2.5 Flash API | `GEMINI_API_KEY` | Gemini 2.5 Flash OCR |
| `telegramApi` | Telegram Bot OCR | `TELEGRAM_BOT_TOKEN` | Telegram Trigger, Get Photo URL, Download Photo, Send Response |

**Step 2: Record Credential IDs**

After UI creation, extract credential IDs from n8n UI URLs or API (if supported in future):
```bash
# Example credential ID format
GEMINI_CRED_ID="abc123xyz"
TELEGRAM_CRED_ID="def456uvw"
```

**Step 3: Patch Workflow JSON with Credential References**

Update workflow export to include credential attachments:

```bash
# Fetch current workflow
curl -s -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  "https://n8n.insightpulseai.com/api/v1/workflows/2gi85MdqffJ63p9x" > workflow.json

# Patch Gemini node with credential
jq '
  .nodes |= map(
    if .id == "gemini-ocr" then
      .credentials = {
        "googlePalmApi": {
          "id": env.GEMINI_CRED_ID,
          "name": "Google Gemini 2.5 Flash API"
        }
      }
    else . end
  )
' workflow.json > workflow_patched.json

# Update workflow via API
curl -X PUT \
  -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  -H "Content-Type: application/json" \
  -d @workflow_patched.json \
  "https://n8n.insightpulseai.com/api/v1/workflows/2gi85MdqffJ63p9x"
```

**Step 4: Verify Credential Attachment**

```bash
# Check Gemini credential attached
curl -s -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  "https://n8n.insightpulseai.com/api/v1/workflows/2gi85MdqffJ63p9x" | \
  jq '.nodes[] | select(.id == "gemini-ocr") | .credentials'

# Expected output
{
  "googlePalmApi": {
    "id": "abc123xyz",
    "name": "Google Gemini 2.5 Flash API"
  }
}
```

**Step 5: Activate Workflow via API**

```bash
# Activate workflow (if API supports)
curl -X PATCH \
  -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"active": true}' \
  "https://n8n.insightpulseai.com/api/v1/workflows/2gi85MdqffJ63p9x"
```

---

## Verification Checklist

- [x] Fetch workflow definition and confirm model = `gemini-2.5-flash`
- [x] Verify change persisted after update
- [x] No other nodes reference old model (`gemini-2.0-flash` or `gemini-3.1-pro-preview`)
- [x] Workflow name updated to reflect correct model version
- [x] Node name updated to match model version
- [ ] Credential provisioned via n8n UI (API limitation - UI step required)
- [ ] Credential ID extracted from n8n UI or API response
- [ ] Workflow JSON patched with credential reference (node: `gemini-ocr`)
- [ ] Updated workflow via `PUT /api/v1/workflows/{id}` with patched JSON
- [ ] Verified credential attachment via `GET /api/v1/workflows/{id}` → check `.nodes[].credentials`
- [ ] Workflow activated via API (or UI if API doesn't support activation)
- [ ] Test execution with real Telegram photo (requires active workflow + credential)
- [ ] Verify logs show `gemini-2.5-flash` in API request (requires execution)

---

## Final Workflow State

**Workflow ID**: `2gi85MdqffJ63p9x`
**Name**: MCP Tool: Telegram OCR with Gemini 2.5 Flash
**Model**: `gemini-2.5-flash`
**Active**: `false` (pending credential configuration)
**URL**: https://n8n.insightpulseai.com/workflow/2gi85MdqffJ63p9x

**Nodes**: 10
1. Telegram Trigger (webhook) - **requires credential**: `telegramApi`
2. Filter Photos Only
3. Get Telegram Photo URL - **requires credential**: `telegramApi`
4. Download Photo - **requires credential**: `telegramApi`
5. **Gemini 2.5 Flash OCR** (model: `gemini-2.5-flash`) - **requires credential**: `googlePalmApi`
6. Extract Text Chain (LangChain LLM)
7. Classify Document Type (8 categories)
8. Format Telegram Response
9. Send Telegram Response - **requires credential**: `telegramApi`
10. Log to Supabase (ops_run_events) - uses env vars (`SUPABASE_URL`, `SUPABASE_SERVICE_KEY`)

**Credential Dependencies**: See `automations/n8n/workflows/claude-ai-mcp/meta/CREDENTIAL_WIRING.md` for complete specification.

---

## Evidence

### Model Verification Query
```bash
curl -s -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  "https://n8n.insightpulseai.com/api/v1/workflows/2gi85MdqffJ63p9x" | \
  jq '{
    id,
    name,
    active,
    gemini_node: (.nodes[] | select(.type == "@n8n/n8n-nodes-langchain.lmChatGoogleGemini") | {
      name,
      model: .parameters.modelName,
      credentials
    })
  }'
```

### Output
```json
{
  "id": "2gi85MdqffJ63p9x",
  "name": "MCP Tool: Telegram OCR with Gemini 2.5 Flash",
  "active": false,
  "gemini_node": {
    "name": "Gemini 2.5 Flash OCR",
    "model": "gemini-2.5-flash",
    "credentials": null
  }
}
```

✅ **Model Confirmed**: Workflow uses correct Gemini 2.5 Flash model
⚠️ **Credentials Status**: `null` (pending provisioning and attachment)

---

## Status Summary

✅ **Model Update**: COMPLETE (gemini-2.5-flash)
✅ **Workflow Name Update**: COMPLETE
✅ **Node Name Update**: COMPLETE
✅ **Persistence Verification**: COMPLETE
⏳ **Credential Provisioning**: BLOCKED (n8n API limitation - requires UI)
⏳ **Credential Attachment**: PENDING (requires Step 3 of API-First workflow)
⏳ **Workflow Activation**: PENDING (requires credential attachment)
⏳ **Production Testing**: PENDING (requires active workflow)

---

## Next Steps (API-First with UI Constraint)

1. **Provision Credentials** (UI-constrained step):
   - Navigate to: https://n8n.insightpulseai.com/credentials
   - Create `Google Gemini 2.5 Flash API` credential (type: `googlePalmApi`)
   - Create `Telegram Bot OCR` credential (type: `telegramApi`)
   - Record credential IDs from UI or API response

2. **Patch and Update Workflow** (API-first):
   - Fetch workflow JSON via `GET /api/v1/workflows/2gi85MdqffJ63p9x`
   - Patch `.nodes[].credentials` with credential IDs using jq
   - Update workflow via `PUT /api/v1/workflows/2gi85MdqffJ63p9x`
   - Verify credential attachment via `GET` request

3. **Activate and Test** (API-first with fallback):
   - Activate via API: `PATCH /api/v1/workflows/{id}` with `{"active": true}`
   - Test: Send photo to Telegram bot
   - Verify: Check Supabase `ops_run_events` for execution log
   - Validate: Confirm model = `gemini-2.5-flash` in execution metadata

4. **Monitoring** (API-driven):
   - Query execution logs: `GET /api/v1/executions?workflowId=2gi85MdqffJ63p9x`
   - Track OCR accuracy via Supabase analytics queries
   - Compare performance metrics (latency, confidence) vs previous models

---

## Apology and Correction

I apologize for the earlier incorrect statements that:
- "Gemini 2.5 does not exist" (FALSE - it exists as `gemini-2.5-flash`)
- "Gemini 3 does not exist" (FALSE - it exists as `gemini-3.1-pro-preview`)

The correct information is now documented above with official Google AI documentation citations. All workflow updates and documentation have been corrected to reflect the accurate model names and capabilities.
