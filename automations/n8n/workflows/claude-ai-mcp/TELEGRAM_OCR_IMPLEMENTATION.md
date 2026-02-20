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

# Supabase
SUPABASE_URL="https://spdtwktxdalcfigzeqrz.supabase.co"
SUPABASE_SERVICE_ROLE_KEY="eyJhbGc..." # Preferred for logging
# OR
SUPABASE_ANON_KEY="eyJhbGc..." # Fallback (requires RLS policies)

# n8n (for workflow management)
N8N_BASE_URL="https://n8n.insightpulseai.com"
N8N_API_KEY="eyJhbGc..."
```

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

### 2. Import Workflow to n8n

**Option A - UI Import:**
1. Open https://n8n.insightpulseai.com
2. Workflows → Import from File
3. Select `11_telegram_ocr_gemini_complete.json`
4. Verify credentials are attached (Telegram Bot OCR)
5. Activate workflow

**Option B - API Import (if supported):**
```bash
curl -X POST \
  -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  -H "Content-Type: application/json" \
  -d @automations/n8n/workflows/claude-ai-mcp/11_telegram_ocr_gemini_complete.json \
  "https://n8n.insightpulseai.com/api/v1/workflows"
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

**Symptom**: Workflow execution stops at Supabase node

**Debug**:
1. Check n8n execution logs
2. Common issues:
   - `SUPABASE_SERVICE_ROLE_KEY` not set
   - RPC `log_ocr_event` not created
   - RLS blocking anon key access

**Fix**:
```bash
# Verify migration applied
psql "$POSTGRES_URL" -c "\df ops.log_ocr_event"

# Test RPC directly
psql "$POSTGRES_URL" << 'SQL'
select ops.log_ocr_event(
  'telegram',
  '123456',
  'test_file_id',
  'other',
  '{"test": true}'::jsonb
);
SQL
```

### Telegram Credentials Missing

**Symptom**: Red "Select Credential" on Telegram nodes

**Fix**: Manually attach credential in n8n UI:
1. Open each Telegram node
2. Select credential: "Telegram Bot OCR" (or create new with token `8221767220:AAGJdtPu9RRiH12_AoM6XmSdaPoy5pdIPqY`)

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
