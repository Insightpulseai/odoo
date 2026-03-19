-- supabase/migrations/20260225000002_email_deliveries.sql
--
-- Provider-level delivery attempt log.
-- One row per send attempt (success or failure) linked to a notification event.

create table if not exists ops.email_deliveries (
  id              bigserial   primary key,
  notification_id bigint      not null
    references ops.email_notification_events(id) on delete cascade,
  provider        text        not null default 'zoho',
  attempt_number  smallint    not null,
  status          text        not null, -- sent | failed
  provider_ref    text,                 -- message-id returned by provider
  error           text,
  attempted_at    timestamptz not null default now()
);

create index if not exists email_deliveries_notification_id_idx
  on ops.email_deliveries (notification_id);

comment on table ops.email_deliveries is
  'Per-attempt delivery log for ops.email_notification_events. '
  'Written by email-dispatcher Edge Function.';
