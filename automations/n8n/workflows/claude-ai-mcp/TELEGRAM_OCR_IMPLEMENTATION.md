# Telegram OCR Implementation Guide

## Overview

Complete Telegram bot integration with Gemini 2.5 Flash OCR and Supabase logging.

**Flow**: Telegram Photo → Gemini OCR → JSON Parse → Supabase Log → Reply

## Architecture

```
Telegram Bot (@Odoo_etl_vibe_bot)
    ↓
Telegram Trigger (download photo)
    ↓
Clean Input Data (extract chatID, file_id)
    ↓
Get File (Telegram API)
    ↓
Extract from File (binary → base64)
    ↓
Gemini OCR (gemini-2.5-flash with structured JSON prompt)
    ↓
Parse Gemini JSON (Code node: JSON.parse with error handling)
    ↓
Supabase Log OCR Event (POST /rpc/log_ocr_event)
    ↓
Telegram Reply (formatted summary + JSON or error)
```

## Required Environment Variables

```bash
# Gemini API
GEMINI_API_KEY="AIzaSyCpotW0q81UxWvq40_G4Qs2P_BoGXpQXVw"

# Supabase (REQUIRED: service_role key for RPC security definer)
SUPABASE_URL="https://spdtwktxdalcfigzeqrz.supabase.co"
SUPABASE_SERVICE_ROLE_KEY="eyJhbGc..." # REQUIRED for ops.log_ocr_event RPC

# n8n (for workflow management)
N8N_BASE_URL="https://n8n.insightpulseai.com"
N8N_API_KEY="eyJhbGc..."
```

**⚠️ Authentication Note**: The Supabase Log OCR Event node **requires** `SUPABASE_SERVICE_ROLE_KEY`, not `SUPABASE_ANON_KEY`. The `ops.log_ocr_event` RPC function is `security definer` and has `revoke all from public`, so anon key access will fail with 401 Unauthorized.

## Workflow JSON Schema

**Output Format** (from Gemini OCR):

```json
{
  "ok": true,
  "doc_type": "receipt",
  "merchant": {
    "name": "ABC Restaurant",
    "tax_id": "123-456-789",
    "address": "123 Main St",
    "phone": "+63 2 1234 5678"
  },
  "transaction": {
    "date": "2026-02-21",
    "time": "14:30:00",
    "currency": "PHP",
    "total": 1250.00,
    "subtotal": 1150.00,
    "tax": 100.00,
    "service": null,
    "discount": null
  },
  "payment": {
    "method": "cash",
    "card_last4": null,
    "auth_code": null
  },
  "items": [
    {
      "name": "Chicken Adobo",
      "qty": 2,
      "unit_price": 250.00,
      "amount": 500.00
    },
    {
      "name": "Rice",
      "qty": 3,
      "unit_price": 50.00,
      "amount": 150.00
    }
  ],
  "raw_text": "ABC RESTAURANT\n123 Main St\n...",
  "confidence": 0.95
}
```

**Error Format**:

```json
{
  "ok": false,
  "error": "JSON parse failed",
  "text": "raw Gemini response that failed to parse",
  "raw": { /* original Gemini API response */ }
}
```

## Database Schema

**Table**: `ops.ocr_events`

```sql
create table ops.ocr_events (
  id uuid primary key default gen_random_uuid(),
  source text not null,           -- 'telegram'
  chat_id text null,               -- Telegram chat ID
  file_id text null,               -- Telegram file_id
  doc_type text not null,          -- 'receipt'|'invoice'|'parse_error'
  payload jsonb not null,          -- Full parsed JSON
  created_at timestamptz not null default now()
);
```

**RPC**: `ops.log_ocr_event(source, chat_id, file_id, doc_type, payload) → uuid`

## Deployment Steps

### 1. Apply Supabase Migration

```bash
cd supabase
supabase db push
# Or manually run migration:
# psql "$POSTGRES_URL" < migrations/20260221000000_ocr_events.sql
```

### 2. Import Workflow to n8n (API-First)

**⚠️ Important**: Strip UI-only fields from workflow JSON before API import. The following fields are instance-specific and must be removed:

- `versionId` (root level)
- `meta.instanceId` (root level)
- `meta.templateId` (optional, but instance-specific)
- `id` (root level, workflow ID)
- `webhookId` (in Telegram Trigger node)
- `credentials.*.id` (credential IDs are instance-specific)

**Prepare workflow JSON for import:**

```bash
# Create API-importable version
jq 'del(.versionId, .meta.instanceId, .meta.templateId, .id) |
    walk(if type == "object" then del(.webhookId) else . end) |
    walk(if type == "object" and has("credentials") then
      .credentials |= with_entries(.value |= del(.id))
    else . end)' \
  automations/n8n/workflows/claude-ai-mcp/11_telegram_ocr_gemini_complete.json \
  > /tmp/telegram_ocr_import.json
```

**Import via n8n Public API:**

```bash
# Import workflow
WORKFLOW_ID=$(curl -sS -X POST \
  -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  -H "Content-Type: application/json" \
  -d @/tmp/telegram_ocr_import.json \
  "${N8N_BASE_URL}/api/v1/workflows" | jq -r '.id')

echo "Imported workflow ID: ${WORKFLOW_ID}"

# Activate workflow
curl -sS -X POST \
  -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  "${N8N_BASE_URL}/api/v1/workflows/${WORKFLOW_ID}/activate"
```

**[MANUAL_REQUIRED] Credential Attachment**:
- **What**: Attach Telegram Bot credential to workflow nodes
- **Why**: n8n Public API doesn't support credential creation/management (platform limitation)
- **Evidence**: n8n API docs, 405 Method Not Allowed on POST /credentials
- **Minimal human action**:
  1. Open `${N8N_BASE_URL}/workflow/${WORKFLOW_ID}`
  2. For each Telegram node (Trigger, Get File, Reply):
     - Click node → Credentials dropdown
     - Select "Telegram Bot OCR" (or create new with token: `8221767220:AAGJdtPu9RRiH12_AoM6XmSdaPoy5pdIPqY`)
  3. Save workflow
- **Then**: Automation resumes with testing (step 3)

**Helper Script** (optional but recommended):

Create `automations/n8n/scripts/import_and_activate_workflow.sh`:

```bash
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
```

### 3. Test End-to-End

1. Send a photo of a receipt to `@Odoo_etl_vibe_bot` on Telegram
2. Expected reply:
   ```
   ✅ Parsed
   Merchant: ABC Restaurant
   Total: 1250.00 PHP
   Date: 2026-02-21

   JSON:
   {"ok":true,"doc_type":"receipt",...}
   ```

3. Verify Supabase logging:
   ```sql
   select id, source, chat_id, doc_type,
          payload->'merchant'->>'name' as merchant,
          payload->'transaction'->>'total' as total,
          created_at
   from ops.ocr_events
   order by created_at desc
   limit 5;
   ```

## Troubleshooting

### Gemini OCR Returns Error

**Symptom**: Telegram reply shows parse error

**Debug**:
1. Check `ops.ocr_events` for `doc_type='parse_error'`
2. Inspect `payload.text` (raw Gemini response)
3. Common issues:
   - Image quality too low
   - Non-receipt/invoice images
   - Gemini returned markdown instead of JSON

**Fix**: Improve prompt or add pre-validation

### Supabase Log Fails

**Symptom**: Workflow execution stops at Supabase node with 401 Unauthorized or permission denied

**Root Cause**: The `ops.log_ocr_event` RPC function is defined as `security definer` with `revoke all on function ops.log_ocr_event(...) from public`. This means:

1. **Service role key is REQUIRED** — anon key will always fail with 401
2. **RLS does NOT apply** — function runs with definer's privileges (schema owner)
3. **No public grants** — only service role can execute

**Debug**:
1. Check n8n execution logs for HTTP 401 or "permission denied for function"
2. Verify n8n environment variable:
   ```bash
   # In n8n settings → Environments → SUPABASE_SERVICE_ROLE_KEY
   # Must start with: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS...
   ```
3. Common issues:
   - Using `SUPABASE_ANON_KEY` instead of `SUPABASE_SERVICE_ROLE_KEY`
   - RPC `log_ocr_event` not created (migration not applied)
   - Wrong Supabase project URL

**Fix**:
```bash
# 1. Verify migration applied
psql "$POSTGRES_URL" -c "\df ops.log_ocr_event"
# Expected output: ops | log_ocr_event | uuid | plpgsql

# 2. Test RPC directly with service_role key
curl -sS -X POST \
  -H "apikey: ${SUPABASE_SERVICE_ROLE_KEY}" \
  -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "telegram",
    "chat_id": "test_123",
    "file_id": "test_file",
    "doc_type": "other",
    "payload": {"test": true}
  }' \
  "${SUPABASE_URL}/rest/v1/rpc/log_ocr_event"

# 3. If test succeeds but workflow fails, check n8n Supabase node config:
# - URL: {{$env.SUPABASE_URL}}/rest/v1/rpc/log_ocr_event
# - Headers: apikey={{$env.SUPABASE_SERVICE_ROLE_KEY}}
# - Headers: Authorization=Bearer {{$env.SUPABASE_SERVICE_ROLE_KEY}}
```

### Telegram Credentials Missing

**Symptom**: Red "Select Credential" on Telegram nodes after API import

**Root Cause**: n8n Public API doesn't support credential creation/management (platform limitation, confirmed 405 Method Not Allowed on POST /credentials)

**Fix** [MANUAL_REQUIRED]: Attach credentials via n8n UI:
1. Open workflow in n8n web UI: `${N8N_BASE_URL}/workflow/${WORKFLOW_ID}`
2. For each Telegram node (Trigger, Get File, Reply):
   - Click node → Credentials dropdown
   - Select existing "Telegram Bot OCR" credential
   - OR create new:
     - Name: "Telegram Bot OCR"
     - Access Token: `8221767220:AAGJdtPu9RRiH12_AoM6XmSdaPoy5pdIPqY`
     - Base URL: (leave default)
3. Save workflow

**Note**: This is the ONLY manual UI step required. All other operations (import, activate, test) are API-driven.

## Next Steps

### 1. Add Receipt Deduplication

Extend `log_ocr_event` to compute hash and check for duplicates:

```sql
create or replace function ops.log_ocr_event(...)
returns jsonb -- Changed from uuid
as $$
declare
  v_hash text;
  v_existing_id uuid;
  v_new_id uuid;
begin
  -- Compute hash from merchant + date + total
  v_hash := encode(
    digest(
      coalesce(payload->>'merchant', '') ||
      coalesce(payload->'transaction'->>'date', '') ||
      coalesce(payload->'transaction'->>'total', ''),
      'sha256'
    ),
    'hex'
  );

  -- Check for existing
  select id into v_existing_id
  from ops.ocr_events
  where payload->>'receipt_hash' = v_hash
  limit 1;

  if v_existing_id is not null then
    return jsonb_build_object('id', v_existing_id, 'deduped', true);
  end if;

  -- Insert new with hash
  insert into ops.ocr_events(source, chat_id, file_id, doc_type, payload)
  values (
    log_ocr_event.source,
    log_ocr_event.chat_id,
    log_ocr_event.file_id,
    log_ocr_event.doc_type,
    payload || jsonb_build_object('receipt_hash', v_hash)
  )
  returning id into v_new_id;

  return jsonb_build_object('id', v_new_id, 'deduped', false);
end;
$$;
```

### 2. Add Structured Receipt Table

Create normalized receipt storage:

```sql
create table ops.receipts (
  id uuid primary key default gen_random_uuid(),
  event_id uuid references ops.ocr_events(id),
  merchant_name text,
  merchant_tax_id text,
  transaction_date date,
  total numeric,
  currency text,
  items jsonb,
  created_at timestamptz default now()
);

-- Trigger to auto-populate from ocr_events
create function ops.sync_receipt_from_event()
returns trigger as $$
begin
  if NEW.doc_type = 'receipt' and NEW.payload->>'ok' = 'true' then
    insert into ops.receipts (event_id, merchant_name, ...)
    values (
      NEW.id,
      NEW.payload->'merchant'->>'name',
      ...
    );
  end if;
  return NEW;
end;
$$ language plpgsql;

create trigger sync_receipt
after insert on ops.ocr_events
for each row execute function ops.sync_receipt_from_event();
```

### 3. Add Business Intelligence

Query patterns:

```sql
-- Top merchants by transaction count
select
  payload->'merchant'->>'name' as merchant,
  count(*) as transactions,
  sum((payload->'transaction'->>'total')::numeric) as total_spent
from ops.ocr_events
where doc_type = 'receipt'
  and payload->>'ok' = 'true'
group by merchant
order by total_spent desc
limit 10;

-- Daily expense trends
select
  date_trunc('day', created_at) as day,
  count(*) as receipts,
  sum((payload->'transaction'->>'total')::numeric) as total
from ops.ocr_events
where doc_type = 'receipt'
  and payload->>'ok' = 'true'
group by day
order by day desc;
```

## Files

- **Workflow JSON**: `automations/n8n/workflows/claude-ai-mcp/11_telegram_ocr_gemini_complete.json`
- **Migration**: `supabase/migrations/20260221000000_ocr_events.sql`
- **This Guide**: `automations/n8n/workflows/claude-ai-mcp/TELEGRAM_OCR_IMPLEMENTATION.md`

## Support

For issues or questions:
1. Check n8n execution logs
2. Query `ops.ocr_events` for raw data
3. Test Gemini API directly via curl
4. Verify all environment variables are set
