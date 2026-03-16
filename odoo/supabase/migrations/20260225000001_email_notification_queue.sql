-- supabase/migrations/20260225000001_email_notification_queue.sql
--
-- Email notification queue for Odoo task events.
-- Separate from ops.email_events (inbound Mailgun tracking, 6-col table).
-- This table is the OUTBOUND notification queue / audit trail.
--
-- Populated by: ops.enqueue_email_notifications() trigger on ops.webhook_events
-- Consumed by:  supabase/functions/email-dispatcher (claim → dispatch → mark)
-- Delivery via: supabase/functions/zoho-mail-bridge?action=send_email

create schema if not exists ops;

create table if not exists ops.email_notification_events (
  id              bigserial   primary key,
  idempotency_key text        not null,
  source          text        not null default 'odoo_webhook',
  event_type      text        not null, -- 'task_assigned' | 'task_stage_changed'
  payload         jsonb       not null default '{}',
  recipient_email text        not null,
  template        text        not null,
  status          text        not null default 'pending',
    -- pending | claimed | sent | failed | dead
  attempts        smallint    not null default 0,
  next_attempt_at timestamptz not null default now(),
  claimed_at      timestamptz,
  completed_at    timestamptz,
  error           text,
  created_at      timestamptz not null default now(),
  constraint email_notification_events_idempotency_key_unique
    unique (idempotency_key)
);

create index if not exists email_notification_events_status_next_idx
  on ops.email_notification_events (status, next_attempt_at)
  where status in ('pending', 'failed');

comment on table ops.email_notification_events is
  'Outbound notification queue. Populated by enqueue_email_notifications() trigger. '
  'Consumed by email-dispatcher Edge Function.';

-- ── Claim RPC ────────────────────────────────────────────────────────────────
-- Atomic batch claim — mirrors ops.claim_jobs() pattern exactly.
-- Uses FOR UPDATE SKIP LOCKED to avoid contention under concurrent workers.

create or replace function ops.claim_email_notifications(p_batch int default 10)
returns setof ops.email_notification_events
language sql
as $$
  update ops.email_notification_events
  set    status     = 'claimed',
         claimed_at = now()
  where  id in (
    select id
    from   ops.email_notification_events
    where  status in ('pending', 'failed')
      and  next_attempt_at <= now()
    order  by next_attempt_at
    limit  p_batch
    for update skip locked
  )
  returning *;
$$;

comment on function ops.claim_email_notifications(int) is
  'Atomically claims up to p_batch pending/retryable notifications. '
  'Safe for concurrent edge function workers via SKIP LOCKED.';
