-- supabase/migrations/20260223000007_metrics_views.sql

create schema if not exists ops;

create or replace view ops.integration_metrics as
select
  i.name,
  i.enabled,
  i.last_seen_at,
  i.last_error_at,
  i.error_count,
  (select count(*) from ops.jobs j where j.integration = i.name and j.status='queued') as queued_jobs,
  (select count(*) from ops.jobs j where j.integration = i.name and j.status='dead') as dead_jobs,
  (select count(*) from ops.webhook_events w where w.integration = i.name and w.status='failed') as failed_webhooks,
  now() as observed_at
from ops.integrations i;

create or replace view ops.queue_metrics as
select
  status,
  count(*) as job_count,
  min(created_at) as oldest_created_at,
  min(run_after) as next_run_after
from ops.jobs
group by status;
