-- supabase/migrations/20260225000004_email_rls.sql
--
-- RLS for the new email orchestration tables.
-- Mirrors the deny-all pattern from ops.email_events in migration 20260223000004.
-- Service role bypasses RLS automatically — no explicit policy needed for that.

alter table ops.email_notification_events enable row level security;
alter table ops.email_deliveries          enable row level security;

-- No access for anon / authenticated roles
create policy "deny_all_email_notification_events"
  on ops.email_notification_events
  for all
  using (false);

create policy "deny_all_email_deliveries"
  on ops.email_deliveries
  for all
  using (false);
