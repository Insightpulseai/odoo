-- Add request_id for correlation + idempotent logging

alter table ops.platform_events
  add column if not exists request_id text;

-- Idempotency: only one event per request_id+action
create unique index if not exists platform_events_request_action_uidx
  on ops.platform_events (request_id, action)
  where request_id is not null;
