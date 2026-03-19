-- ops.ocr_events + ops.log_ocr_event RPC
-- Purpose: Durable logging for Telegram OCR events (success + parse failures)
-- Idempotent: safe to re-run

create schema if not exists ops;

create extension if not exists pgcrypto;

-- Main logging table
create table if not exists ops.ocr_events (
  id uuid primary key default gen_random_uuid(),
  source text not null,
  chat_id text null,
  file_id text null,
  doc_type text not null default 'other',
  payload jsonb not null,
  created_at timestamptz not null default now()
);

-- Performance indexes
create index if not exists ocr_events_created_at_idx on ops.ocr_events (created_at desc);
create index if not exists ocr_events_source_chat_idx on ops.ocr_events (source, chat_id);
create index if not exists ocr_events_doc_type_idx on ops.ocr_events (doc_type) where doc_type != 'parse_error';

-- Optional: GIN index for JSONB payload queries
create index if not exists ocr_events_payload_idx on ops.ocr_events using gin (payload);

-- RPC: logs event and returns inserted id
create or replace function ops.log_ocr_event(
  source text,
  chat_id text,
  file_id text,
  doc_type text,
  payload jsonb
) returns uuid
language plpgsql
security definer
set search_path = ops, pg_temp
as $$
declare
  v_id uuid;
begin
  insert into ops.ocr_events(source, chat_id, file_id, doc_type, payload)
  values (
    log_ocr_event.source,
    log_ocr_event.chat_id,
    log_ocr_event.file_id,
    coalesce(log_ocr_event.doc_type, 'other'),
    log_ocr_event.payload
  )
  returning id into v_id;

  return v_id;
end;
$$;

-- Security: lock down to explicit grants only
revoke all on function ops.log_ocr_event(text, text, text, text, jsonb) from public;

-- If calling via service role (recommended), no further grants needed.
-- If calling via anon/authenticated, uncomment:
-- grant execute on function ops.log_ocr_event(text, text, text, text, jsonb) to anon, authenticated;

-- RLS: enable but allow service role to bypass
alter table ops.ocr_events enable row level security;

-- Optional: add policies if you need anon/authenticated access
-- Example read policy (adjust as needed):
-- create policy "Allow service role full access" on ops.ocr_events
--   for all using (true);

-- Comment on objects for documentation
comment on table ops.ocr_events is 'Audit log for all OCR operations from Telegram/other sources';
comment on function ops.log_ocr_event is 'Insert OCR event with automatic timestamp and return event ID';
