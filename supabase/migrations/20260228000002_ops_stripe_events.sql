-- =============================================================================
-- Migration: 20260228000002_ops_stripe_events.sql
-- Purpose:   Persistent event store for Stripe webhook ingestion.
--            Idempotent: duplicate event_id inserts are no-ops (ON CONFLICT DO NOTHING).
--
-- Consumer:  supabase/functions/stripe-webhook/index.ts
-- SSOT:      ssot/runtime/prod_settings.yaml :: payments.stripe.webhook
-- RLS:       service role only (consistent with all ops.* tables)
-- =============================================================================

-- ---------------------------------------------------------------------------
-- 1. Table
-- ---------------------------------------------------------------------------
create table if not exists ops.stripe_events (
  -- Stripe's globally unique event ID (evt_...) — primary idempotency key
  event_id        text        primary key,

  -- Event metadata
  type            text        not null,               -- e.g. customer.subscription.created
  customer_id     text,                               -- cus_...
  subscription_id text,                               -- sub_... (null for checkout/invoice events)
  invoice_id      text,                               -- in_...  (null for subscription events)

  -- Full event payload for audit / replay
  payload         jsonb       not null,

  -- Timing
  stripe_created_at timestamptz,                      -- event.created from Stripe (epoch → ts)
  first_seen_at   timestamptz not null default now(), -- when this function first received it

  -- Delivery metadata
  webhook_id      text,                               -- Stripe webhook endpoint ID (we_...)
  api_version     text                                -- Stripe API version from event
);

comment on table ops.stripe_events is
  'Append-only Stripe webhook event store. Primary key = event_id provides idempotency. '
  'Consumer: supabase/functions/stripe-webhook. '
  'SSOT: ssot/runtime/prod_settings.yaml payments.stripe.webhook.allowed_events.';

-- Indexes for common queries
create index if not exists stripe_events_type_idx
  on ops.stripe_events (type);

create index if not exists stripe_events_customer_idx
  on ops.stripe_events (customer_id)
  where customer_id is not null;

create index if not exists stripe_events_subscription_idx
  on ops.stripe_events (subscription_id)
  where subscription_id is not null;

create index if not exists stripe_events_first_seen_idx
  on ops.stripe_events (first_seen_at desc);

-- ---------------------------------------------------------------------------
-- 2. RLS — service role only (consistent with all ops.* tables)
-- ---------------------------------------------------------------------------
alter table ops.stripe_events enable row level security;

-- No policies → anon and authenticated are blocked by default.
-- Service role bypasses RLS; Edge Function uses service role key.

-- ---------------------------------------------------------------------------
-- 3. Idempotent ingest RPC
--    Returns: JSON { "ok": true, "deduped": boolean, "event_id": text }
--    Called by: supabase/functions/stripe-webhook/index.ts
-- ---------------------------------------------------------------------------
create or replace function ops.ingest_stripe_event(
  p_event_id        text,
  p_type            text,
  p_customer_id     text,
  p_subscription_id text,
  p_invoice_id      text,
  p_payload         jsonb,
  p_stripe_created_at timestamptz,
  p_webhook_id      text,
  p_api_version     text
)
returns jsonb
language plpgsql
security definer
set search_path = ops, public
as $$
declare
  v_inserted boolean;
begin
  -- Idempotent insert: if event_id already exists, do nothing
  insert into ops.stripe_events (
    event_id,
    type,
    customer_id,
    subscription_id,
    invoice_id,
    payload,
    stripe_created_at,
    webhook_id,
    api_version
  ) values (
    p_event_id,
    p_type,
    p_customer_id,
    p_subscription_id,
    p_invoice_id,
    p_payload,
    p_stripe_created_at,
    p_webhook_id,
    p_api_version
  )
  on conflict (event_id) do nothing;

  -- inserted = true if row was new, false if it was a duplicate
  get diagnostics v_inserted = row_count;

  return jsonb_build_object(
    'ok',      true,
    'deduped', not (v_inserted::boolean),
    'event_id', p_event_id
  );
end;
$$;

comment on function ops.ingest_stripe_event is
  'Idempotent Stripe event ingest. ON CONFLICT (event_id) DO NOTHING. '
  'Returns {ok, deduped, event_id}. Security definer — service role only via Edge Function.';

-- Grant execute to service_role only
revoke execute on function ops.ingest_stripe_event from public, anon, authenticated;
grant  execute on function ops.ingest_stripe_event to service_role;

-- ---------------------------------------------------------------------------
-- 4. Idempotency CI test
--    Run after migration to verify ON CONFLICT behaviour.
--    Expected: second call returns deduped=true, table has exactly one row.
-- ---------------------------------------------------------------------------
do $$
declare
  r1 jsonb;
  r2 jsonb;
begin
  -- First insert
  r1 := ops.ingest_stripe_event(
    'evt_TEST_idempotency_check',
    'invoice.paid',
    'cus_TEST',
    null,
    'in_TEST',
    '{"id":"evt_TEST_idempotency_check","type":"invoice.paid"}'::jsonb,
    now(),
    'we_TEST',
    '2024-06-20'
  );
  assert (r1->>'deduped')::boolean = false,
    'First insert should not be deduped';

  -- Second insert — same event_id
  r2 := ops.ingest_stripe_event(
    'evt_TEST_idempotency_check',
    'invoice.paid',
    'cus_TEST',
    null,
    'in_TEST',
    '{"id":"evt_TEST_idempotency_check","type":"invoice.paid"}'::jsonb,
    now(),
    'we_TEST',
    '2024-06-20'
  );
  assert (r2->>'deduped')::boolean = true,
    'Second insert with same event_id should be deduped';

  -- Cleanup test row
  delete from ops.stripe_events where event_id = 'evt_TEST_idempotency_check';

  raise notice 'ops.stripe_events idempotency check PASSED';
end;
$$;
